# Actual Project Architecture

## Repository layout

The repository has a Vite/React frontend under `frontend/` and a FastAPI backend under `backend/`. The frontend source is organized into app providers/router/store, feature folders, reusable components, pages, hooks, and API/WebSocket service helpers. The backend is the implemented HTTP surface documented in `docs/api.md`.

## Bootstrap and request lifecycle

`backend/app/main.py` creates `FastAPI(title="TeamDeck API")` and includes authentication, user, project, member, task, comment, notification, activity, and attachment routers. The attachment feature is mounted through both generic routes and the project/task/comment-scoped routers. There is no global API prefix.

For a request, FastAPI first resolves the route and its dependencies. The route dependencies can load the database session, authenticate the bearer token, and enforce role or resource access. The route then constructs a feature service. Services apply business rules and call repositories, which query or mutate SQLAlchemy models through the current session. Mutating routes generally commit after successful service work and roll back when they catch a service `ValueError`. Response models in `schemas/` serialize ORM objects through `from_attributes`.

## Authentication and authorization

`core/security.py` creates and decodes JWTs and hashes/verifies passwords. `dependencies/auth.py` uses `OAuth2PasswordBearer(tokenUrl="/auth/login")`; the token subject is interpreted as a user UUID. `get_current_user` rejects invalid tokens, unknown users, and inactive accounts. `require_admin`, `require_super_admin`, and `require_manager` add role checks.

The project, task, and comment dependency modules add resource checks. Project access is granted to admins, the owner, or a project member. Task access resolves the task and then checks its project. Comment access resolves the comment and task before checking the project. Modification dependencies additionally allow the relevant author/creator/owner or administrators. These dependencies are the main authorization boundary; services still enforce business invariants such as duplicate membership and valid task assignees.

## Services and repositories

Services in `backend/app/services/` coordinate models, repositories, and side effects. Authentication owns registration/login orchestration. User, project, member, task, comment, notification, attachment, task-attachment, activity, and file-storage services each cover their corresponding feature.

Repositories in `backend/app/repositories/` encapsulate SQLAlchemy reads and writes for users, projects, members, tasks, comments, attachments, task attachments, notifications, and activities. They add, flush, refresh, query, or delete; transaction boundaries are controlled by the route/session flow rather than by a repository-wide commit policy.

## Models and schemas

`backend/app/models/` contains the ORM entities for users, projects, memberships, tasks, comments, attachments, task attachments, notifications, activities, and enums. `backend/app/schemas/` contains request models such as `UserCreate`, `ProjectCreate`, `TaskCreate`, `CommentCreate`, and update variants, plus response models such as `UserResponse`, `ProjectResponse`, `TaskResponse`, `CommentResponse`, `AttachmentResponse`, `NotificationResponse`, and `ActivityResponse`. Activities and notifications have response schemas but no user-facing create schema because services generate them.

## Database, sessions, and migrations

`db/base.py` provides the declarative base. `db/session.py` creates the SQLAlchemy engine from `settings.DATABASE_URL`, configures `SessionLocal` with `autocommit=False` and `autoflush=False`, and exposes `get_db()` as a yield dependency that closes the session in `finally`. `backend/alembic/` contains migration configuration and revisions. The application itself does not commit from `get_db`; individual mutation routes commit after service calls.

## Files and side effects

Attachments use FastAPI `UploadFile` and `services/file_storage.py` for disk-backed storage under the configured `UPLOAD_DIR`. The attachment model stores metadata and a generated stored name; download routes return a `FileResponse` after checking access based on attachment kind.

State-changing project, membership, task, and comment services create `Activity` records through `ActivityService`. Several also create user notifications through `NotificationService`, including member changes, task assignment/update, and comment events. These side effects share the request's SQLAlchemy session and are committed with the surrounding route operation.

## Configuration

`core/config.py` loads settings from `.env` (first from the working directory, then from the backend-relative fallback). Required settings are `DATABASE_URL`, `UPLOAD_DIR`, and `JWT_SECRET_KEY`. `JWT_ALGORITHM` defaults to `HS256`, and `ACCESS_TOKEN_EXPIRE_MINUTES` defaults to `30`. `requirements.txt` files define the Python dependencies; the frontend has its own `package.json` and Vite configuration.

## Known implementation caveats

- The router set has no activity creation endpoint; activities are read-only over HTTP and are generated as side effects.
- Static routes such as `/users/me`, `/projects/owned`, `/projects/all`, `/tasks/assigned`, and `/notifications/unread` are declared before dynamic UUID routes and must remain ordered that way for unambiguous matching.
- The source uses both route-level `db.commit()`/`db.rollback()` and service-created side effects, so partial work is expected to be governed by the route's exception path and session transaction.
- Some route modules use inconsistent local names and formatting, but the mounted router objects and decorators define the actual public API.
- The frontend directory is a separate Vite/React application; this backend architecture document does not assume that every frontend feature is currently connected to every API route.
