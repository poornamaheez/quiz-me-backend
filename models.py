from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(500))
    status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.BigInteger, primary_key=True)
    subject_id = db.Column(db.BigInteger, db.ForeignKey("subjects.id"))
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(500))
    order_no = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.BigInteger, primary_key=True)
    subject_id = db.Column(db.BigInteger, db.ForeignKey("subjects.id"))
    category_id = db.Column(db.BigInteger, db.ForeignKey("categories.id"))
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.Enum('single', 'multiple'))
    explanation = db.Column(db.Text)
    difficulty = db.Column(db.Integer)
    created_by = db.Column(db.BigInteger)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Answer(db.Model):
    __tablename__ = "answers"

    id = db.Column(db.BigInteger, primary_key=True)
    question_id = db.Column(db.BigInteger, db.ForeignKey("questions.id"))
    answer_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    option_order = db.Column(db.Integer)