#pytest .\tests\backend_test.py
import pytest
import pandas as pd
from io import StringIO, BytesIO
import json

# Correct imports based on your project structure
from tests.test_main import app
from tests.routers.test_first_page_module import merger, process_file
from tests.routers.test_second_page_module import parse_questions_and_answers, parse_text_to_json, rename_columns
from tests.routers.test_third_page_module import parse_text_to_json_third_page, custom_sort, classify_income

# --------------------------- Connection Test ---------------------------

@app.get("/")
def read_main():
    return {"message": "Welcome to the Unit Testing"}

# --------------------------- First Page Module Tests ---------------------------

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
    """Test the merger function from the first page module."""
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

# --------------------------- Second Page Module Tests ---------------------------

from fastapi import UploadFile
from starlette.datastructures import UploadFile as StarletteUploadFile

@pytest.fixture
def json_data_input():
    data = json.dumps({
        "Q1": {
            "question": "Did you vote in the Petaling Jaya Parliament?",
            "answers": {
                "FlowNo_2=1": "Yes",
                "FlowNo_2=2": "No"
            }
        },
        "Q2": {
            "question": "Do you agree with the cancellation of the PJD Link?",
            "answers": {
                "FlowNo_3=1": "Yes",
                "FlowNo_3=2": "No",
                "FlowNo_3=3": "Unsure",
                "FlowNo_3=4": "Does not mind"
            }
        }
    })
    return UploadFile(file=BytesIO(data.encode('utf-8')), filename="test.json")


@pytest.fixture
def text_content_input():
    content = (
        "1. Did you vote in the Batu Pahat Parliament?\n"
        "   - Yes\n"
        "   - No\n\n"
        "2. Ethnicity\n"
        "   - Malay\n"
        "   - Chinese\n"
        "   - Indian\n"
        "   - Others"
    )
    return UploadFile(file=BytesIO(content.encode('utf-8')), filename="test.txt")


def test_parse_questions_and_answers(json_data_input: UploadFile):
    """Test the parsing of questions and answers from JSON for the second page module."""
    json_data_input.file.seek(0)  # Rewind the file to the start
    data = json.load(json_data_input.file)  # Reading and decoding JSON data correctly
    parsed_data = parse_questions_and_answers(data)  # Pass the dictionary data
    assert isinstance(parsed_data, dict)
    assert 'Q1' in parsed_data
    assert 'Q2' in parsed_data
    assert parsed_data['Q1']['question'] == "Did you vote in the Petaling Jaya Parliament?"
    assert parsed_data['Q1']['answers']['FlowNo_2=1'] == "Yes"
    assert parsed_data['Q1']['answers']['FlowNo_2=2'] == "No"
    


def test_parse_text_to_json(text_content_input: UploadFile):
    """Test the conversion of structured text to JSON for parsing questions and answers."""
    parsed_data = parse_text_to_json(text_content_input)
    assert "Q1" in parsed_data
    assert parsed_data["Q1"]["question"] == "Did you vote in the Batu Pahat Parliament?"
    assert "FlowNo_2=1" in parsed_data["Q1"]["answers"]
    assert parsed_data["Q1"]["answers"]["FlowNo_2=1"] == "Yes"
    assert "Q2" in parsed_data
    assert parsed_data["Q2"]["question"] == "Ethnicity"
    assert "FlowNo_3=1" in parsed_data["Q2"]["answers"]
    assert parsed_data["Q2"]["answers"]["FlowNo_3=1"] == "Malay"


@pytest.fixture
def dataframe_input():
    df = pd.DataFrame({
        'PhoneNo': ['1234567890', '0987654321'],
        'UserKeyPress': ['FlowNo_2=1', 'FlowNo_2=2']
    })
    return df

def test_rename_columns(dataframe_input: pd.DataFrame):
    """Test renaming DataFrame columns."""
    new_column_names = ['PhoneNumber', 'UserAction']
    result = rename_columns(dataframe_input, new_column_names)
    assert list(result.columns) == new_column_names  # This will now work because result is a DataFrame


# --------------------------- Third Page Module Tests ---------------------------

def test_parse_text_to_json_third_page(text_content_input: UploadFile):
    """Test parsing of text to JSON on the third page, checking adjusted FlowNo."""
    text_content_input.file.seek(0)  # Ensure the file pointer is at the start
    content = text_content_input.file.read().decode('utf-8')
    result = parse_text_to_json_third_page(content)
    assert "Q1" in result
    assert result["Q1"]["question"] == "Did you vote in the Batu Pahat Parliament?"
    assert "FlowNo_2=1" in result["Q1"]["answers"]
    assert result["Q1"]["answers"]["FlowNo_2=1"] == "Yes"
    assert "Q2" in result
    assert result["Q2"]["question"] == "Ethnicity"
    assert result["Q2"]["answers"]["FlowNo_3=1"] == "Malay"


def test_custom_sort():
    """Test the custom sorting functionality for the third page module."""
    result = custom_sort("FlowNo_2=3")
    assert result == {"question_num": 2, "flow_no": 3}

def test_classify_income():
    """Test classification of income into economic groups for the third page module."""
    assert classify_income("RM4,850 & below") == {"income_group": "B40"}
    assert classify_income("RM10,961 to RM15,039") == {"income_group": "T20"}

# --------------------------- Running Pytest Directly ---------------------------

if __name__ == "__main__":
    pytest.main()
