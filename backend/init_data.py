from app.models import SessionLocal, init_db, User, Course, KnowledgeNode
# 导入 auth 里的哈希函数 (如果报错找不到，就手动写个字符串 "123456")
# 这里为了稳健，我们在 login 接口里写死了比对 "123456"

def init():
    print("正在重置数据库...")
    init_db()
    db = SessionLocal()
    
    # 清空旧数据 (可选，为了防止重复)
    db.query(User).delete()
    db.query(Course).delete()
    db.commit()

    print("创建标准用户 (密码默认 123456)...")
    users = [
        User(username="admin", role="admin", full_name="管理员", hashed_password="fake_hash"),
        User(username="teacher", role="teacher", full_name="王老师", hashed_password="fake_hash"),
        User(username="student", role="student", full_name="小瑞", hashed_password="fake_hash")
    ]
    db.add_all(users)
    db.commit()

    print("✅ 用户初始化完成！用户名: admin/teacher/student, 密码: 123456")
    db.close()

if __name__ == "__main__":
    init()