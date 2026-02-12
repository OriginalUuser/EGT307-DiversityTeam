"""
- Ingests data payload from fast api 
- Ensure format of the data matches database (data type/schema matches, no missing columns, "add additional columns")
- Send data "payload" to the database
"""

import pandas as pd
from typing import Any

expectedSchema = {
    "created_at":           pd.Timestamp,
    "entry_id":             int,
    "temperature":          float,
    "turbidity":            float,
    "dissolved_oxygen":     float,
    "ph":                   float,
    "ammonia":              float,
    "nitrate":              int,
    "population":           int,
    "fish_length":          float,
    "fish_weight":          float,
}

imputationValues = {
    "created_at":           pd.Timestamp('2026-1-1'),
    "entry_id":             0,
    "temperature":          27.0,
    "turbidity":            100,
    "dissolved_oxygen":     25.0,
    "ph":                   6.0,
    "ammonia":              6,
    "nitrate":              900,
    "population":           50,
    "fish_length":          7.11,
    "fish_weight":          2.91,
}

expectedColumns = set(expectedSchema.keys())

tableNames = {'iot_pond_1', 'iot_pond_2', 'iot_pond_3', 'iot_pond_4', 'iot_pond_6', 'iot_pond_7', 'iot_pond_8', 'iot_pond_9', 'iot_pond_10', 'iot_pond_11', 'iot_pond_12'}

def tableExists(table_name: str) -> bool:
    """
    Check if table exists in database
    """
    return {table_name} < tableNames


def checkColumnsPresent(payload: dict) -> tuple[bool, set[str]]:

    """
    - Are all the expected columns present?
        - Yes:  (True, set())
        - No:   (False, {missingCol1, missingCol2, ...})
    """

    dataColumns = set(payload.keys())
    missingColumns = expectedColumns - dataColumns

    return expectedColumns <= dataColumns, missingColumns

def checkColumnsAdditional(payload: dict) -> tuple[bool, set[str]]:

    """
    - Are there any additional columns?
        - Yes:  (True, {additionalCol1, additionalCol2, ...})
        - No:   (False, set())
    """

    dataColumns = set(payload.keys())
    additionalColumns = dataColumns - expectedColumns

    return expectedColumns < dataColumns, additionalColumns

def checkDataType(data: Any, expectedType: type) -> tuple[bool, Any, Any]:

    """
    - Are they in the proper format?
        - Yes:  (True, None, None)
        - No:   (False, correctedData, correctType)
    """
    
    # Check Null value
    if data == None:
        return False, None, None

    # Check if data is from additional column
    if expectedType == None:
        return False, None, type(data)

    # Check if data is time based
    if expectedType == pd.Timestamp:
        if type(data) == expectedType:
            return True, None, None
    
        else:

            # Attempt type casting
            try:
                correctedData = pd.Timestamp(data)
                correctedData = pd.to_datetime(correctedData, format='%Y-%m-%d %H:%M:%S %Z', errors='coerce')

                # If error, treat as bad data
                if pd.isnull(correctedData):
                    correctedData = None
                else:
                    correctedData = str(correctedData.tz_localize('CET'))

            # If error, treat as bad data
            except ValueError:
                correctedData = None
        return False, correctedData, None

            

    # Check if actual type matches expected type
    if type(data) == expectedType:
        return True, None, None
    
    else:

        # Attempt type casting
        try:
            correctedData = expectedType(data)

        # If error, treat as bad data
        except ValueError:
            correctedData = None

    return False, correctedData, None

def checkPayloadSchema(payload: dict) -> tuple[dict[str:Any], set[str], dict[str:Any], bool]:

    """
    Payload Content Checking Process:
    - Are all the expected columns present?
        - If <=20% missing, impute with previous value (reasonable value for initial)
        - If >20% missing, discard payload
    - Are there any additional columns?
        - If Yes, create new column in database and update expected schema
    - Are they in the proper format?
        - Typecast all to appropriate type
        - If unable, impute with previous value (reasonable value for initial)
    """

    # Initial declaration of payload variable to format later
    formattedPayload = payload

    # Check Columns Present
    columnsAllPresent, missingColumns = checkColumnsPresent(payload)

    # Check Additional Columns
    columnsAdditional, additionalColumns = checkColumnsAdditional(payload)

    # Check Column Data Type and Fix (if necessary)
    missingData = set()
    columnsActual = payload.keys()
    for col in columnsActual:

        # Check Data Type
        data = payload[col]
        expectedType = expectedSchema[col] if {col} < set(expectedSchema.keys()) else None
        properFormat, correctedData, correctType = checkDataType(data, expectedType)

        # Fix (if necessary)
        if not properFormat and (correctedData != None or correctType == None):
            formattedPayload[col] = correctedData
        
        # Log as Missing
        if not properFormat and correctedData == None and correctType == None:
            missingData.add(col)

        # Update Expected Schema
        if not properFormat and correctedData == None and correctType != None:
            expectedSchema.update({col: correctType})
            imputationValues.update({col: data})
    
    # Check if Payload is Clear to Send (based on number of missing columns & data)
    clearToSend = len(missingColumns) + len(missingData) <= 0.2 * len(expectedColumns)

    # Impute Missing Values and Columns (if not discarding payload)
    if clearToSend:
        if not columnsAllPresent:
            for col in missingColumns:
                formattedPayload.update({col:imputationValues[col]})
        if missingData != None:
            for col in missingData:
                formattedPayload[col] = imputationValues[col]
    
    
    # Update Imputation Values
    # valuesToChange = set(columnsActual) - missingData
    # for col in valuesToChange:
    #     if {col} < set(imputationValues.keys()):
    #         imputationValues[col] += 0.05 * (formattedPayload[col] - imputationValues[col])
        
    return formattedPayload, additionalColumns, expectedSchema, clearToSend

# Test code for checkPayloadSchema()
# checkPayloadSchema(
    # {
    # "created_at":           pd.Timestamp('2026-1-1'),
    # "entry_id":             0,
    # "temperature":          27.0,
    # "turbidity":            100,
    # "dissolved_oxygen":     25.0,
    # "ph":                   6.0,
    # "ammonia":              6,
    # "nitrate":              900,
    # "population":           50,
    # "fish_length":          7.11,
    # "fish_weight":          2.91
    # }
# )
