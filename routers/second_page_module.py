import re

async def parse_questions_and_answers(json_data):
            """
            Parses questions and their respective answers from a JSON data structure.

            Parameters:
            - json_data (dict): A dictionary containing questions as keys and their details (question text and answers) as values.

            Returns:
            - dict: A dictionary with question numbers as keys and a sub-dictionary containing the question text and a list of answers.
            """
            questions_and_answers = {}
            for q_key, q_value in json_data.items():
                question_text = q_value['question']
                answers = [answer for _, answer in q_value['answers'].items()]
                questions_and_answers[q_key] = {'question': question_text, 'answers': answers}
            return questions_and_answers

async def parse_text_to_json(text_content):
            """
            Converts structured text content into a JSON-like dictionary, parsing questions and their answers.

            Parameters:
            - text_content (str): Text content containing questions and answers in a structured format.

            Returns:
            - dict: A dictionary representing the parsed content with questions as keys and their details (question text and answers) as values.
            """
            data = {}
            question_re = re.compile(r'^(\d+)\.\s+(.*)')
            answer_re = re.compile(r'^\s+-\s+(.*)')
            current_question = ""

            for line in text_content.splitlines():
                question_match = question_re.match(line)
                answer_match = answer_re.match(line)

                if question_match:
                    q_number, q_text = question_match.groups()
                    current_question = f"Q{q_number}"
                    data[current_question] = {"question": q_text, "answers": {}}
                elif answer_match and current_question:
                    answer_text = answer_match.groups()[0]
                    flow_no = len(data[current_question]["answers"]) + 1
                    flow_no_key = f"FlowNo_{int(q_number)+1}={flow_no}"
                    data[current_question]["answers"][flow_no_key] = answer_text

            return data

async def rename_columns(df, new_column_names):
            """
            Renames dataframe columns based on a list of new column names.
            
            Parameters:
            - df (pd.DataFrame): The original DataFrame.
            - new_column_names (list): A list of new column names corresponding to the DataFrame's columns.
            
            Returns:
            - pd.DataFrame: A DataFrame with updated column names.
            """
            mapping = {old: new for old, new in zip(df.columns, new_column_names) if new}
            return df.rename(columns=mapping, inplace=False)