from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A lightweight CRUD API for managing tasks."
)


class Task(BaseModel):
    id: int
    title: str
    done: bool = False

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Task title cannot be empty")

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    done: Optional[bool] = None

# Initial In-Memory "Database" (Stage 2)
tasks_db = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Read backend lecture notes", "done": True},
    {"id": 3, "title": "Complete Week 2 Assignment", "done": False},
]

# Helper to find next free ID (Stage 3)
def get_next_id() -> int:
    return max([t["id"] for t in tasks_db], default=0) + 1



@app.get("/", summary="Root Endpoint")
def get_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health", summary="Health Check Endpoint")
def get_health():
    return {"status": "ok"}


# ----------------------------------------------------
# Stage 2: Read Endpoints
# ----------------------------------------------------
@app.get("/tasks", response_model=list[Task], summary="List All Tasks")
def get_tasks():
    return tasks_db

@app.get("/tasks/{id}", response_model=Task, summary="Get Single Task")
def get_task(id: int):
    for task in tasks_db:
        if task["id"] == id:
            return task
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {id} not found"
    )



@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED, summary="Create Task")
def create_task(payload: TaskCreate):
    # Validation: checks title is non-empty string
    clean_title = payload.title.strip()
    if not clean_title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty or whitespace"
        )
    
    new_task = {
        "id": get_next_id(),
        "title": clean_title,
        "done": False
    }
    tasks_db.append(new_task)
    return new_task

@app.put("/tasks/{id}", response_model=Task, summary="Update Task")
def update_task(id: int, payload: TaskUpdate):
    for task in tasks_db:
        if task["id"] == id:
            if payload.title is not None:
                clean_title = payload.title.strip()
                if not clean_title:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Title cannot be empty or whitespace"
                    )
                task["title"] = clean_title
            
            if payload.done is not None:
                task["done"] = payload.done

            return task

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {id} not found"
    )

@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Task")
def delete_task(id: int):
    for index, task in enumerate(tasks_db):
        if task["id"] == id:
            tasks_db.pop(index)
            return
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {id} not found"
    )