from fastapi.testclient import TestClient
import pytest
from tests.test_main import app 
import json
import pandas as pd

client = TestClient(app)

# Test for processing files on the first page
def test_first_page_process_file():
    sample_data = {
        "PhoneNo": ["1234567890", "0987654321"],
        "UserKeyPress": ["FlowNo_2=1", "FlowNo_2=2"]
    }
    df = pd.DataFrame(sample_data)
    df_json = df.to_json(orient='records')  # DataFrame to JSON string

    response = client.post("/first_page/process_file", json={"df_json": df_json})
    assert response.status_code == 200
    assert "total_calls" in response.json()
    assert response.json()["total_calls"] == 2


# Test for parsing questions and answers from JSON on the second page
def test_second_page_parse_qna():
    sample_qna = {
        "questions": {
            "Q1": {
                "question": "What is your favorite fruit?",
                "answers": {
                    "FlowNo_2=1": "Apple",
                    "FlowNo_2=2": "Banana"
                }
            }
        }
    }
    response = client.post("/second_page/parse_qna", json=sample_qna)
    assert response.status_code == 200
    assert "Q1" in response.json()
    assert response.json()["Q1"]["answers"]["FlowNo_2=1"] == "Apple"


# Test for parsing structured text into JSON on the second page
def test_second_page_parse_text_to_json():
    text_content = (
        "1. What is your favorite fruit?\n"
        "   - Apple\n"
        "   - Banana\n\n"
        "2. What is your favorite color?\n"
        "   - Blue\n"
        "   - Red\n"
    )
    response = client.post("/second_page/parse_text_to_json", json={"text_content": text_content})
    assert response.status_code == 200
    assert "Q1" in response.json()


# Test for renaming columns in a DataFrame on the second page
def test_second_page_rename_columns():
    df_json = {
        "columns": ["PhoneNo", "UserKeyPress"],
        "data": [
            ["1234567890", "FlowNo_2=1"],
            ["0987654321", "FlowNo_2=2"]
        ],
        "new_column_names": ["PhoneNumber", "UserAction"]
    }
    response = client.post("/second_page/rename_columns", json=df_json)
    assert response.status_code == 200
    assert "PhoneNumber" in response.json()[0] and "UserAction" in response.json()[0], "New column names are not in the response"


# Test for sorting based on custom sort keys on the third page
def test_third_page_custom_sort():
    response = client.get("/third_page/custom_sort", params={"col": "FlowNo_2=3"})
    assert response.status_code == 200
    assert response.json() == {"question_num": 2, "flow_no": 3}

# Test for income classification on the third page
def test_third_page_classify_income():
    response = client.get("/third_page/classify_income", params={"income": "RM4,850 & below"})
    assert response.status_code == 200
    assert response.json() == {"income_group": "B40"}

# Test for parsing text to JSON specifically on the third page
def test_third_page_parse_text_to_json():
    text_content = "1. What is your favorite sport?\n   - Soccer\n   - Basketball\n2. What is your favorite food?\n   - Pizza\n   - Sushi"
    response = client.post("/third_page/parse_text_to_json_third_page", json={"text_content": text_content})
    assert response.status_code == 200
    assert "Q1" in response.json()



# Test for processing file content based on content type on the third page
def test_third_page_process_file_content():
    # Assuming file_path is correctly handled in your application via mocking or test setup
    response = client.get("/third_page/process_file_content?file_path=mock_path&content_type=application/json")
    assert response.status_code == 200

# Test for flattening JSON structure on the third page
def test_third_page_flatten_json_structure():
    data = {
        'flow_no_mappings': {
            'Q1': {
                'question': 'What is your favorite color?',
                'answers': {
                    'FlowNo_2=1': 'Red',
                    'FlowNo_2=2': 'Blue'
                }
            }
        }
    }
    response = client.post("/third_page/flatten_json_structure", json=data)
    assert response.status_code == 200
    assert "FlowNo_2=1" in response.json()
    assert response.json()["FlowNo_2=1"] == "Red"



if __name__ == "__main__":
    pytest.main(["-v"])
