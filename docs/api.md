# Backend API Testing Reference

This reference is derived from `backend/app/main.py`, the router modules, their dependencies, and the Pydantic schemas. No API prefix is added by the application, so the default local base URL is `http://127.0.0.1:8000` (or the host and port used to run Uvicorn).

## Authentication

Register with `POST /auth/register` and JSON `{ "name": "Jane Doe", "email": "jane@example.com", "password": "Passw0rd!" }`. The response is `201` and a `UserResponse`. Login with `POST /auth/login` as form data, using `username` for the email and `password` for the password. The response is `200` and `{ "access_token": "...", "token_type": "bearer" }`.

Send the token on protected requests as `Authorization: Bearer <access_token>`. `get_current_user` rejects missing, malformed, unknown, or invalid tokens with `401`, and rejects accounts whose status is not `active` with `403`. Registration may therefore require an administrator to approve the account before login succeeds, depending on the model defaults and current data.

## Route reference

Unless noted, successful reads return `200`; list routes return a JSON array and object routes return the response schema named below. Successful create routes explicitly return `201`. Path parameters are UUIDs.

### Authentication and users

| Method and path | Access | Input and success response |
|---|---|---|
| `POST /auth/register` | Public | JSON `UserCreate`: `name` 2-120 chars, `email`, `password` 8-128 chars. `201`, `UserResponse`. Duplicate email is `400`. |
| `POST /auth/login` | Public | Form fields `username` (email) and `password`. `200`, `TokenResponse`. Invalid credentials or inactive account are `401`. |
| `GET /users/me` | Any active user | No input. `200`, `UserResponse`. |
| `GET /users/` | Admin or super_admin | No input. `200`, `list[UserResponse]`. |
| `GET /users/{user_id}` | Admin or super_admin | No body. `200`, `UserResponse`; missing user is `404`. |
| `PATCH /users/{user_id}` | Admin or super_admin | JSON `UserUpdate`: optional `name` and `email`. `200`, `UserResponse`; duplicate email or missing user is reported as a service error. |
| `PATCH /users/me/password` | Any active user | JSON `PasswordChange`: `current_password` and `new_password`, each 8-128 chars. `200`, `UserResponse`; incorrect current password is a service validation error. |
| `PATCH /users/{user_id}/approval` | Admin or super_admin | JSON `UserApproval`: `approved` and optional `rejection_reason`. `200`, `UserResponse`; missing user is `404`. |
| `DELETE /users/{user_id}` | Admin or super_admin | No body. The route's delete response/status is defined in `users.py`; test the actual status rather than assuming a JSON body. |

### Projects and members

| Method and path | Access | Input and success response |
|---|---|---|
| `POST /projects/` | Project creator dependency | JSON `ProjectCreate`: `name` 2-200 chars and optional `description`. `201`, `ProjectResponse`. The owner becomes a manager and a project activity is created. |
| `GET /projects/` | Authenticated user | No input. `200`, accessible `list[ProjectResponse]`. |
| `GET /projects/owned` | Authenticated user | No input. `200`, owner project list. |
| `GET /projects/all` | Admin or super_admin | No input. `200`, all project list. |
| `GET /projects/{project_id}` | Project access | No body. `200`, `ProjectResponse`; absent project is `404`, non-member access is `403`. |
| `PATCH /projects/{project_id}` | Project manager | JSON `ProjectUpdate`: optional `name`, `description`, `is_archived`. `200`, `ProjectResponse`. |
| `DELETE /projects/{project_id}` | Project manager | No body. Delete status is defined in `projects.py`; missing project is a service-level `404`. |
| `GET /projects/{project_id}/members/` | Project access | No input. `200`, `list[ProjectMemberResponse]`. |
| `POST /projects/{project_id}/members/` | Project manager | JSON `ProjectMemberCreate`: `user_id` and optional `role` (default `developer`). `201`, `ProjectMemberResponse`; project/user missing, inactive user, or duplicate membership is `400`. |
| `PATCH /projects/{project_id}/members/{user_id}` | Manager dependency | JSON `ProjectMemberUpdate`: required `role`. `200`, `ProjectMemberResponse`. |
| `DELETE /projects/{project_id}/members/{user_id}` | Manager dependency | No body. Delete status is defined in `project_members.py`; missing project/member is a service-level `404`. |

### Tasks

| Method and path | Access | Input and success response |
|---|---|---|
| `POST /projects/{project_id}/tasks/` | Task creator for project | JSON `TaskCreate`: `title` 3-120 chars, optional `description`, `assignee_id`, `due_date`, and `priority` (default `medium`, max 20). `201`, `TaskResponse`; an assignee must be a project member. |
| `GET /projects/{project_id}/tasks/` | Project access | No input. `200`, `list[TaskResponse]`. |
| `GET /tasks/assigned` | Authenticated user | No input. `200`, tasks assigned to the current user. |
| `GET /tasks/{task_id}` | Task access | No body. `200`, `TaskResponse`; missing task is `404`. |
| `PATCH /tasks/{task_id}` | Task creator, project owner, or admin | JSON `TaskUpdate`: optional title, description, assignee, priority, status, and due date. `200`, `TaskResponse`; a new assignee must be a member. |
| `DELETE /tasks/{task_id}` | Task creator, project owner, or admin | No body. Delete status is defined in `tasks.py`; missing task is `404`. |

