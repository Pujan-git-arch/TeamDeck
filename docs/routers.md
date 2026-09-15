# routers

Complete source catalog for backend/app/routers.

## backend/app/routers/__init__.py

```python
```


## backend/app/routers/activities.py

```python
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import (
    require_admin,
    require_project_access,
)
from app.models.user import User
from app.schemas.activity import ActivityResponse
from app.services.activity import ActivityService


router = APIRouter(
    prefix="/activities",
    tags=["Activities"],
)


# ---------------------------------------------------------
# GET PROJECT ACTIVITY
# ---------------------------------------------------------

@router.get(
    "/project/{project_id}",
    response_model=list[ActivityResponse],
)
def get_project_activity(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_project_access),
):
    service = ActivityService(db)

    return service.get_project_activity(project_id)


# ---------------------------------------------------------
# GET SINGLE ACTIVITY
# ---------------------------------------------------------

@router.get(
    "/{activity_id}",
    response_model=ActivityResponse,
)
def get_activity(
    activity_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    service = ActivityService(db)

    try:
        return service.get_activity(activity_id)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )

```


## backend/app/routers/attachments.py

```python
import uuid
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse

from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import (
    get_current_user,
    require_project_access,
    require_task_access,
    require_comment_access,
)
from app.models.attachment import Attachment
from app.models.user import User
from app.schemas.attachment import AttachmentResponse
from app.services.attachment import AttachmentService


router = APIRouter(
    prefix="/attachments",
    tags=["Attachments"],
)


@router.get("/{attachment_id}/file")
def get_attachment_file(
    attachment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AttachmentService(db)

    try:
        attachment = service.get_attachment(attachment_id)

        if attachment.kind == "project_cover":
            if attachment.project_id:
                require_project_access(
                    project_id=attachment.project_id,
                    db=db,
                    current_user=current_user,
                )

        elif attachment.kind == "task_attachment":
            if attachment.task_id:
                require_task_access(
                    task_id=attachment.task_id,
                    db=db,
                    current_user=current_user,
                )

        elif attachment.kind == "comment_attachment":
            if attachment.comment_id:
                require_comment_access(
                    comment_id=attachment.comment_id,
                    db=db,
                    current_user=current_user,
                )

        elif attachment.kind == "avatar":
            if (
                attachment.uploader_id != current_user.id
                and current_user.role not in {"admin", "super_admin"}
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to access this file",
                )

        file_path = service.get_file_path(attachment_id)

        return FileResponse(
            path=file_path,
            media_type=attachment.mime_type,
            filename=attachment.original_name,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
@router.get(
    "/{attachment_id}",
    response_model=AttachmentResponse,
)
def get_attachment(
    attachment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AttachmentService(db)

    try:
        return service.get_attachment(attachment_id)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )




@router.get(
    "/project/{project_id}",
    response_model=list[AttachmentResponse],
)
def get_project_attachments(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_project_access),
):
    service = AttachmentService(db)

    return service.get_project_attachments(project_id)


@router.get(
    "/task/{task_id}",
    response_model=list[AttachmentResponse],
)
def get_task_attachments(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_task_access),
):
    service = AttachmentService(db)

    return service.get_task_attachments(task_id)


@router.get(
    "/comment/{comment_id}",
    response_model=list[AttachmentResponse],
)
def get_comment_attachments(
    comment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_comment_access),
):
    service = AttachmentService(db)

    return service.get_comment_attachments(comment_id)


@router.post(
    "/upload",
    response_model=AttachmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_attachment(
    file: UploadFile = File(...),
    kind: str = Form(...),
    project_id: UUID | None = Form(None),
    task_id: UUID | None = Form(None),
    comment_id: UUID | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    valid_kinds = {
        "avatar",
        "project_cover",
        "task_attachment",
        "comment_attachment",
    }

    if kind not in valid_kinds:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid kind. Must be one of: {', '.join(valid_kinds)}",
        )


    # ---------------------------------------------------------
    # AVATAR
    # ---------------------------------------------------------

    if kind == "avatar":
        if project_id or task_id or comment_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Avatar attachments cannot belong to a project, task, or comment",
            )


    # ---------------------------------------------------------
    # PROJECT COVER
    # ---------------------------------------------------------

    elif kind == "project_cover":
        if not project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="project_id is required for project_cover attachments",
            )

        if task_id or comment_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project cover attachments cannot belong to a task or comment",
            )

        require_project_access(
            project_id=project_id,
            db=db,
            current_user=current_user,
        )


    # ---------------------------------------------------------
    # TASK ATTACHMENT
    # ---------------------------------------------------------

    elif kind == "task_attachment":
        if not task_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="task_id is required for task_attachment attachments",
            )

        if project_id or comment_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task attachments cannot directly belong to a project or comment",
            )

        require_task_access(
            task_id=task_id,
            db=db,
            current_user=current_user,
        )


    # ---------------------------------------------------------
    # COMMENT ATTACHMENT
    # ---------------------------------------------------------

    elif kind == "comment_attachment":
        if not comment_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="comment_id is required for comment_attachment attachments",
            )

        if project_id or task_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Comment attachments cannot belong to a project or task",
            )

        require_comment_access(
            comment_id=comment_id,
            db=db,
            current_user=current_user,
        )

    service = AttachmentService(db)

    try:
        import uuid as uuid_lib

        stored_name = f"{uuid_lib.uuid4()}_{file.filename}"
        
        file.file.seek(0)
        
        file_path = service.file_storage.save_file(
            file,
            stored_name,
        )
        size_bytes = file_path.stat().st_size

        attachment = Attachment(
            uploader_id=current_user.id,
            project_id=project_id,
            task_id=task_id,
            comment_id=comment_id,
            original_name=file.filename,
            stored_name=stored_name,
            mime_type=file.content_type or "application/octet-stream",
            size_bytes=size_bytes,
            kind=kind,
        )

        attachment = service.create_attachment(attachment)

        db.commit()

        return attachment

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.delete(
    "/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_attachment(
    attachment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AttachmentService(db)

    try:
        attachment = service.get_attachment(attachment_id)

        if (
            attachment.uploader_id != current_user.id
            and current_user.role not in {"admin", "super_admin"}
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this attachment",
            )

        service.delete_attachment(attachment_id)

        db.commit()

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
```


