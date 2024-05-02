from fastapi.testclient import TestClient
from tests.test_main import app

client = TestClient(app)

# ---------------------------------------------------
# Welcome Page Test (1)
# ---------------------------------------------------

def test_welcome_page():
    response = client.get("/welcome_page")
    assert response.status_code == 200
    assert "Welcome to FastAPI Survey Web Application" in response.text

# ---------------------------------------------------
# Tests for the First Page Module (1 Endpoints)
# ---------------------------------------------------

def test_first_page_process_file():
    sample_json = {
        "df_json": '[{"PhoneNo": "1234567890", "UserKeyPress": "FlowNo_2=1"}]'
    }
    response = client.post("/first_page/process_file", json=sample_json)
    assert response.status_code == 200
    assert "Processed successfully" in response.json()["message"]

# ---------------------------------------------------
# Tests for the Second Page Module (3 Endpoints)
# ---------------------------------------------------

def test_second_page_parse_qna():
    sample_data = {
        "Q1": {
            "question": "What is your favorite sport?",
            "answers": {
                "FlowNo_2=1": "Soccer",
                "FlowNo_2=2": "Basketball"
            }
        }
    }
    response = client.post("/second_page/parse_qna", json=sample_data)
    assert response.status_code == 200
    assert "Q1" in response.json()

def test_second_page_parse_text_to_json():
    content = (
        "1. What is your favorite sport?\n"
        "   - Soccer\n"
        "   - Basketball\n\n"
        "2. What is your favorite team?\n"
        "   - Team A\n"
        "   - Team B\n"
    )
    files = {'upload_file': ('test.txt', content, 'text/plain')}
    response = client.post("/second_page/parse_texttojson", files=files)
    assert response.status_code == 200
    assert "Q1" in response.json()
    assert "Q2" in response.json()

def test_rename_columns():
    sample_dataframe = '{"PhoneNo": ["1234567890", "0987654321"], "UserKeyPress": ["FlowNo_2=1", "FlowNo_2=2"]}'
    new_column_names = ["PhoneNumber", "UserAction"]
    response = client.post("/second_page/rename_columns", json={"df": sample_dataframe, "new_column_names": new_column_names})
    assert response.status_code == 200
    assert "PhoneNumber" in response.json()['df'].columns
    assert "UserAction" in response.json()['df'].columns

# ---------------------------------------------------
# Tests for the Third Page Module (4 Endpoints)
# ---------------------------------------------------

def test_third_page_custom_sort():
    response = client.get("/third_page/custom_sort?col=FlowNo_2=3")
    assert response.status_code == 200
    assert response.json()["question_num"] == 2
    assert response.json()["flow_no"] == 3

def test_third_page_classify_income():
    response = client.get("/third_page/classify_income?income=RM4,850 & below")
    assert response.status_code == 200
    assert response.json()["income_group"] == "B40"

def test_flatten_json_structure():
    sample_data = {
        "Q1": {
            "question": "What is your favorite color?",
            "answers": {
                "FlowNo_2=1": "Red",
                "FlowNo_2=2": "Blue"
            }
        }
    }
    response = client.get("/third_page/flatten_json_structure", json={"flow_no_mappings": sample_data})
    assert response.status_code == 200
    assert "FlowNo_2=1" in response.json()
    assert response.json()["FlowNo_2=1"] == "Red"

# Optionally, run these tests using pytest from the command line
if __name__ == "__main__":
    import pytest
    pytest.main()
