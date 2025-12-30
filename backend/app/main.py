from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from .models import init_db
from .routers import student, teacher, admin, ai_engine, auth, forum, quiz

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

init_db()

app = FastAPI(title="XIAORUI智能教育平台")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(student.router)
app.include_router(teacher.router)
app.include_router(admin.router)
app.include_router(ai_engine.router)
app.include_router(auth.router)
app.include_router(forum.router)
app.include_router(quiz.router)

@app.get("/")
def root():
    return {"status": "System Running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)