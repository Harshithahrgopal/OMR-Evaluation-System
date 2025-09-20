CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE students (
  student_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  roll_no TEXT UNIQUE,
  batch TEXT,
  course TEXT,
  email TEXT,
  phone TEXT
);

CREATE TABLE exams (
  exam_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  exam_name TEXT NOT NULL,
  exam_date DATE,
  num_questions INT DEFAULT 100,
  num_subjects INT DEFAULT 5
);

CREATE TABLE subjects (
  subject_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  exam_id UUID REFERENCES exams(exam_id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  start_qno INT NOT NULL,
  end_qno INT NOT NULL
);

CREATE TABLE answer_keys (
  key_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  exam_id UUID REFERENCES exams(exam_id) ON DELETE CASCADE,
  version TEXT NOT NULL,
  question_no INT NOT NULL,
  correct_option TEXT NOT NULL,
  UNIQUE (exam_id, version, question_no)
);

CREATE TABLE omr_sheets (
  sheet_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  exam_id UUID REFERENCES exams(exam_id) ON DELETE CASCADE,
  student_id UUID REFERENCES students(student_id),
  version TEXT,
  file_path TEXT,
  status TEXT DEFAULT 'uploaded',
  uploaded_at TIMESTAMP DEFAULT now()
);

CREATE TABLE responses (
  response_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  sheet_id UUID REFERENCES omr_sheets(sheet_id) ON DELETE CASCADE,
  question_no INT NOT NULL,
  marked_option TEXT,
  confidence FLOAT,
  UNIQUE (sheet_id, question_no)
);

CREATE TABLE scores (
  score_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  exam_id UUID REFERENCES exams(exam_id) ON DELETE CASCADE,
  student_id UUID REFERENCES students(student_id) ON DELETE CASCADE,
  subject_id UUID REFERENCES subjects(subject_id) ON DELETE CASCADE,
  score INT NOT NULL,
  UNIQUE (exam_id, student_id, subject_id)
);

CREATE TABLE total_scores (
  total_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  exam_id UUID REFERENCES exams(exam_id),
  student_id UUID REFERENCES students(student_id),
  total_score INT NOT NULL,
  UNIQUE (exam_id, student_id)
);
