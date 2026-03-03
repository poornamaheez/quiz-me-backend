import pandas as pd

def validate_excel(file):

    errors = []
    df = pd.read_excel(file)

    required_columns = ["question_text", "question_type"]

    for col in required_columns:
        if col not in df.columns:
            errors.append(f"Missing required column: {col}")

    if errors:
        return errors, None

    for index, row in df.iterrows():

        if pd.isna(row["question_text"]):
            errors.append(f"Row {index+2}: Question text missing")

        if row["question_type"] not in ["single", "multiple"]:
            errors.append(f"Row {index+2}: Question type must be 'single' or 'multiple'")

        if "difficulty" in df.columns:
            if not pd.isna(row["difficulty"]):
                if int(row["difficulty"]) not in [1, 2, 3]:
                    errors.append(f"Row {index+2}: Difficulty must be 1, 2 or 3")

    return errors, df