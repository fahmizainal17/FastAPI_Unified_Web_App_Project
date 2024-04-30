import pandas as pd
import numpy as np
from fastapi import APIRouter
from typing import Any 
from io import StringIO

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
def process_file(df_json: str):
    df = pd.read_json(StringIO(df_json), orient='records')
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
    
    # Ensuring that the length check is removed or correctly applied
    df_merge, phonenum_combined = merger([df_complete], [phonenum_list])

    return {
        "message": "Processed successfully",
        "df_complete": df_complete,  # Return as DataFrame
        "phonenum_list": phonenum_list,  # Return as DataFrame
        "total_calls": total_calls_made,
        "total_pickup": total_of_pickups,
        "df_merge": df_merge  # Return as DataFrame
    }

















# This is to put the sample output for testing
# if __name__ == "__main__":
#     from json import dumps
#     test_data = pd.read_csv(r"C:\Users\User\Desktop\Invoke Project\FastAPI_Unified_App\FastAPI_Unified_Web_App_Project\tests\app\Batu_Pahat_IVR_Raw_Results_8April_2024\Broadcast_List_Report_for_BARU PAHAT MAC 24 PT4.csv")
#     with open(r"C:\Users\User\Desktop\Invoke Project\FastAPI_Unified_App\FastAPI_Unified_Web_App_Project\tests\app\Batu_Pahat_IVR_Raw_Results_8April_2024\sample_output.json","w") as file:
#         file.write(dumps(process_file(test_data),indent=4)) #dumps convert dict to json and loads convert json to dict