## backend/app/routers/auth.py

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.db.session import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.services.auth import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    service = AuthService(db)
    
    try:
        user = service.register_user(user_data)
        db.commit()
        return user
    
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
        
        
@router.post("/login",
             response_model=TokenResponse,
             )
def login(
    form_data: OAuth2PasswordRequestForm=Depends(),
    
    db: Session = Depends(get_db),
):
    service= AuthService(db)
    
    login_data = UserLogin(
        email=form_data.username,
        password=form_data.password,
    )
    
    try:
        access_token = service.authenticate_user(login_data)
        
        return{
            "access_token": access_token,
            "token_type": "bearer",
        }
    
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
            headers={"WWW-Authenticate":"Bearer"}
        )
```


## backend/app/routers/comments.py

```python
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import (
    require_task_access,
    require_comment_access,
    require_comment_author,
)
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from app.services.comment import CommentService


# Task-scoped comment routes: /tasks/{task_id}/comments
task_comments_router = APIRouter(
    prefix="/tasks/{task_id}/comments",
    tags=["Comments"],
)

# Comment-scoped routes: /comments
comments_router = APIRouter(
    prefix="/comments",
    tags=["Comments"],
)


# ---------------------------------------------------------
# TASK-SCOPED: CREATE COMMENT
# ---------------------------------------------------------

@task_comments_router.post(
    "/",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    task_id: UUID,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_task_access),
):
    service = CommentService(db)

    try:
        comment = service.create_comment(
            task_id=task_id,
            actor_id=current_user.id,
            comment_data=comment_data,
        )

        db.commit()

        return comment

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


# ---------------------------------------------------------
# TASK-SCOPED: LIST COMMENTS
# ---------------------------------------------------------

@task_comments_router.get(
    "/",
    response_model=list[CommentResponse],
)
def get_task_comments(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_task_access),
):
    service = CommentService(db)

    return service.get_task_comments(task_id)


# ---------------------------------------------------------
# COMMENT-SCOPED: GET ONE
# ---------------------------------------------------------

