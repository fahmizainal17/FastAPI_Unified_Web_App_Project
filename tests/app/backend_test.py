from fastapi import FastAPI
from fastapi.testclient import TestClient
from .main import app
from routers.first_page_module import merger,process_file
import json
from json import loads #dumps convert dict to json and loads convert json to dict
import pandas as pd
import os

# test connection 
@app.get("/")
def read_main():
    return {"msg": "Hello World"}

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}


def test_process_file():
    # Setup file paths correctly
    base_path = r"C:\Users\User\Desktop\Invoke Project\FastAPI_Unified_App\FastAPI_Unified_Web_App_Project\tests\app\Batu_Pahat_IVR_Raw_Results_8April_2024"
    csv_file_path = os.path.join(base_path, "Broadcast_List_Report_for_BARU PAHAT MAC 24 PT4.csv")
    json_file_path = os.path.join(base_path, "sample_output.json")

    # Read the CSV file, handling data types explicitly if necessary
    dtype_dict = {'Column1': 'str', 'Column2': 'float'}  # Example: adjust column names and types
    test_data = pd.read_csv(csv_file_path, dtype=dtype_dict)

    # Load expected output
    with open(json_file_path, "r") as file:
        test_output = json.load(file)

    # Convert DataFrame to JSON as expected by the API
    test_data_json = test_data.to_json(orient='records')

    # Make a POST request with the properly formatted JSON
    response = client.post("/first_page/process_file", json={"df": test_data_json})
    assert response.status_code == 200
    assert response.json() == test_output

# Run the test
test_process_file()


#####################################################################
# import requests
# from requests_toolbelt.multipart.encoder import MultipartEncoder

# url = "http://127.0.0.1:8000/first_page/process_file"

# filename = r"C:\Users\User\Desktop\Invoke Project\FastAPI_Unified_App\tests\app\Batu_Pahat_IVR_Raw_Results_8April_2024\Broadcast_List_Report_for_BARU PAHAT MAC 24 PT4.csv"

# m = MultipartEncoder(
#         fields={'file': ('filename', open(filename, 'rb'), 'text/csv')}
#     )
# r = requests.post(url, data=m, headers={'Content-Type': m.content_type}, timeout = 8000)
# print(r.status_code)
# assert r.status_code == 200



#####################################################################
# import os
# from fastapi.testclient import TestClient
# from app.main import app # Import your FastAPI application here
# from requests_toolbelt.multipart.encoder import MultipartEncoder

# client = TestClient(app)

# def test_process_file():
#     url = "/first_page/process_file"  # Adjust if your endpoint route is different
#     filename = r"C:\Users\User\Desktop\Invoke Project\FastAPI_Unified_App\tests\Batu_Pahat_IVR_Raw_Results_8April_2024\Broadcast_List_Report_for_BARU PAHAT MAC 24 PT4.csv"  # Provide path to a test CSV file

#     # Use the actual path of the file in your test environment
#     filepath = os.path.join(os.path.dirname(__file__), filename)

#     m = MultipartEncoder(
#         fields={'file': ('filename', open(filepath, 'rb'), 'text/csv')}
#     )

#     response = client.post(
#         url,
#         data=m,
#         headers={'Content-Type': m.content_type}
#     )

#     assert response.status_code == 200
#     ### You can also add more assertions here to check the correctness of the response content

#     ## It's good practice to close the file after opening it
#     m.fields['file'][1].close()
