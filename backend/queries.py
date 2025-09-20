from models import Student, OMRSheet, Response, Score, TotalScore
from sqlalchemy.orm import Session

def add_student(db: Session, name, roll_no, batch=None, course=None, email=None, phone=None):
    s = Student(name=name, roll_no=roll_no, batch=batch, course=course, email=email, phone=phone)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s

def save_sheet(db: Session, exam_id, student_id, version, file_path):
    sheet = OMRSheet(exam_id=exam_id, student_id=student_id, version=version, file_path=file_path)
    db.add(sheet)
    db.commit()
    db.refresh(sheet)
    return sheet

def save_responses(db: Session, sheet_id, responses):
    for qno, marked in responses.items():
        db.add(Response(sheet_id=sheet_id, question_no=qno, marked_option=marked))
    db.commit()

def save_score(db: Session, exam_id, student_id, subject_id, score_value):
    sc = Score(exam_id=exam_id, student_id=student_id, subject_id=subject_id, score=score_value)
    db.add(sc)
    db.commit()
    return sc

def save_total(db: Session, exam_id, student_id, total):
    ts = TotalScore(exam_id=exam_id, student_id=student_id, total_score=total)
    db.add(ts)
    db.commit()
    return ts