@comments_router.get(
    "/{comment_id}",
    response_model=CommentResponse,
)
def get_comment(
    comment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_comment_access),
):
    service = CommentService(db)

    try:
        return service.get_comment(comment_id)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


# ---------------------------------------------------------
# COMMENT-SCOPED: UPDATE
# ---------------------------------------------------------

@comments_router.patch(
    "/{comment_id}",
    response_model=CommentResponse,
)
def update_comment(
    comment_id: UUID,
    comment_data: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_comment_author),
):
    service = CommentService(db)

    try:
        comment = service.update_comment(
            comment_id=comment_id,
            comment_data=comment_data,
            actor_id=current_user.id,
            
        )

        db.commit()

        return comment

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


# ---------------------------------------------------------
# COMMENT-SCOPED: DELETE
# ---------------------------------------------------------

@comments_router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_comment(
    comment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_comment_author),
):
    service = CommentService(db)

    try:
        service.delete_comment(comment_id,
                               current_user.id
                               )

        db.commit()

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


__all__ = ["task_comments_router", "comments_router"]
```


## backend/app/routers/notifications.py

```python
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.services.notification import NotificationService


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


# ---------------------------------------------------------
# GET MY NOTIFICATIONS
# ---------------------------------------------------------

@router.get(
    "/",
    response_model=list[NotificationResponse],
)
def get_my_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = NotificationService(db)

    return service.get_user_notifications(current_user.id)


# ---------------------------------------------------------
# GET MY UNREAD NOTIFICATIONS
# ---------------------------------------------------------

@router.get(
    "/unread",
    response_model=list[NotificationResponse],
)
def get_my_unread_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = NotificationService(db)

    return service.get_unread_notifications(current_user.id)


# ---------------------------------------------------------
# GET SINGLE NOTIFICATION
# ---------------------------------------------------------

@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
)
def get_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = NotificationService(db)

    try:
        notification = service.get_notification(notification_id)

        if notification.recipient_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this notification",
            )

        return notification

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


# ---------------------------------------------------------
# MARK NOTIFICATION AS READ
# ---------------------------------------------------------

@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
def mark_notification_as_read(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = NotificationService(db)

    try:
        notification = service.get_notification(notification_id)

        if notification.recipient_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this notification",
            )

        notification = service.mark_as_read(notification_id)

        db.commit()

        return notification

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


# ---------------------------------------------------------
# DELETE NOTIFICATION
# ---------------------------------------------------------

@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = NotificationService(db)

    try:
        notification = service.get_notification(notification_id)

        if notification.recipient_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this notification",
            )

        service.delete_notification(notification_id)

        db.commit()

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
```


## backend/app/routers/project_members.py

```python
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import(
    require_project_access,
    require_project_manager,
    require_manager,
)
from app.models.user import User
from app.schemas.project_member import(
    ProjectMemberCreate,
    ProjectMemberResponse,
    ProjectMemberUpdate,
)
from app.services.project_member import ProjectMemberService

router = APIRouter(
    prefix="/projects/{project_id}/members",
    tags=["Project Members"],
)

@router.get(
    "/",
    response_model= list[ProjectMemberResponse],
)
def get_project_membres(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_User: User = Depends(require_project_access),
):
    service = ProjectMemberService(db)
    
    return service.get_project_members(
        project_id
    )
    
    
@router.post(
    "/",
    response_model=ProjectMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_project_member(
    project_id:UUID,
    member_data: ProjectMemberCreate,
    db:Session =Depends(get_db),
    current_user:User = Depends(require_project_manager),
):
    service = ProjectMemberService(db)
    
    try:
        member = service.add_member(
            project_id,
            member_data,
            current_user.id,
        )
        
        db.commit()
        
        return member
    
    except ValueError as error:
        db.rollback()
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
        

@router.patch(
    "/{user_id}",
    response_model=ProjectMemberResponse,
)
def update_project_member(
    project_id: UUID,
    user_id: UUID,
    member_data: ProjectMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_project_manager),
):
    service = ProjectMemberService(db)
    
    try:
        member = service.update_member(
            project_id,
            user_id,
            member_data,
            current_user.id,
        )

        db.commit()

        return member

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )

    
  
