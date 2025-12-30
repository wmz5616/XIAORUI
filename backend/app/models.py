from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Float, DateTime, JSON
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from sqlalchemy import create_engine
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./xiaorui_full_system.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="student")
    full_name = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    learn_time = Column(Integer, default=0)
    is_silenced = Column(Boolean, default=False)

    student_records = relationship("LearningRecord", back_populates="student")
    posts = relationship("ForumPost", back_populates="author")
    notifications = relationship("Notification", back_populates="user")
    answers = relationship("StudentAnswer", back_populates="student")

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="draft")
    
    nodes = relationship("KnowledgeNode", back_populates="course")
    resources = relationship("CourseResource", back_populates="course")
    questions = relationship("Question", back_populates="course")

class CourseResource(Base):
    __tablename__ = "course_resources"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    title = Column(String)
    type = Column(String)
    url = Column(String)
    
    course = relationship("Course", back_populates="resources")

class KnowledgeNode(Base):
    __tablename__ = "knowledge_nodes"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    label = Column(String)
    description = Column(Text)
    weight = Column(Float, default=1.0)
    
    course = relationship("Course", back_populates="nodes")

class KnowledgeEdge(Base):
    __tablename__ = "knowledge_edges"
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("knowledge_nodes.id"))
    target_id = Column(Integer, ForeignKey("knowledge_nodes.id"))
    relation_type = Column(String, default="prerequisite")

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    content = Column(Text)
    type = Column(String, default="choice")
    options_json = Column(String)
    correct_answer = Column(String)
    
    course = relationship("Course", back_populates="questions")
    student_answers = relationship("StudentAnswer", back_populates="question")

class StudentAnswer(Base):
    __tablename__ = "student_answers"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    answer_content = Column(Text)
    score = Column(Integer, default=None)
    teacher_comment = Column(Text)
    submitted_at = Column(DateTime, default=datetime.now)

    student = relationship("User", back_populates="answers")
    question = relationship("Question", back_populates="student_answers")

class LearningRecord(Base):
    __tablename__ = "learning_records"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    knowledge_node_id = Column(Integer, ForeignKey("knowledge_nodes.id"))
    mastery_level = Column(Float, default=0.0)
    last_practice_date = Column(DateTime, default=datetime.now)
    status = Column(String)
    
    student = relationship("User", back_populates="student_records")

class ForumPost(Base):
    __tablename__ = "forum_posts"
    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    content = Column(Text)
    type = Column(String, default="discussion")
    is_pinned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    
    author = relationship("User", back_populates="posts")

class SystemConfig(Base):
    __tablename__ = "system_configs"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True)
    value = Column(String)
    description = Column(String)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(String)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    
    user = relationship("User", back_populates="notifications")

def init_db():
    Base.metadata.create_all(bind=engine)