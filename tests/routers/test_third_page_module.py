import re
import json
from fastapi import APIRouter

router = APIRouter(prefix="/third_page", tags=["Keypress_Decoder"])

@router.get("/custom_sort")
def custom_sort(col):
            # Improved regex to capture question and flow numbers accurately
            match = re.match(r"FlowNo_(\d+)=*(\d*)", col)
            if match:
                question_num = int(match.group(1))  # Question number
                flow_no = int(match.group(2)) if match.group(2) else 0  # Flow number, default to 0 if not present
                return { "question_num" : question_num, "flow_no": flow_no}
            else:
                return {"question_num":float('inf'),"flow_no":0}

@router.get("/classify_income")
def classify_income(income):
            if income == 'RM4,850 & below':
                return {"income_group": 'B40'}
            elif income == 'RM4,851 to RM10,960':
                return {"income_group":'M40'}
            elif income in ['RM15,040 & above', 'RM10,961 to RM15,039']:
                return {"income_group":'T20'}


def parse_text_to_json_third_page(text_content):
            """
            Parses structured text containing survey questions and answers into a JSON-like dictionary.
            Adjusts FlowNo to start from 2 for the first question as specified.
            """

            # Initialize variables
            data = {}
            current_question = None

            # Regular expressions for identifying parts of the text
            question_re = re.compile(r'^(\d+)\.\s+(.*)')
            answer_re = re.compile(r'^\s+-\s+(.*)')

            for line in text_content.splitlines():
                question_match = question_re.match(line)
                answer_match = answer_re.match(line)

                if question_match:
                    # New question found
                    q_number, q_text = question_match.groups()
                    current_question = f"Q{q_number}"
                    data[current_question] = {"question": q_text, "answers": {}}
                elif answer_match and current_question:
                    # Answer found for the current question
                    answer_text = answer_match.groups()[0]
                    # Assuming FlowNo starts at 2 for the first question and increments for each answer within a question
                    flow_no = len(data[current_question]["answers"]) + 1
                    # Adjusting FlowNo to start from 2 for the first question and increment accordingly for each answer
                    flow_no_key = f"FlowNo_{int(q_number)+1}={flow_no}"
                    data[current_question]["answers"][flow_no_key] = answer_text

            return data

@router.get("/process_file_content")
def process_file_content(uploaded_file):
            """Process the content of the uploaded file."""
            try:
                if uploaded_file and uploaded_file.type == "application/json":
                    # Handle JSON file
                    flow_no_mappings = json.loads(uploaded_file.getvalue().decode("utf-8"))
                else:
                    # Handle plain text file
                    flow_no_mappings = parse_text_to_json_third_page(uploaded_file.getvalue().decode("utf-8"))
                return {"flow_no_mappings":flow_no_mappings, "message" : "Questions and answers parsed successfully.✨", "error":None}
            except Exception as e:
                return {"flow_no_mappings":None,"message": None,"error": f"Error processing file: {e}"}
            
@router.get("/flatten_json_structure")
def flatten_json_structure(flow_no_mappings):
            """Flatten the JSON structure to simplify the mapping access."""
            if not flow_no_mappings:
                return {}
            return {k: v for question in flow_no_mappings.values() for k, v in question["answers"].items()}
