# ███╗   ██╗ ██████╗ ██████╗ ███████╗███████╗
# ████╗  ██║██╔═══██╗██╔══██╗██╔════╝██╔════╝
# ██╔██╗ ██║██║   ██║██║  ██║█████╗  ███████╗
# ██║╚██╗██║██║   ██║██║  ██║██╔══╝  ╚════██║
# ██║ ╚████║╚██████╔╝██████╔╝███████╗███████║
# ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚══════╝╚══════╝

# DESCRIPTION |
# This file contains all the functions needed to build the training pipeline.

# Linted and formatted with Ruff

import utils

from typing import Dict, Tuple

import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from skopt import BayesSearchCV

import logging
import sklearn

logger = logging.getLogger(__name__)
sklearn.set_config(transform_output="pandas")


def split_dataset(df: pd.DataFrame, options: Dict) -> Tuple:
    """
    Splits the dataframe and applies stratification.

    Parameters
    ----------
    df: pd.DataFrame
        Dataset to be split

    options: Dict
        Configuration that specifies train test split ratio and random state;
        Defined in configurations/global_configurations.yml under key 'global_configurations'

    Returns
    -------
    Tuple
        Returns train test split
    """

    target_column = options["target_column"]
    X = df.drop(target_column, axis=1)
    y = df[target_column]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=options["dataset_split_ratio"],
        random_state=options["random_state"],
        stratify=y,
    )

    return X_train, X_test, y_train, y_test


def train_model(
    X_train: pd.DataFrame, y_train: pd.DataFrame, model_config: Dict, options: Dict
) -> Tuple[BaseEstimator, Dict]:
    """
    Trains a model using Bayesian Optimization for hyperparameter tuning

    Parameters
    ----------
    X_train: pd.DataFrame
        Features of the training dataset

    y_train: pd.DataFrame
        Targets of the training dataset

    model_config: Dict
        Defined in configurations/model_configurations/*.yml under key '<model_header>'

    options: Dict
        Defined in configurations/global_configurations.yml under key 'global_configurations'

    Returns
    -------
    Tuple[BaseEstimator, Dict]
        Returns a tuple containing the best fitted model and its corresponsing hyperparameters.
    """

    # Initialize model object
    model = utils._init_model(X_train, model_config, options)

    # Create dataset preprocessor object
    preprocessor = utils._build_preprocessor(X_train, model_config)

    # Pipes ColumnTransformer object to Pipeline object
    # When dataset is passed into the Pipeline object, the necessary dataset
    # preprocessing steps are applied before being fit to the model
    # Docs: https://scikit-learn.org/stable/auto_examples/compose/plot_column_transformer_mixed_types.html
    if preprocessor:
        model_to_tune = Pipeline(
            steps=[("preprocessor", preprocessor), ("model", model)]
        )
        prefix = (
            "model__"  # Pipeline object requires to add prefix in front of parameters
        )

    else:
        model_to_tune = model
        prefix = ""

    search_space = model_config.get("search_space", {})
    search_space = {f"{prefix}{k}": v for k, v in search_space.items()}
    param_grid = utils._parse_search_space(search_space)

    # Use StratifiedKFold over KFold due to imbalanced datset
    cv_strategy = StratifiedKFold(
        n_splits=options["no_cv_splits"],
        shuffle=True,
        random_state=options["random_state"],
    )

    # Hyperparameter optimization with Bayesian Optimisation
    bs = BayesSearchCV(
        estimator=model_to_tune,
        search_spaces=param_grid,
        cv=cv_strategy,
        scoring=options["bayes_scoring"],
        n_jobs=-1,
        verbose=0,
        n_iter=options["bayes_search_n_iters"],
        random_state=options["random_state"],
    )

    bs.fit(X_train, y_train)

    return bs.best_estimator_, bs.best_params_
