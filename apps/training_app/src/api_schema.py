from pydantic import BaseModel, Field
from typing import List, Optional


class TrainingConfig(BaseModel):
    # Data processing parameters
    tables: Optional[List[str]] = Field(
        None, description="List of tables to retrain. If null, all tables are used."
    )
    columns: Optional[List[str]] = Field(
        None, description="Specific features to retrain. If null, all features used."
    )
    rows_limit: Optional[int] = Field(
        5000, description="Number of rows to use for training."
    )

    # LSTM Hyperparameters
    window_size: int = Field(
        10, description="Number of past time steps to look back (sliding window)."
    )
    lstm_units: int = Field(50, description="Number of neurons in the LSTM layers.")
    epochs: int = Field(10, description="Number of training iterations.")
    optimizer: str = Field("adam", description="Optimizer.")
    loss_function: str = Field("mean_squared_error", description="Optimizer.")
    batch_size: int = Field(32, description="Number of samples per gradient update.")
    num_layers: int = Field(2, ge=1, description="Number of stacked LSTM layers.")
