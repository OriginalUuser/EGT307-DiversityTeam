# ███╗   ███╗ █████╗ ██╗███╗   ██╗
# ████╗ ████║██╔══██╗██║████╗  ██║
# ██╔████╔██║███████║██║██╔██╗ ██║
# ██║╚██╔╝██║██╔══██║██║██║╚██╗██║
# ██║ ╚═╝ ██║██║  ██║██║██║ ╚████║
# ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝

# DESCRIPTION |
# Application code for the model training pipeline.

# Linted and formatted with Ruff

import utils
import nodes

import os

import logging

logger = logging.getLogger(__name__)


def run_training_pipeline():
    # Get configuration file paths
    db_config_path = os.getenv("DB_CONFIG_PATH")
    global_config_path = os.getenv("GLOBAL_CONFIG_PATH")
    model_config_path = os.getenv("MODEL_CONFIG_PATH")

    # Parse YAML configurations into python dictionaries
    db_config = utils._parse_yaml(db_config_path)
    global_config = utils._parse_yaml(global_config_path)
    model_config = utils._parse_yaml(model_config_path)

    # Parse .db file to pandas DataFrame
    df = utils._parse_to_pd(db_config)

    X_train, X_test, y_train, y_test = nodes.split_dataset(df, global_config)

    best_model, best_params = nodes.train_model(
        X_train, y_train, model_config, global_config
    )

    # Add Evaluation Node! >.<

    utils._write_to_disk(
        best_model,
        best_params,
    )


if __name__ == "__main__":
    run_training_pipeline()
