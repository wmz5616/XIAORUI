from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Float, DateTime, JSON
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from sqlalchemy import create_engine
from datetime import datetime

# 数据库连接
SQLALCHEMY_DATABASE_URL = "sqlite:///./xiaorui_full_system.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 1. 用户与权限
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="student")
    full_name = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    learn_time = Column(Integer, default=0)
    
    student_records = relationship("LearningRecord", back_populates="student")
    posts = relationship("ForumPost", back_populates="author")

# 2. 课程与资源
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
    
    # ✅ 修复点：补全了这行关联代码
    course = relationship("Course", back_populates="resources")

# 3. 知识图谱
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

# 4. 真实题库
class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    content = Column(Text)
    options_json = Column(String) 
    correct_answer = Column(Integer) 
    
    course = relationship("Course", back_populates="questions")

# 5. 学情记录
class LearningRecord(Base):
    __tablename__ = "learning_records"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    knowledge_node_id = Column(Integer, ForeignKey("knowledge_nodes.id"))
    
    mastery_level = Column(Float, default=0.0)
    last_practice_date = Column(DateTime, default=datetime.now)
    status = Column(String)
    
    student = relationship("User", back_populates="student_records")

# 6. 社区
class ForumPost(Base):
    __tablename__ = "forum_posts"
    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    content = Column(Text)
    type = Column(String, default="discussion")
    created_at = Column(DateTime, default=datetime.now)
    
    author = relationship("User", back_populates="posts")

class SystemConfig(Base):
    __tablename__ = "system_configs"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True)
    value = Column(String)
    description = Column(String)

def init_db():
    Base.metadata.create_all(bind=engine)