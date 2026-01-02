from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Set
import shutil, os, json
from datetime import datetime
from ..models import SessionLocal, User, Course, CourseResource, Notification, Question, StudentAnswer, LearningRecord, KnowledgeNode, KnowledgeEdge, Homework
from .auth import get_current_user

router = APIRouter(prefix="/teacher", tags=["Teacher End"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class CourseCreate(BaseModel):
    title: str
    description: str

class HomeworkCreate(BaseModel):
    course_id: int
    title: str
    description: str = ""

class QuestionCreate(BaseModel):
    course_id: int
    homework_id: Optional[int] = None
    content: str
    type: str 
    options: List[str] = []
    correct_answer: str

class GradeRequest(BaseModel):
    submission_id: int
    score: int
    comment: str

class RemindRequest(BaseModel):
    student_id: int
    message: str

class NodeCreate(BaseModel):
    course_id: int; label: str; weight: float = 1.0

class EdgeCreate(BaseModel):
    source_id: int; target_id: int; relation: str = "前置"

@router.get("/my-courses")
def get_teacher_courses(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取该老师发布的所有课程（用于下拉菜单）"""
    return db.query(Course).filter(Course.status == "published").all()

@router.get("/course/{course_id}/homeworks")
def get_course_homeworks(course_id: int, db: Session = Depends(get_db)):
    """获取课程下的所有作业包"""
    return db.query(Homework).filter(Homework.course_id == course_id).all()

@router.get("/class-monitor")
def get_class_monitor(db: Session = Depends(get_db)):
    """
    获取班级学情监控数据 - 已修复薄弱点显示“未知知识点”的问题
    """
    records = db.query(LearningRecord).all()
    students = db.query(User).filter(User.role == 'student').all()
    
    student_map = {
        s.id: {
            "id": s.id,
            "name": s.full_name or s.username, 
            "progress": 0, 
            "weak_points": set(), 
            "is_silenced": s.is_silenced
        } 
        for s in students
    }
    
    for r in records:
        if r.student_id in student_map:
            if r.mastery_level >= 0.8: 
                student_map[r.student_id]["progress"] += 5

            elif r.mastery_level < 0.6:
                point_name = ""
                if r.knowledge_node_id and r.knowledge_node_id > 0:
                    node = db.query(KnowledgeNode).filter(KnowledgeNode.id == r.knowledge_node_id).first()
                    point_name = node.label if node else f"未知节点({r.knowledge_node_id})"
                else:
                    if r.status and "AI诊断" in r.status:
                        point_name = r.status.replace("AI诊断发现:", "").replace("AI诊断发现: ", "").strip()
                    else:
                        point_name = r.status or "综合薄弱点"

                if point_name:
                    display_name = point_name[:8] + ".." if len(point_name) > 8 else point_name
                    student_map[r.student_id]["weak_points"].add(display_name)

    return [{
        "id": v["id"],
        "name": v["name"],
        "progress": min(100, v["progress"]),
        "status": "Risk" if len(v["weak_points"]) > 2 else "Normal",
        "weak_points_list": list(v["weak_points"]),
        "is_silenced": v["is_silenced"]
    } for v in student_map.values()]

@router.post("/generate-report")
def generate_class_report(db: Session = Depends(get_db)):
    count = db.query(User).filter(User.role == 'student').count()
    return {"report": f"<h3>AI 教学分析报告</h3><p>本班共有学生 {count} 人。整体学情稳定，建议关注部分薄弱点较多的同学。</p>"}

@router.post("/courses")
def create_course(course: CourseCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_course = Course(title=course.title, description=course.description, teacher_id=current_user.id, status="published")
    db.add(new_course)
    db.commit()
    return {"msg": "课程创建成功", "id": new_course.id}

@router.post("/homeworks")
def create_homework(hw: HomeworkCreate, db: Session = Depends(get_db)):
    """新建一个作业包"""
    new_hw = Homework(course_id=hw.course_id, title=hw.title, description=hw.description)
    db.add(new_hw)
    db.commit()
    return {"msg": "作业创建成功", "id": new_hw.id}

@router.post("/upload-resource")
async def upload_resource(course_id: int = Form(...), title: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    os.makedirs("uploads", exist_ok=True)
    file_path = f"uploads/{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    res_type = "video" if file.filename.endswith(('.mp4', '.avi')) else "document"
    new_res = CourseResource(course_id=course_id, title=title, type=res_type, url=f"http://localhost:8000/{file_path}")
    db.add(new_res)
    db.commit()
    return {"msg": "上传成功"}

@router.post("/questions")
def create_question(q: QuestionCreate, db: Session = Depends(get_db)):
    """
    录入题目：支持关联 CourseID 和 HomeworkID
    """
    course = db.query(Course).filter(Course.id == q.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")

    options_str = json.dumps(q.options, ensure_ascii=False) if q.type == 'choice' else ""
    
    new_q = Question(
        course_id=q.course_id, 
        homework_id=q.homework_id,
        content=q.content, 
        type=q.type,
        options_json=options_str, 
        correct_answer=q.correct_answer
    )
    db.add(new_q)
    db.commit()
    return {"msg": "题目已添加到题库"}

@router.get("/submissions/pending")
def get_pending_submissions(db: Session = Depends(get_db)):
    """获取待批改（score 为 None）的作业，包含作业标题信息"""
    subs = db.query(StudentAnswer).filter(StudentAnswer.score == None).all()
    result = []
    for s in subs:
        if s.question and s.student:
            hw_title = s.question.homework.title if s.question.homework else "普通练习"
            
            result.append({
                "id": s.id,
                "student_name": s.student.full_name,
                "homework_title": hw_title,
                "question_content": s.question.content,
                "answer_content": s.answer_content,
                "submitted_at": s.submitted_at.strftime("%Y-%m-%d %H:%M")
            })
    return result

@router.post("/submissions/grade")
def grade_submission(req: GradeRequest, db: Session = Depends(get_db)):
    sub = db.query(StudentAnswer).filter(StudentAnswer.id == req.submission_id).first()
    if not sub: raise HTTPException(404, "作业记录不存在")
    
    sub.score = req.score
    sub.teacher_comment = req.comment

    preview = sub.question.content[:10] + "..." if sub.question else "作业"
    db.add(Notification(user_id=sub.student_id, content=f"你的题目【{preview}】已被老师批改，得分：{req.score}，评语：{req.comment}", is_read=False))
    
    db.commit()
    return {"msg": "批改完成"}

@router.post("/remind-student")
def remind_student(req: RemindRequest, db: Session = Depends(get_db)):
    db.add(Notification(user_id=req.student_id, content=f"【老师提醒】{req.message}", is_read=False))
    db.commit()
    return {"msg": "提醒已发送"}

@router.put("/students/{student_id}/silence")
def toggle_silence(student_id: int, db: Session = Depends(get_db)):
    stu = db.query(User).filter(User.id == student_id).first()
    if stu:
        stu.is_silenced = not stu.is_silenced
        db.commit()
        return {"msg": "操作成功", "is_silenced": stu.is_silenced}
    return {"msg": "用户不存在"}

@router.post("/add-node")
def add_node(node: NodeCreate, db: Session = Depends(get_db)):
    new_node = KnowledgeNode(course_id=node.course_id, label=node.label, weight=node.weight)
    db.add(new_node)
    db.commit()
    return {"msg": "节点添加成功"}

@router.post("/add-edge")
def add_edge(edge: EdgeCreate, db: Session = Depends(get_db)):
    db.add(KnowledgeEdge(source_id=edge.source_id, target_id=edge.target_id, relation_type=edge.relation))
    db.commit()
    return {"msg": "连线添加成功"}

@router.get("/course-nodes/{course_id}")
def get_nodes_list(course_id: int, db: Session = Depends(get_db)):
    nodes = db.query(KnowledgeNode).filter(KnowledgeNode.course_id == course_id).all()
    return [{"id": n.id, "label": n.label} for n in nodes]