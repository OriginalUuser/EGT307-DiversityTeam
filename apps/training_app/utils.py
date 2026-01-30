# ██╗   ██╗████████╗██╗██╗     ███████╗
# ██║   ██║╚══██╔══╝██║██║     ██╔════╝
# ██║   ██║   ██║   ██║██║     ███████╗
# ██║   ██║   ██║   ██║██║     ╚════██║
# ╚██████╔╝   ██║   ██║███████╗███████║
#  ╚═════╝    ╚═╝   ╚═╝╚══════╝╚══════╝

# DESCRIPTION | 
# This file stores all utility tools used by the model training pipleine.

import importlib
from typing import Any, Dict, Tuple, Type
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def _parse_search_space(search_space: dict) -> Dict[str, Any]:
    """
    Parses a dictionary into skopt.space objects.
    Converting to skopt.space objects is necessary before passing into BayesSearchCV as 'search_spaces' parameters.

    If unsure of what 'search_spaces' is, refer to 'specifying_model_config.md' documentation!!

    Parameters
    ----------
    search_space: dict
        Dictionary specifing search_space range of parameters; Defined in conf/base/parameters_model_config/*.yml under header 'search_space'

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

        _parse_search_space(space)
        {'x': Integer(1, 10), 'y': Categorical(['a', 'b'])}
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
    Moves uses cuda if specified in model's configuration.

    If unsure of what 'search_spaces' and 'options' should be, refer to 'specifying_model_config.md' documentation!!

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
    You can also refuse to apply any encoding to the dataset.

    Parameters
    ----------
    X_train: pd.DataFrame
        Training data; Used to determine categorical and numerical columns in the dataset

    model_config:
        Model base hyperparameter configuration.
        Used to check datset how dataset should be encoded, as well as if the dataset requires scaling.

        If encoding is not specified as a parameter, One-Hot encoding will be applied by default.;

        Defined in conf/base/parameters_model_config/*.yml under key 'model_params'

    Returns
    -------
    ColumnTransformer
        Defines how dataset should be transformed: (OHE/Label/None) w/o Scaling
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
