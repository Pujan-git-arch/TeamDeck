# Architecture Overview

This document explains the current backend architecture for TeamDeck and how the major layers fit together.

## High-Level Structure

The backend follows a typical layered FastAPI pattern:

- `app/main.py` bootstraps the FastAPI application and registers routers.
- `app/routers/` contains HTTP route handlers.
- `app/dependencies/` contains shared auth and authorization checks.
- `app/services/` contains business logic and validation rules.
- `app/repositories/` contains SQLAlchemy queries and persistence logic.
- `app/models/` defines the database schema as SQLAlchemy models.
- `app/schemas/` defines request and response contracts with Pydantic.
- `app/db/` configures the database engine and session dependency.

## Request Flow

A typical request moves through the stack like this:

1. FastAPI receives the HTTP request.
2. The matching router function runs.
3. Dependencies such as `get_current_user()` or `require_project_access()` validate authentication and permissions.
4. The route calls a service class.
5. The service uses a repository object to query or persist data.
6. The repository interacts with the SQLAlchemy `Session` and model layer.
7. The route commits or rolls back the transaction, then returns a response.

## Main Layers

### Router Layer

The router layer is located in `backend/app/routers/` and exposes endpoints grouped by feature.

Examples:

- `auth.py` for login and registration
- `users.py` for account and admin management
- `projects.py` for project lifecycle routes
- `project_members.py` for membership assignment
- `tasks.py` for project-scoped and task-scoped task operations
- `comments.py` for task-scoped and comment-scoped comment operations
- `notifications.py` and `activities.py` for user/project activity flows
- `task_attachments.py` for multiple attachment-scoped listing/upload/delete routers

### Dependency Layer

The dependency layer centralizes permission checks.

Current dependencies include:

- `get_current_user()`
- `require_admin()`
- `require_super_admin()`
- `require_manager()`
- `require_project_access()`
- `require_project_manager()`
- `require_project_creator()`

This keeps route logic shorter and makes access rules reusable.

### Service Layer

The service layer holds the application rules that are not database-specific.

Examples:

- `AuthService` handles registration and token generation.
- `UserService` handles account updates, approvals, and password changes.
- `ProjectService` handles project creation, update, listing, and ownership logic.
- `ProjectMemberService` handles membership creation and role updates.

### Repository Layer

Repositories handle database queries and persistence operations for each model.

Examples:

- `ProjectRepository` queries project records.
- `ProjectMemberRepository` queries project membership records.
- `UserRepository` queries users by email and ID.
- `NotificationRepository` handles unread and recipient-based queries.

### Model and Schema Layer

- `models/` defines the database schema using SQLAlchemy.
- `schemas/` defines the API contracts with Pydantic.
- Database models and Pydantic models are intentionally kept separate so validation is independent from persistence.

## Database and Session Configuration

The database configuration is defined in:

- `backend/app/core/config.py` for environment settings
- `backend/app/db/session.py` for engine and session creation

The app uses a single PostgreSQL connection string from environment configuration and creates a session per request through `get_db()`.

## Current State of the Project

The current backend is a working feature-oriented API with the following core flows already in place:

- user authentication and registration
- user approval management
- project creation and ownership
- project member assignment
- project access control
- task creation, listing, assignment, update, and deletion
- comment creation, listing, update, and deletion
- notifications
- activities
- attachments and project/task/comment attachment listings

The task and comment modules are active and mounted through multiple scoped routers rather than a single flat router file. The attachment module similarly exposes several scoped router instances for project, task, and comment attachment listing.

## Architectural Notes

- The system is organized around domain features rather than a strict hexagonal architecture.
- Permission checks are centralized in dependencies instead of being duplicated across routes.
- Repositories are thin and strongly tied to the SQLAlchemy model layer.
- The service layer sits in the middle, coordinating model creation and validation before persistence.
