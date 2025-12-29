from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Float, DateTime
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from sqlalchemy import create_engine
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./xiaorui_full_system.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 1. 用户与权限 (User & RBAC)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="student")
    full_name = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关联
    student_records = relationship("LearningRecord", back_populates="student")
    posts = relationship("ForumPost", back_populates="author")

# 2. 课程与资源 (Course & Resources)
class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="draft") # draft, published
    
    nodes = relationship("KnowledgeNode", back_populates="course")

class CourseResource(Base):
    __tablename__ = "course_resources"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    title = Column(String)
    type = Column(String) # 'video', 'article', 'quiz'
    url = Column(String) # 文件路径或外链

# 3. 核心：知识图谱 (Knowledge Graph)
class KnowledgeNode(Base):
    __tablename__ = "knowledge_nodes"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    label = Column(String) # 知识点名称
    description = Column(Text)
    weight = Column(Float, default=1.0) # 知识点重要性权重
    
    course = relationship("Course", back_populates="nodes")
    # 边关系将在应用层逻辑中处理，或增加 Edge 表

class KnowledgeEdge(Base):
    __tablename__ = "knowledge_edges"
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("knowledge_nodes.id")) # 前置知识点
    target_id = Column(Integer, ForeignKey("knowledge_nodes.id")) # 后续知识点
    relation_type = Column(String, default="prerequisite") # 关系类型：前置/包含

# 4. 学生学情 (Learning Analytics)
class LearningRecord(Base):
    __tablename__ = "learning_records"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    knowledge_node_id = Column(Integer, ForeignKey("knowledge_nodes.id"))
    
    mastery_level = Column(Float, default=0.0) # 0.0 - 1.0 (掌握程度)
    last_practice_date = Column(DateTime, default=datetime.now)
    status = Column(String) # 'learning', 'mastered', 'struggling'
    
    student = relationship("User", back_populates="student_records")

# 5. 社区互动 (Community)
class ForumPost(Base):
    __tablename__ = "forum_posts"
    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    content = Column(Text)
    type = Column(String, default="discussion") # 'question', 'discussion'
    created_at = Column(DateTime, default=datetime.now)
    
    author = relationship("User", back_populates="posts")

# 6. 系统管理 (System Config)
class SystemConfig(Base):
    __tablename__ = "system_configs"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True) # e.g., 'ai_model_version', 'recommendation_threshold'
    value = Column(String)
    description = Column(String)

# 初始化表结构
def init_db():
    Base.metadata.create_all(bind=engine)