@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_project_member(
    project_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_project_manager),
):
    service = ProjectMemberService(db)

    try:
        service.remove_member(
            project_id,
            user_id,
            current_user.id,
        )

        db.commit()

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
```


## backend/app/routers/projects.py

```python
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import (
    require_manager,
    require_admin,
    get_current_user,
    require_project_access,
    require_project_manager,
    require_project_creator,
)
from app.models.user import User
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
from app.services.project import ProjectService


router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


# ---------------------------------------------------------
# CREATE PROJECT
# ---------------------------------------------------------

@router.post(
    "/",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_project_creator),
):
    service = ProjectService(db)

    try:
        project = service.create_project(
            current_user.id,
            project_data,
        )

        db.commit()

        return project

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


# ---------------------------------------------------------
# GET MY PROJECTS
# ---------------------------------------------------------

@router.get(
    "/",
    response_model=list[ProjectResponse],
)
def get_my_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProjectService(db)
    return service.get_user_accessible_projects(current_user.id)

# ---------------------------------------------------------
# GET MY OWNED PROJECTS
# ---------------------------------------------------------

@router.get(
    "/owned",
    response_model=list[ProjectResponse],
)
def get_my_owned_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProjectService(db)

    return service.get_user_projects(
        current_user.id,
    )
# ---------------------------------------------------------
# GET ALL PROJECTS
# ---------------------------------------------------------

@router.get(
    "/all",
    response_model=list[ProjectResponse],
)
def get_all_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    service = ProjectService(db)

    return service.get_all_projects()


# ---------------------------------------------------------
# GET SINGLE PROJECT
# ---------------------------------------------------------

@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_project_access),
):
    service = ProjectService(db)

    try:
        return service.get_project(
            project_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


# ---------------------------------------------------------
# UPDATE PROJECT
# ---------------------------------------------------------

@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
)
def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_project_manager),
):
    service = ProjectService(db)

    try:
        project = service.update_project(
            project_id,
            project_data,
        )

        db.commit()

        return project

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


# ---------------------------------------------------------
# DELETE PROJECT
# ---------------------------------------------------------

@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_project_manager),
):
    service = ProjectService(db)

    try:
        service.delete_project(
            project_id
        )

        db.commit()

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
        
```


## backend/app/routers/task_attachments.py

```python
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import (
    get_current_user,
    require_project_access,
    require_task_access,
    require_comment_access,
)
from app.models.attachment import Attachment
from app.models.user import User
from app.schemas.attachment import AttachmentResponse
from app.services.attachment import AttachmentService


# Parent-scoped listing routers
project_attachments_router = APIRouter(
    prefix="/projects/{project_id}/attachments",
    tags=["Attachments"],
)

task_attachments_files_router = APIRouter(
    prefix="/tasks/{task_id}/attachments/files",
    tags=["Attachments"],
)

comment_attachments_router = APIRouter(
    prefix="/comments/{comment_id}/attachments",
    tags=["Attachments"],
)



# ---------------------------------------------------------
# PROJECT-SCOPED: LIST ATTACHMENT FILES
# ---------------------------------------------------------

@project_attachments_router.get(
    "/",
    response_model=list[AttachmentResponse],
)
def get_project_attachments(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_project_access),
):
    service = AttachmentService(db)

    return service.get_project_attachments(project_id)


# ---------------------------------------------------------
# TASK-SCOPED: LIST ATTACHMENT FILES
# ---------------------------------------------------------

@task_attachments_files_router.get(
    "/",
    response_model=list[AttachmentResponse],
)
def get_task_attachment_files(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_task_access),
):
    service = AttachmentService(db)

    return service.get_task_attachments(task_id)


# ---------------------------------------------------------
# COMMENT-SCOPED: LIST ATTACHMENT FILES
# ---------------------------------------------------------

@comment_attachments_router.get(
    "/",
    response_model=list[AttachmentResponse],
)
def get_comment_attachments(
    comment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_comment_access),
):
    service = AttachmentService(db)

    return service.get_comment_attachments(comment_id)



