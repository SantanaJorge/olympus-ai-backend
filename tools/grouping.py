from typing import List, Dict, Any
import pandas as pd

def recursive_grouping(df: pd.DataFrame, cols: List[str]) -> List[Dict[str, Any]] | Dict[str, Any]:
    """
    Recursively groups a DataFrame by the specified columns.
    Returns a nested dictionary structure where keys are group values and values are the next level of grouping
    or a list of records for the leaf nodes.
    """
    if not cols:
        if len(df.columns) == 1:
            return {df.columns[0]: df[df.columns[0]].tolist()}
        return df.to_dict(orient="records")
    
    # Filter out columns that don't exist in the dataframe
    valid_cols = [c for c in cols if c in df.columns]
    
    if not valid_cols:
        if len(df.columns) == 1:
            return {df.columns[0]: df[df.columns[0]].tolist()}
        return df.to_dict(orient="records")
        
    col = valid_cols[0]
    rest = valid_cols[1:]
    grouped = {}
    
    # Iterate over groups
    for key, val in df.groupby(col):
        # Recursively group the remaining columns
        # We drop the current grouping column to avoid repetition in nested structures
        grouped[str(key)] = recursive_grouping(val.drop(columns=[col]), rest)
        
    return grouped