### Comments

| Method and path | Access | Input and success response |
|---|---|---|
| `POST /tasks/{task_id}/comments/` | Task access | JSON `CommentCreate` with non-empty `body`. `201`, `CommentResponse`; missing task/project access fails. |
| `GET /tasks/{task_id}/comments/` | Task access | No input. `200`, `list[CommentResponse]`. |
| `GET /comments/{comment_id}` | Comment access | No body. `200`, `CommentResponse`; missing comment/task is `404`. |
| `PATCH /comments/{comment_id}` | Comment author, project owner, or admin | JSON `CommentUpdate` with non-empty `body`. `200`, `CommentResponse`. |
| `DELETE /comments/{comment_id}` | Comment author, project owner, or admin | No body. Delete status is defined in `comments.py`; missing comment is `404`. |

### Notifications and activities

| Method and path | Access | Input and success response |
|---|---|---|
| `GET /notifications/` | Authenticated user | No input. `200`, own `list[NotificationResponse]`. |
| `GET /notifications/unread` | Authenticated user | No input. `200`, own unread notification list. |
| `GET /notifications/{notification_id}` | Authenticated user | No body. `200`, `NotificationResponse`; missing is `404`, another user's notification is `403`. |
| `PATCH /notifications/{notification_id}/read` | Authenticated user | No body. `200`, updated `NotificationResponse`; ownership is checked by the router. |
| `DELETE /notifications/{notification_id}` | Authenticated user | No body. Delete status is defined in `notifications.py`; service lookup failure is `404`. |
| `GET /activities/project/{project_id}` | Project access | No input. `200`, `list[ActivityResponse]`. |
| `GET /activities/{activity_id}` | Admin or super_admin | No body. `200`, `ActivityResponse`; missing activity is `404`. |

There is no `POST /activities/`. Activity records are created by services as side effects of project, member, task, and comment operations.

### Attachments

| Method and path | Access | Input and success response |
|---|---|---|
| `GET /attachments/{attachment_id}/file` | Authenticated user plus access based on attachment kind | No body. Returns a `FileResponse`; missing file/attachment and denied access are errors handled by the router. |
| `GET /attachments/{attachment_id}` | Authenticated user | No body. `200`, `AttachmentResponse`. |
| `GET /attachments/project/{project_id}` | Project access | No input. `200`, attachment metadata list. |
| `GET /attachments/task/{task_id}` | Task access | No input. `200`, attachment metadata list. |
| `GET /attachments/comment/{comment_id}` | Comment access | No input. `200`, attachment metadata list. |
| `POST /attachments/upload` | Authenticated user and resource-specific access checks | Multipart form: `file` (`UploadFile`), `kind`, and optional `project_id`, `task_id`, `comment_id`. Returns `AttachmentResponse` on success; invalid kind/resource/access and storage errors are route errors. |
| `DELETE /attachments/{attachment_id}` | Authenticated user and resource-specific access checks | No body. Deletes metadata and stored file; status is defined in `attachments.py`. |
| `GET /projects/{project_id}/attachments/` | Project access | No input. `200`, `list[AttachmentResponse]`. |
| `GET /tasks/{task_id}/attachments/files/` | Task access | No input. `200`, `list[AttachmentResponse]`. |
| `GET /comments/{comment_id}/attachments/` | Comment access | No input. `200`, `list[AttachmentResponse]`. |

For upload tests, use `multipart/form-data`, provide a real small file, and send the IDs required by the selected kind. File bytes are stored under the configured `UPLOAD_DIR`; metadata contains original name, stored name, MIME type, size, kind, and optional resource IDs.

## Validation and route-ordering caveats

Pydantic validation failures are normally `422`. UUID path values must be valid UUID strings. Service `ValueError` exceptions are translated by routes to either `400` or `404`, depending on the operation. Authorization failures are normally `401` or `403`.

Static paths are intentionally declared before dynamic paths in several routers: `/users/me`, `/users/`, `/projects/owned`, `/projects/all`, `/tasks/assigned`, `/notifications/unread`, and the attachment subpaths must be tested as their literal routes rather than being mistaken for `{user_id}`, `{project_id}`, `{task_id}`, `{notification_id}`, or `{attachment_id}` values.

## Suggested end-to-end sequence

1. Register a user and confirm the `201` response and validation errors.
2. Approve the account as an administrator, then log in with form data and capture the bearer token.
3. Call `/users/me`, create a project, and verify the owner/member and project activity side effects.
4. Add an active user as a member, then create an assigned task and verify task/activity/notification responses.
5. Create, list, update, and delete a comment; verify access failures with a non-member token.
6. Exercise notification list, unread, read, ownership, and delete paths.
7. Upload an attachment with multipart data, list it through both generic and scoped routes, download the file, and delete it.
8. Read project activities as an authorized member and as an administrator; verify that no activity POST route exists.
