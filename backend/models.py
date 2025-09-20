import uuid
from sqlalchemy import Column, String, Integer, Date, Float, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def gen_uuid():
    return str(uuid.uuid4())

class Student(Base):
    __tablename__ = "students"
    student_id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    roll_no = Column(String, unique=True)
    batch = Column(String)
    course = Column(String)
    email = Column(String)
    phone = Column(String)

class Exam(Base):
    __tablename__ = "exams"
    exam_id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    exam_name = Column(String, nullable=False)
    exam_date = Column(Date)
    num_questions = Column(Integer, default=100)
    num_subjects = Column(Integer, default=5)

class Subject(Base):
    __tablename__ = "subjects"
    subject_id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    exam_id = Column(UUID(as_uuid=False), ForeignKey("exams.exam_id"), nullable=False)
    name = Column(String, nullable=False)
    start_qno = Column(Integer, nullable=False)
    end_qno = Column(Integer, nullable=False)

class AnswerKey(Base):
    __tablename__ = "answer_keys"
    key_id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    exam_id = Column(UUID(as_uuid=False), ForeignKey("exams.exam_id"), nullable=False)
    version = Column(String, nullable=False)
    question_no = Column(Integer, nullable=False)
    correct_option = Column(String, nullable=False)

class OMRSheet(Base):
    __tablename__ = "omr_sheets"
    sheet_id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    exam_id = Column(UUID(as_uuid=False), ForeignKey("exams.exam_id"), nullable=False)
    student_id = Column(UUID(as_uuid=False), ForeignKey("students.student_id"))
    version = Column(String)
    file_path = Column(String)
    status = Column(String, default="uploaded")
    uploaded_at = Column(TIMESTAMP)

class Response(Base):
    __tablename__ = "responses"
    response_id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    sheet_id = Column(UUID(as_uuid=False), ForeignKey("omr_sheets.sheet_id"), nullable=False)
    question_no = Column(Integer, nullable=False)
    marked_option = Column(String)
    confidence = Column(Float)

class Score(Base):
    __tablename__ = "scores"
    score_id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    exam_id = Column(UUID(as_uuid=False), ForeignKey("exams.exam_id"), nullable=False)
    student_id = Column(UUID(as_uuid=False), ForeignKey("students.student_id"), nullable=False)
    subject_id = Column(UUID(as_uuid=False), ForeignKey("subjects.subject_id"), nullable=False)
    score = Column(Integer, nullable=False)

class TotalScore(Base):
    __tablename__ = "total_scores"
    total_id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    exam_id = Column(UUID(as_uuid=False), ForeignKey("exams.exam_id"), nullable=False)
    student_id = Column(UUID(as_uuid=False), ForeignKey("students.student_id"), nullable=False)
    total_score = Column(Integer, nullable=False)
