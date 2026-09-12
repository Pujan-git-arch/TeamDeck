from fastapi import FastAPI

from app.db.session import engine
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.projects import router as projects_router
from app.routers.project_members import router as project_members_router
from app.routers.tasks import project_tasks_router, tasks_router
from app.routers.comments import task_comments_router, comments_router
from app.routers.notifications import router as notifications_router
from app.routers.activities import router as activities_router
from app.routers.attachments import (
    project_attachments_router,
    task_attachments_files_router,
    comment_attachments_router,
    attachments_router,
)
from app.routers.task_attachments import router as task_attachments_router


app = FastAPI(title="TeamDeck API")


# Auth + users
app.include_router(auth_router)
app.include_router(users_router)

# Projects and members
app.include_router(projects_router)
app.include_router(project_members_router)

# Tasks
app.include_router(project_tasks_router)
app.include_router(tasks_router)

# Comments
app.include_router(task_comments_router)
app.include_router(comments_router)

# Notifications + activities
app.include_router(notifications_router)
app.include_router(activities_router)

# Attachments
app.include_router(project_attachments_router)
app.include_router(task_attachments_files_router)
app.include_router(comment_attachments_router)
app.include_router(task_attachments_router)
app.include_router(attachments_router)