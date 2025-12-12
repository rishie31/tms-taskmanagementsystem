# backend/app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
from datetime import datetime
import os

app = FastAPI(
    title="Task Management API",
    description="Backend API for Task Management System",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tasks.db")
DB_PATH = DATABASE_URL.replace("sqlite:///", "")


def init_db():
    """Initialize database with tasks table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


# Initialize database on startup
init_db()


# Pydantic models
class TaskCreate(BaseModel):
    title: str
    completed: bool = False


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None


class Task(BaseModel):
    id: int
    title: str
    completed: bool
    created_at: str


# API endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "taskmanagement-backend",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/tasks", response_model=List[Task])
async def get_tasks():
    """Get all tasks"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, completed, created_at FROM tasks ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    tasks = [
        Task(
            id=row[0],
            title=row[1],
            completed=bool(row[2]),
            created_at=row[3]
        )
        for row in rows
    ]
    return tasks


@app.get("/api/tasks/{task_id}", response_model=Task)
async def get_task(task_id: int):
    """Get a specific task"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, completed, created_at FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return Task(
        id=row[0],
        title=row[1],
        completed=bool(row[2]),
        created_at=row[3]
    )


@app.post("/api/tasks", response_model=Task, status_code=201)
async def create_task(task: TaskCreate):
    """Create a new task"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, completed) VALUES (?, ?)",
        (task.title, task.completed)
    )
    task_id = cursor.lastrowid
    conn.commit()
    
    cursor.execute("SELECT id, title, completed, created_at FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    
    return Task(
        id=row[0],
        title=row[1],
        completed=bool(row[2]),
        created_at=row[3]
    )


@app.put("/api/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, task: TaskUpdate):
    """Update a task"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if task exists
    cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update task
    update_fields = []
    params = []
    
    if task.title is not None:
        update_fields.append("title = ?")
        params.append(task.title)
    
    if task.completed is not None:
        update_fields.append("completed = ?")
        params.append(task.completed)
    
    if update_fields:
        params.append(task_id)
        query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()
    
    # Get updated task
    cursor.execute("SELECT id, title, completed, created_at FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    
    return Task(
        id=row[0],
        title=row[1],
        completed=bool(row[2]),
        created_at=row[3]
    )


@app.delete("/api/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int):
    """Delete a task"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")
    
    conn.commit()
    conn.close()
    return None


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Task Management API - Enhanced Version",
        "version": "2.0.0",
        "endpoints": {
            "health": "/health",
            "tasks": "/api/tasks",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)