import re
from fastapi import APIRouter, UploadFile
from pydantic import BaseModel, Field
from typing import List
import pandas as pd
from pydantic import BaseModel, Field
from typing import Dict, List
from fastapi import HTTPException

router = APIRouter(prefix="/second_page", tags=["Questionnaire_Definer"])

class Question(BaseModel):
    question: str
    answers: Dict[str, str]

class Questionnaire(BaseModel):
    questions: Dict[str, Question]

@router.post("/parse_qna")
def parse_questions_and_answers(questionnaire: Questionnaire):
    try:
        questions_and_answers = {
            q_key: {
                "question": q_val.question,
                "answers": q_val.answers
            } for q_key, q_val in questionnaire.questions.items()
        }
        return questions_and_answers
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class TextContent(BaseModel):
    text_content: str

@router.post("/parse_text_to_json")
def parse_text_to_json(input_data: TextContent):
    content = input_data.text_content
    
    data = {}
    question_re = re.compile(r'^(\d+)\.\s*(.*)')
    answer_re = re.compile(r'^\s*-\s*(.*)')
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

class RenameColumnsRequest(BaseModel):
    columns: List[str]
    data: List[List[str]]
    new_column_names: List[str]

@router.post("/rename_columns")
def rename_columns(request: RenameColumnsRequest):
    """Renaming DataFrame columns based on a list of new column names."""
    df = pd.DataFrame(data=request.data, columns=request.columns)
    df = df.rename(columns=dict(zip(df.columns, request.new_column_names)), inplace=False)
    return df.to_dict(orient='records')

