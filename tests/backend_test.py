import pytest
import pandas as pd
from io import StringIO, BytesIO
import json
from tests.test_main import app
from tests.routers.test_first_page_module import merger, process_file
from tests.routers.test_second_page_module import parse_questions_and_answers, parse_text_to_json, rename_columns
from tests.routers.test_third_page_module import parse_text_to_json_third_page, custom_sort, classify_income, process_file_content, flatten_json_structure
from fastapi import UploadFile
from starlette.datastructures import UploadFile as StarletteUploadFile 
from typing import Any

# ---------------------------------------------------
# Connection Test
# ---------------------------------------------------

@app.get("/")
def read_main():
    return {"message": "Welcome to the Unit Testing"}

# ---------------------------------------------------s
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
    data = json.dumps({
        "Q1": {
            "question": "What is your favorite fruit?",
            "answers": {
                "FlowNo_2=1": "Apple",
                "FlowNo_2=2": "Banana"
            }
        },
        "Q2": {
            "question": "What is your favorite color?",
            "answers": {
                "FlowNo_3=1": "Blue",
                "FlowNo_3=2": "Red",
                "FlowNo_3=3": "Green"
            }
        }
    })
    return UploadFile(file=BytesIO(data.encode('utf-8')), filename="test.json")

@pytest.fixture
def text_content_input():
    content = (
        "1. What is your favorite fruit?\n"
        "   - Apple\n"
        "   - Banana\n\n"
        "2. What is your favorite color?\n"
        "   - Blue\n"
        "   - Red\n"
        "   - Green"
    )
    return UploadFile(file=BytesIO(content.encode('utf-8')), filename="test.txt")

def test_parse_questions_and_answers(json_data_input: UploadFile):
    json_data_input.file.seek(0)  # Rewind the file to the start
    data = json.load(json_data_input.file)  # Reading and decoding JSON data correctly
    parsed_data = parse_questions_and_answers(data)
    assert isinstance(parsed_data, dict)
    assert 'Q1' in parsed_data and 'Q2' in parsed_data
    assert parsed_data['Q1']['answers']['FlowNo_2=1'] == "Apple"
    assert parsed_data['Q2']['answers']['FlowNo_3=1'] == "Blue"

def test_parse_text_to_json(text_content_input: UploadFile):
    parsed_data = parse_text_to_json(text_content_input)
    assert "Q1" in parsed_data and "Q2" in parsed_data
    assert parsed_data["Q1"]["answers"]["FlowNo_2=1"] == "Apple"
    assert parsed_data["Q2"]["answers"]["FlowNo_3=1"] == "Blue"

def test_rename_columns(create_data: pd.DataFrame):
    new_column_names = ['PhoneNumber', 'UserAction']
    result = rename_columns(create_data, new_column_names)
    assert list(result.columns) == new_column_names

# ---------------------------------------------------
# Third Page Module Tests
# ---------------------------------------------------

def test_parse_text_to_json_third_page(text_content_input: UploadFile):
    text_content_input.file.seek(0)
    content = text_content_input.file.read().decode('utf-8')
    result = parse_text_to_json_third_page(content)
    assert "Q1" in result and "Q2" in result
    assert result["Q1"]["answers"]["FlowNo_2=1"] == "Apple"
    assert result["Q2"]["answers"]["FlowNo_3=1"] == "Blue"

def test_custom_sort():
    result = custom_sort("FlowNo_2=3")
    assert result == {"question_num": 2, "flow_no": 3}

def test_classify_income():
    assert classify_income("RM4,850 & below") == {"income_group": "B40"}
    assert classify_income("RM10,961 to RM15,039") == {"income_group": "T20"}

@pytest.fixture
def json_file_input():
    data = '{"Q1": {"question": "Did you vote in the Petaling Jaya Parliament?", "answers": {"FlowNo_2=1": "Yes", "FlowNo_2=2": "No"}}}'
    return UploadFile(content=BytesIO(data.encode()), filename="test.json", content_type="application/json")


@pytest.fixture
def flow_no_mappings_input():
    return {
        "Q1": {
            "question": "Did you vote in the Petaling Jaya Parliament?",
            "answers": {
                "FlowNo_2=1": "Yes",
                "FlowNo_2=2": "No"
            }
        }
    }


def test_process_file_content_json(json_file_input: UploadFile):
    result = process_file_content(json_file_input)
    assert result["message"] == "Questions and answers parsed successfully.✨"
    assert "Q1" in result["flow_no_mappings"]
    assert result["flow_no_mappings"]["Q1"]["answers"]["FlowNo_2=1"] == "Yes"
    assert result["flow_no_mappings"]["Q1"]["answers"]["FlowNo_2=2"] == "No"


@pytest.fixture
def text_file_input():
    content = "1. What is your favorite sport?\n   - Soccer\n   - Basketball\n2. What is your favorite color?\n   - Blue\n   - Red\n   - Green"
    return UploadFile(content=BytesIO(content.encode()), filename="test.txt", content_type="text/plain")


def test_process_file_content_text(text_file_input: UploadFile):
    result = process_file_content(text_file_input)
    assert result["message"] == "Questions and answers parsed successfully.✨"
    assert "Q1" in result["flow_no_mappings"]
    assert result["flow_no_mappings"]["Q1"]["answers"]["FlowNo_2=1"] == "Soccer"


@pytest.fixture
def flow_no_mappings_input():
    return {
        "Q1": {
            "question": "What is your favorite hobby?",
            "answers": {
                "FlowNo_2=1": "Reading",
                "FlowNo_2=2": "Writing"
            }
        }
    }

def test_flatten_json_structure(flow_no_mappings_input: dict[str, dict[str, Any]]):
    result = flatten_json_structure(flow_no_mappings_input)
    assert "FlowNo_2=1" in result
    assert result["FlowNo_2=1"] == "Reading"

# ---------------------------------------------------
# Running Pytest Directly
# ---------------------------------------------------

if __name__ == "__main__":
    pytest.main()
