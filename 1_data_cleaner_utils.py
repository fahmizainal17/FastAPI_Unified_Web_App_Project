import pandas as pd
import numpy as np

async def process_file(uploaded_file):
    """
    Process the uploaded CSV file to extract and transform phone number data
    and user response data for analysis.
    
    The function performs several steps:
    - Reads the CSV, skipping the first row and setting column names dynamically.
    - Drops columns that are entirely NA.
    - Extracts columns for phone numbers and user responses.
    - Identifies total number of calls and total pickups.
    - Filters data to complete responses where a user key press is recorded.
    - Adds a 'Set' column to indicate data belonging to the IVR set.
    - Filters for records where the user key press response is exactly 10 characters long.

    Parameters:
    - uploaded_file: A file-like object representing the uploaded CSV file.
                     This object must support file-like operations such as read.

    Returns:
    - A tuple containing:
        - df_complete: A pandas DataFrame of the processed data, with calls that have complete information.
        - phonenum_list: A pandas DataFrame containing the list of phone numbers that have at least one user key press.
        - total_calls: The total number of calls (rows) in the uploaded file.
        - total_pickup: The total number of calls where a user key press was recorded.

    Note:
    - The function assumes the uploaded CSV has specific columns of interest, notably 'PhoneNo' and 'UserKeyPress'.
    - It is assumed that the second row of the CSV provides the column names for the data.
    """
    df = pd.read_csv(uploaded_file, skiprows=1, names=range(100), engine='python')
    df.dropna(axis='columns', how='all', inplace=True)
    df.columns = df.iloc[0]
    df_phonenum = df[['PhoneNo']]
    df_response = df.loc[:, 'UserKeyPress':]
    df_results = pd.concat([df_phonenum, df_response], axis='columns')
    
    total_calls = len(df_results)
    phonenum_recycle = df_results.dropna(subset=['UserKeyPress'])
    phonenum_list = phonenum_recycle[['PhoneNo']]
    
    df_complete = df_results.dropna(axis='index')
    total_pickup = len(df_complete)

    df_complete.columns = np.arange(len(df_complete.columns))
    df_complete['Set'] = 'IVR'
    df_complete = df_complete.loc[:, :'Set']
    df_complete = df_complete.loc[(df_complete.iloc[:, 2].str.len() == 10)]
    
    return {
        "df_complete": df_complete.to_dict(),
        "phonenum_list": phonenum_list.to_dict(),
        "total_calls": total_calls,
        "total_pickup": total_pickup
    }



