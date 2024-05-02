import pytest
import pandas as pd
import json
from io import StringIO, BytesIO
from fastapi import UploadFile
from tests.test_main import app
from tests.routers.test_first_page_module import merger, process_file
from tests.routers.test_second_page_module import parse_questions_and_answers, parse_text_to_json, rename_columns
from tests.routers.test_third_page_module import parse_text_to_json_third_page, custom_sort, classify_income, process_file_content, flatten_json_structure

# ---------------------------------------------------
# Connection Test
# ---------------------------------------------------

@app.get("/")
def read_main():
    return {"message": "Welcome to the Unit Testing"}

# ---------------------------------------------------
# First Page Module Tests
# ---------------------------------------------------

@pytest.fixture
def create_data():
    """Fixture for creating DataFrame input for testing."""
    data = [
        {"PhoneNo": "1234567890", "UserKeyPress": "FlowNo_2=1"},
        {"PhoneNo": "0987654321", "UserKeyPress": "FlowNo_2=2"}
    ]
    data_json = json.dumps(data)
    return pd.read_json(StringIO(data_json), orient='records')

def test_merger(create_data: pd.DataFrame):
    df_list = [create_data]
    phonenum_list = [create_data[['PhoneNo']]]
    df_merge, phonenum_combined = merger(df_list, phonenum_list)
    
    assert not df_merge.empty
    assert 'PhoneNo' in df_merge.columns
    assert not phonenum_combined.empty
    assert 'phonenum' in phonenum_combined.columns

def test_process_file(create_data: pd.DataFrame):
    df_json = create_data.to_json(orient='records')
    result = process_file(df_json)
    
    assert 'df_complete' in result
    assert len(result['df_complete']) == 2  # Expecting 2 entries after processing
    assert result['total_calls'] == 2
    assert result['total_pickup'] == 2
    assert 'df_merge' in result
    assert not result['df_merge'].empty  # Should not be empty

# ---------------------------------------------------
# Second Page Module Tests
# ---------------------------------------------------

@pytest.fixture
def json_data_input():
    data = {
        "Q1": {
            "question": "What is your favorite food?",
            "answers": {
                "FlowNo_2=1": "Pizza",
                "FlowNo_2=2": "Burger"
            }
        },
        "Q2": {
            "question": "What is your favorite drink?",
            "answers": {
                "FlowNo_3=1": "Coffee",
                "FlowNo_3=2": "Tea"
            }
        }
    }
    return UploadFile(file=BytesIO(json.dumps(data).encode('utf-8')), filename="test.json")

@pytest.fixture
def text_content_input():
    content = (
        "1. What is your favorite food?\n"
        "   - Pizza\n"
        "   - Burger\n\n"
        "2. What is your favorite drink?\n"
        "   - Coffee\n"
        "   - Tea\n"
    )
    return UploadFile(file=BytesIO(content.encode('utf-8')), filename="test.txt")

def test_parse_questions_and_answers(json_data_input: UploadFile):
    json_data_input.file.seek(0)
    data = json.load(json_data_input.file)
    parsed_data = parse_questions_and_answers(data)
    assert isinstance(parsed_data, dict)
    assert 'Q1' in parsed_data and 'Q2' in parsed_data
    assert parsed_data['Q1']['answers']['FlowNo_2=1'] == "Pizza"

def test_parse_text_to_json(text_content_input: UploadFile):
    parsed_data = parse_text_to_json(text_content_input)
    assert "Q1" in parsed_data and "Q2" in parsed_data
    assert parsed_data["Q1"]["answers"]["FlowNo_2=1"] == "Pizza"

@pytest.fixture
def dataframe_input():
    df = pd.DataFrame({
        'PhoneNo': ['1234567890', '0987654321'],
        'UserKeyPress': ['FlowNo_2=1', 'FlowNo_2=2']
    })
    return df

def test_rename_columns(dataframe_input: pd.DataFrame):
    new_column_names = ['PhoneNumber', 'UserAction']
    result = rename_columns(dataframe_input, new_column_names)
    assert list(result.columns) == new_column_names

# ---------------------------------------------------
# Third Page Module Tests
# ---------------------------------------------------

def test_parse_text_to_json_third_page(text_content_input: UploadFile):
    text_content_input.file.seek(0)
    content = text_content_input.file.read().decode('utf-8')
    result = parse_text_to_json_third_page(content)
    assert "Q1" in result and "Q2" in result
    assert result["Q1"]["answers"]["FlowNo_2=1"] == "Pizza"

def test_custom_sort():
    result = custom_sort("FlowNo_2=3")
    assert result == {"question_num": 2, "flow_no": 3}

def test_classify_income():
    assert classify_income("RM4,850 & below") == {"income_group": "B40"}
    assert classify_income("RM10,961 to RM15,039") == {"income_group": "T20"}

def test_process_file_content_json(json_data_input: UploadFile):
    result = process_file_content(json_data_input)
    assert result["message"] == "Questions and answers parsed successfully.✨"
    assert "Q1" in result["flow_no_mappings"]
    assert result["flow_no_mappings"]["Q1"]["answers"]["FlowNo_2=1"] == "Pizza"

def test_process_file_content_text(text_content_input: UploadFile):
    result = process_file_content(text_content_input)
    assert result["message"] == "Questions and answers parsed successfully.✨"
    assert "Q1" in result["flow_no_mappings"]
    assert result["flow_no_mappings"]["Q1"]["answers"]["FlowNo_2=1"] == "Coffee"

@pytest.fixture
def flow_no_mappings_input():
    return {
        "Q1": {
            "question": "What is your favorite sport?",
            "answers": {
                "FlowNo_2=1": "Soccer",
                "FlowNo_2=2": "Basketball"
            }
        }
    }

def test_flatten_json_structure(flow_no_mappings_input):
    result = flatten_json_structure(flow_no_mappings_input)
    assert "FlowNo_2=1" in result
    assert result["FlowNo_2=1"] == "Soccer"

# ---------------------------------------------------
# Running Pytest Directly
# ---------------------------------------------------

if __name__ == "__main__":
    pytest.main()
