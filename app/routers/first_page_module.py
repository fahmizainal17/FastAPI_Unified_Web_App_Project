import pandas as pd
from fastapi import APIRouter, HTTPException
from io import StringIO
from pydantic import BaseModel

class FileProcessRequest(BaseModel):
    df_json: str  # This will validate that the incoming JSON contains this key and this expects a JSON string that can be loaded into a DataFrame

router = APIRouter( prefix="/first_page", tags=["Data_Cleaner_Pre_Processor"])

def merger(df_list, phonenum_list):
    """
    Concatenates lists of DataFrames and renames a column.

    Parameters:
    - df_list (list of pd.DataFrame): List of DataFrames to be concatenated vertically.
    - phonenum_list (list of pd.DataFrame): List of phone number DataFrames to be concatenated vertically.

    Returns:
    - df_merge (pd.DataFrame): Concatenated DataFrame of df_list.
    - phonenum_combined (pd.DataFrame): Concatenated DataFrame of phonenum_list with 'PhoneNo' column renamed to 'phonenum'.
    """
    # Check if the lists are not empty before concatenating
    if df_list:
        df_merge = pd.concat(df_list, axis='index')
    else:
        df_merge = pd.DataFrame()  # Return an empty DataFrame if list is empty

    if phonenum_list:
        phonenum_combined = pd.concat(phonenum_list, axis='rows')
        phonenum_combined.rename(columns={'PhoneNo': 'phonenum'}, inplace=True)
    else:
        phonenum_combined = pd.DataFrame()  # Return an empty DataFrame if list is empty

    return df_merge, phonenum_combined

@router.post("/process_file")
def process_file(request: FileProcessRequest):
    try:
        # Parse the DataFrame from the JSON string
        df = pd.read_json(StringIO(request.df_json), orient='records')
        df.dropna(axis='columns', how='all', inplace=True)
        df_phonenum = df[['PhoneNo']]
        df_response = df.loc[:, 'UserKeyPress':]
        df_results = pd.concat([df_phonenum, df_response], axis='columns')
        df_results.drop_duplicates(subset=['PhoneNo'], inplace=True)
        total_calls_made = len(df_results)
        
        phonenum_recycle = df_results.dropna(subset=['UserKeyPress'])
        phonenum_list = phonenum_recycle[['PhoneNo']]
        
        df_complete = df_results.dropna(axis='index')
        total_of_pickups = len(df_complete)
        df_complete['Set'] = 'IVR'
        
        df_merge, phonenum_combined = merger([df_complete], [phonenum_list])
        
        return {
            "message": "Processed successfully",
            "df_complete": df_complete.to_dict(orient='records'),  # Convert DataFrame to dictionary for response
            "phonenum_list": phonenum_list.to_dict(orient='records'),
            "total_calls": total_calls_made,
            "total_pickup": total_of_pickups,
            "df_merge": df_merge.to_dict(orient='records')
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))