import re
from fastapi import APIRouter, UploadFile
import json

router = APIRouter(prefix="/second_page", tags=["Questionnaire_Definer"])

@router.post("/parse_qna")
def parse_questions_and_answers(data):
    """
    Parses questions and their respective answers from a JSON data structure.
    Parameters:
    - data (dict): A dictionary containing questions as keys and their details (question text and answers) as values.
    Returns:
    - dict: A dictionary with question numbers as keys and a sub-dictionary containing the question text and a dictionary of answers.
    """
    questions_and_answers = dict()
    for q_key, q_value in data.items():
        question_text = q_value['question']
        answers = {key: answer for key, answer in q_value['answers'].items()}
        questions_and_answers[q_key] = {'question': question_text, 'answers': answers}
    return questions_and_answers

@router.post("/parse_texttojson")
def parse_text_to_json(upload_file: UploadFile):
    """
    Converts structured text content into a JSON-like dictionary, parsing questions and their answers.
    Parameters:
    - upload_file (UploadFile): The uploaded file containing structured text content.
    Returns:
    - dict: A dictionary representing the parsed content with questions as keys and their details (question text and answers) as values.
    """
    # Rewind and read the file content
    upload_file.file.seek(0)
    content = upload_file.file.read().decode('utf-8')
    
    data = {}
    question_re = re.compile(r'^(\d+)\.\s*(.*)')  # Adjusted to allow optional spaces after the period
    answer_re = re.compile(r'^\s*-\s*(.*)')  # Adjusted to allow optional spaces around the dash
    current_question = None

    for line in content.splitlines():
        question_match = question_re.match(line)
        answer_match = answer_re.match(line)

        if question_match:
            q_number, q_text = question_match.groups()
            current_question = f"Q{q_number}"
            data[current_question] = {"question": q_text, "answers": {}}
        elif answer_match and current_question:
            answer_text = answer_match.group(1)
            flow_no = len(data[current_question]["answers"]) + 1
            flow_no_key = f"FlowNo_{int(q_number)+1}={flow_no}"
            data[current_question]["answers"][flow_no_key] = answer_text

    return data

@router.post("/rename_columns")
def rename_columns(df, new_column_names):
    """Renaming DataFrame columns based on a list of new column names."""
    mapping = dict(zip(df.columns, new_column_names))
    return df.rename(columns=mapping, inplace=False)