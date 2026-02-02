from evidently import Report
from evidently.metrics import DriftedColumnsCount, ValueDrift
from evidently.generators import ColumnMetricGenerator
from evidently.core.report import Snapshot

from pandas import DataFrame

from typing import Union

# monitoring.py
# Utilities for running various monitoring processes

def generate_report(
        reference_df: DataFrame, 
        current_df: DataFrame, 
        columns: list[str], 
        num_metrics: str="wasserstein",
        cat_metrics: str="jensenshannon"
    ) -> Union[Snapshot, dict]:
    """
    `generate_report()` creates a datadrift report for the specified columns in the reference and current dataset
    
    :param reference_df: Dataframe containing the data to reference (old data)
    :param current_df: Dataframe containing the current data (new data)
    :param columns: List of columns to include in the report
    :param num_metrics: Metric to use for numerical columns 
    :param cat_metrics: Metric to use for categorical columns 

    :type reference_df: pd.DataFrame
    :type current_df: pd.DataFrame
    :type columns: str
    :type num_metrics: str (wasserstein, psi, ks)
    :type cat_metrics: str (jensenshannon, chisquare)
    """
    drift_report = Report([
        # Overall data drift report on the columns
        DriftedColumnsCount(columns=columns, threshold=0.3, num_method=num_metrics, cat_method=cat_metrics),

        # Data drift report for each column
        ColumnMetricGenerator(ValueDrift, columns=columns, column_types='num', metric_kwargs={"method": num_metrics}),
        ColumnMetricGenerator(ValueDrift, columns=columns, column_types='cat', metric_kwargs={"method": cat_metrics}),
    ], include_tests=True)

    # Run the data drift tests
    drift_snapshot = drift_report.run(current_data=current_df, reference_data=reference_df)
    drift_snapshot_dict = drift_snapshot.dict()

    return drift_snapshot, drift_snapshot_dict

def is_data_drift(report_results: dict) -> bool:
    # In order to see if the model needs retraining, the "Overall Data Drift Report" must FAIL
    # The "Overall Data Drift Report" shows how many of the columns failed the data drift test, measuring overall data drift of the dataset
    
    # Find the test for the overall data drift (The first test)
    test_results = report_results["tests"][0]
    assert test_results["id"] == "lt"

    # Return True if the result is a failure
    if test_results["status"] == "FAIL":
        return True
    else:
        return False
    

def upload_to_ui(snapshot: Snapshot) -> None:
    ...