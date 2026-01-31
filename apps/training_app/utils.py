# ██╗   ██╗████████╗██╗██╗     ███████╗
# ██║   ██║╚══██╔══╝██║██║     ██╔════╝
# ██║   ██║   ██║   ██║██║     ███████╗
# ██║   ██║   ██║   ██║██║     ╚════██║
# ╚██████╔╝   ██║   ██║███████╗███████║
#  ╚═════╝    ╚═╝   ╚═╝╚══════╝╚══════╝

# DESCRIPTION |
# This file stores all utility tools used by the model training pipeline.

# Linted and formatted with Ruff

from typing import Any, Dict, Type

import os
import yaml
import importlib
import psycopg2
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.base import BaseEstimator
from skopt.space import Categorical, Integer, Real
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

import logging

logger = logging.getLogger(__name__)

#####################
# General Utilities #
#####################


def _parse_yaml(file_path: str) -> Dict[str, Any]:
    """
    Converts YAML file to python dictionary.

    Parameters
    ----------
    file_path: str
        YAML file path.

    Returns
    -------
    Dict[str, Any]
        Python dictionary of all YAML defined configurations.
    """
    try:
        with open(file_path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.debug(f"Failed to parse configuration file to python Dictionary: {e}")


def _parse_to_pd(con_params: Dict) -> pd.DataFrame:
    """
    Fetches PostgreSQL table and converts it to a pandas DataFrame.

    Parameters
    ----------
    con_params: Dict
        Postgres connection data.

    Returns
    -------
    pd.DataFrame
        Converted table as pandas DataFrame.
    """
    target_table = os.getenv("TARGET_TABLE")
    with psycopg2.connect(**con_params) as con:
        query = f"SELECT * FROM {target_table};"
        df = pd.read_sql(query, con)

        logger.info(f"Converted {target_table} to pandas DataFrame")
        return df

def _write_to_disk(model: BaseEstimator, params: dict):
    """
    Writes data to disk.
    """

    base_path = os.getenv("OUTPUT_PATH")
    table_name = os.getenv("TARGET_TABLE")
    model_name = os.getenv("MODEL_CONFIG_PATH").replace(".yaml", "")

    final_dir = os.path.join(base_path, table_name, model_name)

    os.makedirs(final_dir, exist_ok=True)

    model_path = os.path.join(final_dir, "model.joblib")
    param_path = os.path.join(final_dir, "params.json")

    joblib.dump(model, model_path)
    with open(param_path, 'w') as f:
        json.dump(params, f, indent=4)

    logger.info(f"Saved data to: {final_dir}")


##################
# Node Utilities #
##################


def _parse_search_space(search_space: dict) -> Dict[str, Any]:
    """
    Parses a dictionary into skopt.space objects.
    Converting to skopt.space objects is necessary before passing into BayesSearchCV as 'search_spaces' parameters.

    Parameters
    ----------
    search_space: dict
        Dictionary specifing search_space range of parameters;
        Defined in conf/base/parameters_model_config/*.yml under header 'search_space'

    Returns
    -------
    Dict[str, Any]
        Dictionary with parameters wrapped in skopt.space objects

    Example
    -------
        space = {
            'x': {'type': 'Integer', 'low': 1, 'high': 10},
            'y': {'type': 'Categorical', 'categories': ['a', 'b']}
        }

        _parse_search_space(space):
            Returns -> {'x': Integer(1, 10), 'y': Categorical(['a', 'b'])}
    """
    bayes_search_params = {}
    for identifier, values in search_space.items():
        value_type = values["type"]

        if value_type == "Integer":
            bayes_search_params[identifier] = Integer(values["low"], values["high"])

        # Checks 'Real' type for prior parameter and parses as kwargs
        elif value_type == "Real":
            kwargs = {
                k: v for k, v in values.items() if k not in ["type", "low", "high"]
            }
            bayes_search_params[identifier] = Real(
                values["low"], values["high"], **kwargs
            )

        elif value_type == "Categorical":
            bayes_search_params[identifier] = Categorical(values["categories"])

    return bayes_search_params


def _get_model_class(class_path: str) -> Type[BaseEstimator]:
    """
    Imports and returns a class from a dotted string path.

    Parameters
    ----------
    class_path: str
        Full path in the 'package.module.ClassName' format

    Returns
    -------
    Type[BaseEstimator]
        Python class of the dotted string path

    Example
    -------
    python_class = _get_model_class("sklearn.ensemble.RandomForestClassifier")
    """
    # Split string one dot <.> from the right
    module_path, class_name = class_path.rsplit(".", 1)

    # Import model class library with importlib
    module = importlib.import_module(module_path)

    # Returns model class
    return getattr(module, class_name)


def _init_model(
    X_train: pd.DataFrame, model_config: Dict, options: Dict
) -> Type[BaseEstimator]:
    """
    Initializes a ML model object with model confiuration specified in model's *.yml file.

    Parameters
    ----------
    X_train: pd.DataFrame
        Training data; Used to detect categorial features for catboost classifier

    model_config: Dict
        Model base hyperparameter configuration; Defined in conf/base/parameters_model_config/*.yml under header 'model_params'

    options: Dict
        Execution confiuration; Defined in parameters_execution_configuration.yml under header 'execution_config'

    Returns
    -------
    Type[BaseEstimator]
        Initialise model instance
    """
    model_class = _get_model_class(model_config["class"])

    model_params = model_config.get("model_params", {})

    # CatboostClassifier requires to specify category features in its parameters
    # for proper training
    if model_config["class"] == "catboost.CatBoostClassifier":
        model_params["cat_features"] = X_train.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()
        model_config["data_encoding"] = "none"
        logger.debug("Added categorical cat_features")

    return model_class(random_state=options["random_state"], **model_params)


def _build_preprocessor(X_train: pd.DataFrame, model_config: dict) -> ColumnTransformer:
    """
    Creates dataset transformation object.

    Used for applying One-Hot, Label (Oritental) encoding on the entire dataset.
    No data encoding is done by default unless One-Hot or Label encoding values are explicitly defined in the model configuration files.

    Also used for applying feature scaling to the dataset.
    Feature scaling is not done by default unless explicitly defined in the model configuration files.

    Parameters
    ----------
    X_train: pd.DataFrame
        Training data; Used to determine categorical and numerical columns in the dataset

    model_config:
        Model base hyperparameter configuration.
        Used to check datset how dataset should be encoded, as well as if the dataset requires scaling.
        Defined in conf/base/parameters_model_config/*.yml under key 'model_params'

    Returns
    -------
    ColumnTransformer
        Defines how dataset should be transformed: (OHE/Label/None) & (Feature Scaling/No Feature Scaling)
    """

    # Returns subset of DataFrame cols based on col dtypes
    categorical_cols = X_train.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()
    numerical_cols = X_train.select_dtypes(
        include=["int64", "float64"]
    ).columns.tolist()

    preprocessing_steps = []
    data_encoding = model_config.get(
        "data_encoding", "none"
    ).lower()  # Default encoding is one-hot encoding

    # Applies One-Hot encoding to dataset
    if data_encoding == "ohe":
        logger.debug("Applying One-Hot Encoding")
        encoding_transformer = (
            "ohe",
            OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            categorical_cols,
        )
        preprocessing_steps.append(encoding_transformer)

    # Applies Label/Ordinal encoding to datset
    elif data_encoding == "label":
        logger.debug("Applying Label Encoding")
        encoding_transformer = (
            "label",
            OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1),
            categorical_cols,
        )
        preprocessing_steps.append(encoding_transformer)

    # Applies no encoding to dataset
    elif data_encoding == "none":
        logger.debug("Skipped encoding")
        pass

    # Applies dataset scaling to the data if required
    if model_config.get("requires_scaling", False):
        scaling_transformer = ("scaler", StandardScaler(), numerical_cols)
        preprocessing_steps.append(scaling_transformer)
        logger.debug("Applied Standard Scaling")

    return ColumnTransformer(
        transformers=preprocessing_steps,
        remainder="passthrough",
        n_jobs=-1,
        verbose_feature_names_out=False,
    )