__all__ = [
    "project_attachments_router",
    "task_attachments_files_router",
    "comment_attachments_router",
    
]
```


## backend/app/routers/tasks.py

```python
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import (
    get_current_user,
    require_project_access,
    require_task_access,
    require_task_creator,
    require_task_creator_for_project,
)
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.task import TaskService


# Project-scoped task routes: /projects/{project_id}/tasks
project_tasks_router = APIRouter(
    prefix="/projects/{project_id}/tasks",
    tags=["Tasks"],
)

# Task-scoped routes: /tasks
tasks_router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


# ---------------------------------------------------------
# PROJECT-SCOPED: CREATE TASK
# ---------------------------------------------------------

@project_tasks_router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    project_id: UUID,
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_task_creator_for_project),
):
    service = TaskService(db)

    try:
        task = service.create_task(
            project_id=project_id,
            actor_id=current_user.id,
            task_data=task_data,
        )

        db.commit()

        return task

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


# ---------------------------------------------------------
# PROJECT-SCOPED: LIST TASKS
# ---------------------------------------------------------

@project_tasks_router.get(
    "/",
    response_model=list[TaskResponse],
)
def get_project_tasks(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_project_access),
):
    service = TaskService(db)

    return service.get_project_tasks(project_id)


# ---------------------------------------------------------
# TASK-SCOPED: MY ASSIGNED TASKS
# ---------------------------------------------------------
# Literal route BEFORE dynamic route.

@tasks_router.get(
    "/assigned",
    response_model=list[TaskResponse],
)
def get_assigned_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TaskService(db)

    return service.get_assigned_tasks(current_user.id)


# ---------------------------------------------------------
# TASK-SCOPED: GET ONE TASK
# ---------------------------------------------------------

@tasks_router.get(
    "/{task_id}",
    response_model=TaskResponse,
)
def get_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_task_access),
):
    service = TaskService(db)

    try:
        return service.get_task(task_id)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


# ---------------------------------------------------------
# TASK-SCOPED: UPDATE TASK
# ---------------------------------------------------------

@tasks_router.patch(
    "/{task_id}",
    response_model=TaskResponse,
)
def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_task_creator),
):
    service = TaskService(db)

    try:
        task = service.update_task(
            task_id=task_id,
            task_data=task_data,
            actor_id=current_user.id,
        )

        db.commit()

        return task

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


# ---------------------------------------------------------
# TASK-SCOPED: DELETE TASK
# ---------------------------------------------------------

@tasks_router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_task_creator),
):
    service = TaskService(db)

    try:
        service.delete_task(task_id,
                            current_user.id)

        db.commit()

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


__all__ = ["project_tasks_router", "tasks_router"]
```


## backend/app/routers/users.py

```python
from uuid  import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user, require_admin
from app.models.user import User
from app.schemas.user import(
    PasswordChange,
    UserApproval,
    UserResponse,
    UserUpdate
)
from app.services.user import UserService

router= APIRouter(
    prefix="/users",
    tags=["Users"],
)

@router.get(
    "/me",
    response_model=UserResponse,
)
def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user



@router.get(
    "/",
    response_model=list[UserResponse],
)
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    service = UserService(db)
    
    return service.get_all_users()


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    service = UserService(db)
    
    try:
        return service.get_user(user_id)
    
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )
        
@router.patch(
    "/{user_id}",
    response_model=UserResponse
)
def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db:Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    service = UserService(db)
    
    try:
        user= service.update_user(
            user_id,
            user_data,    
        )
        
        db.commit()
        
        return user
    
    except ValueError as error:
        db.rollback()
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
            )
        
        
        
@router.patch(
    "/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
)
def change_password(
    password_data: PasswordChange,
    db:Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service= UserService(db)
    
    try:
        service.change_password(
            current_user.id,
            password_data,
        )
        
        db.commit()
    
    except ValueError as error:
        db.rollback()
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )
      
        
@router.patch(
    "/{user_id}/approval",
    response_model=UserResponse,
)
def approve_user(
    user_id: UUID,
    approval_data: UserApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    service = UserService(db)

    try:
        user = service.approve_or_reject_user(
            user_id,
            current_user.id,
            approval_data,
        )

        db.commit()

        return user

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
    
    
@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    service = UserService(db)

    try:
        service.delete_user(
            user_id,
        )

        db.commit()

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
```


