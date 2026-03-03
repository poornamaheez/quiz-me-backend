from flask import Flask, jsonify, render_template, request, redirect, send_file
from config import Config
from models import db, Subject, Category, Question, Answer
from excel_validator import validate_excel
import os
import pandas as pd

# Create uploads folder if not exists
if not os.path.exists("uploads"):
    os.makedirs("uploads")

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


# ===============================
# HOME
# ===============================
@app.route("/")
def home():
    return redirect("/subjects")


# ===============================
# CREATE TABLES API
# ===============================
@app.route("/api/create-tables")
def create_tables():
    db.create_all()
    return jsonify({"message": "Tables created successfully (if not exists)!"})


# ===============================
# SUBJECTS
# ===============================
@app.route("/subjects", methods=["GET", "POST"])
def subjects():
    if request.method == "POST":
        name = request.form["name"]
        description = request.form.get("description")

        subject = Subject(name=name, description=description)
        db.session.add(subject)
        db.session.commit()

        return redirect("/subjects")

    subjects = Subject.query.all()
    return render_template("subjects.html", subjects=subjects)


# ===============================
# CATEGORIES
# ===============================
@app.route("/categories/<int:subject_id>", methods=["GET", "POST"])
def categories(subject_id):

    if request.method == "POST":
        name = request.form["name"]

        category = Category(
            subject_id=subject_id,
            name=name
        )

        db.session.add(category)
        db.session.commit()

    categories = Category.query.filter_by(subject_id=subject_id).all()
    return render_template("categories.html", categories=categories)


# ===============================
# DOWNLOAD TEMPLATE
# ===============================
@app.route("/download-template")
def download_template():
    df = pd.DataFrame({
        "question_text": [],
        "question_type": [],
        "option_1": [],
        "is_correct_1": [],
        "option_2": [],
        "is_correct_2": [],
        "explanation": [],
        "difficulty": []
    })

    file_path = "template.xlsx"
    df.to_excel(file_path, index=False)

    return send_file(file_path, as_attachment=True)


# ===============================
# UPLOAD QUESTIONS
# ===============================
@app.route("/upload/<int:category_id>", methods=["GET", "POST"])
def upload(category_id):

    category = Category.query.get_or_404(category_id)

    if request.method == "POST":

        file = request.files.get("file")
        if not file:
            return render_template("upload.html", errors=["No file selected"])

        errors, df = validate_excel(file)

        if errors:
            return render_template("upload.html", errors=errors)

        try:
            for index, row in df.iterrows():

                question = Question(
                    subject_id=category.subject_id,  # ✅ FIXED
                    category_id=category_id,
                    question_text=row["question_text"],
                    question_type=row["question_type"],
                    explanation=row.get("explanation"),
                    difficulty=int(row.get("difficulty", 1)),
                    created_by=1
                )

                db.session.add(question)
                db.session.flush()

                option_count = 0
                correct_count = 0

                for col in df.columns:
                    if col.startswith("option_") and pd.notna(row[col]):

                        number = col.split("_")[1]
                        is_correct = bool(row.get(f"is_correct_{number}", False))

                        option = Answer(
                            question_id=question.id,
                            answer_text=row[col],
                            is_correct=is_correct,
                            option_order=int(number)
                        )

                        if is_correct:
                            correct_count += 1

                        option_count += 1
                        db.session.add(option)

                # STRICT VALIDATION
                if option_count < 2:
                    raise Exception(f"Row {index+2}: At least 2 options required")

                if row["question_type"] == "single" and correct_count != 1:
                    raise Exception(f"Row {index+2}: Single type must have exactly 1 correct answer")

                if row["question_type"] == "multiple" and correct_count < 2:
                    raise Exception(f"Row {index+2}: Multiple type must have at least 2 correct answers")

            db.session.commit()

            return render_template("upload.html", success="Upload successful!")

        except Exception as e:
            db.session.rollback()
            return render_template("upload.html", errors=[str(e)])

    return render_template("upload.html")


# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    app.run(debug=True)