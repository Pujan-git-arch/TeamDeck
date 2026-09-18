# Model Reference

This file summarizes the SQLAlchemy models in `backend/app/models/` and reflects the actual database schema currently in the project.

## 1. Model overview

| Model | Table | Purpose |
| --- | --- | --- |
| `User` | `users` | Authenticated user account and approval state |
| `Project` | `projects` | Project workspace owned by a user |
| `ProjectMember` | `project_members` | Membership of a user in a project |
| `Task` | `tasks` | Project work item |
| `Comment` | `comments` | Comment attached to a task |
| `Attachment` | `attachments` | Uploaded file metadata |
| `TaskAttachment` | `task_attachments` | Join table between tasks and attachments |
| `Activity` | `activity` | Event log for project actions |
| `Notification` | `notifications` | User notification records |

## 2. PostgreSQL enums

Database enums are defined in `backend/app/models/enums.py`:

- `account_status_enum`: `pending`, `active`, `rejected`, `suspended`
- `user_role_enum`: `super_admin`, `admin`, `manager`, `developer`, `designer`, `hr`, `qa_tester`, `viewer`
- `task_status_enum`: `todo`, `in_progress`, `review`, `done`
- `task_priority_enum`: `low`, `medium`, `high`, `urgent`
- `attachment_kind_enum`: `avatar`, `project_cover`, `task_attachment`, `comment_attachment`

## 3. `User`

Table: `users`

Fields:

- `id: UUID` primary key, default `uuid.uuid4()`
- `name: String(120)` required
- `email: String(255)` required, unique
- `password_hash: String(255)` required
- `role: user_role_enum` default `viewer`
- `account_status: account_status_enum` default `pending`
- `rejection_reason: Text | None`
- `avatar_attachment_id: UUID | None` foreign key to `attachments.id` with `SET NULL`
- `requested_at: DateTime(timezone=True)` server default `CURRENT_TIMESTAMP`
- `approved_by: UUID | None` self-reference to `users.id`
- `approved_at: DateTime | None`
- `created_at: DateTime(timezone=True)` default `CURRENT_TIMESTAMP`
- `updated_at: DateTime(timezone=True)` default `CURRENT_TIMESTAMP`

Relationships:

- `approver: User | None`
- `avatar: Attachment | None`

## 4. `Project`

Table: `projects`

Fields:

- `id: UUID` primary key
- `owner_id: UUID` required, FK to `users.id`, `ondelete="RESTRICT"`
- `name: String(150)` required
- `description: Text | None`
- `cover_attachment_id: UUID | None` FK to `attachments.id` with `SET NULL`
- `is_archived: Boolean` default `False`
- `created_at: DateTime(timezone=True)` default `CURRENT_TIMESTAMP`
- `updated_at: DateTime(timezone=True)` default `CURRENT_TIMESTAMP`, `onupdate` set to `CURRENT_TIMESTAMP`

Relationships:

- `owner: User`
- `cover: Attachment | None`

## 5. `ProjectMember`

Table: `project_members`

Composite primary key:

- `project_id: UUID`
- `user_id: UUID`

Fields:

- `role: user_role_enum` default `developer`
- `joined_at: DateTime(timezone=True)` default `CURRENT_TIMESTAMP`

Relationships:

- `project: Project`
- `user: User`

## 6. `Task`

Table: `tasks`

Fields:

- `id: UUID` primary key
- `project_id: UUID` FK to `projects.id`, `ondelete="CASCADE"`
- `assignee_id: UUID | None` FK to `users.id`, `ondelete="SET NULL"`
- `created_by_id: UUID` FK to `users.id`, `ondelete="RESTRICT"`
- `title: String(200)` required
- `description: Text | None`
- `status: task_status_enum` default `todo`
- `priority: task_priority_enum` default `medium`
- `due_date: DateTime | None`
- `created_at: DateTime(timezone=True)` default `CURRENT_TIMESTAMP`
- `updated_at: DateTime(timezone=True)` default `CURRENT_TIMESTAMP`, `onupdate` set to `CURRENT_TIMESTAMP`

Indexes:

- `idx_tasks_project_status` on `(project_id, status)`

Relationships:

- `project: Project`
- `assignee: User | None`
- `creator: User`

## 7. `Comment`

Table: `comments`

Fields:

- `id: UUID` primary key
- `task_id: UUID` FK to `tasks.id`, `ondelete="CASCADE"`
- `author_id: UUID` FK to `users.id`, `ondelete="CASCADE"`
- `body: Text` required
- `created_at: DateTime(timezone=True)` default `CURRENT_TIMESTAMP`
- `updated_at: DateTime(timezone=True)` default `CURRENT_TIMESTAMP`, `onupdate` set to `CURRENT_TIMESTAMP`

Index:

- `idx_comments_task_id` on `(task_id, created_at)`

Relationships:

- `task: Task`
- `author: User`

## 8. `Attachment`

Table: `attachments`

Fields:

- `id: UUID` primary key
- `uploader_id: UUID` FK to `users.id`, `ondelete="CASCADE"`
- `project_id: UUID | None` FK to `projects.id`, `ondelete="CASCADE"`
- `task_id: UUID | None` FK to `tasks.id`, `ondelete="CASCADE"`
- `comment_id: UUID | None` FK to `comments.id`, `ondelete="CASCADE"`
- `original_name: String(255)` required
- `stored_name: String(255)` required
- `mime_type: String(100)` required
- `size_bytes: Integer` required
- `kind: attachment_kind_enum` required
- `created_at: DateTime(timezone=True)` default `CURRENT_TIMESTAMP`

Indexes:

- `idx_attachments_uploader`
- `idx_attachments_project`
- `idx_attachments_task`
- `idx_attachments_comment`

Relationships:

- `uploader: User`
- `project: Project | None`
- `task: Task | None`
- `comment: Comment | None`

## 9. `TaskAttachment`

Table: `task_attachments`

Composite primary key:

- `task_id: UUID` FK to `tasks.id`, `ondelete="CASCADE"`
- `attachment_id: UUID` FK to `attachments.id`, `ondelete="CASCADE"`

This table prevents duplicate attachments on the same task.

## 10. `Activity`

Table: `activity`

Fields:

- `id: UUID` primary key
- `project_id: UUID | None` FK to `projects.id`, `ondelete="CASCADE"`
- `actor_id: UUID` FK to `users.id`, `ondelete="CASCADE"`
- `action: String(100)` required
- `entity_type: String(50)` required
- `entity_id: UUID` required
- `extra_data: JSONB` mapped to the database column name `metadata`, default `'{}'::jsonb`
- `created_at: DateTime(timezone=True)` default `CURRENT_TIMESTAMP`

Index:

- `idx_activity_project_id` on `(project_id, created_at DESC)`

Relationships:

- `project: Project | None`
- `actor: User`

## 11. `Notification`

Table: `notifications`

Fields:

- `id: UUID` primary key
- `recipient_id: UUID` FK to `users.id`, `ondelete="CASCADE"`
- `type: String(50)` required
- `message: Text` required
- `entity_type: String(50)` required
- `entity_id: UUID` required
- `read_at: DateTime | None`
- `created_at: DateTime(timezone=True)` default `CURRENT_TIMESTAMP`

Index:

- `idx_notifications_recipient` on `(recipient_id, read_at)`

Relationship:

- `recipient: User`

## 12. Relationship summary

```text
User 1---* Project             (owner)
User *---* Project             (through ProjectMember)
Project 1---* Task
User 1---* Task                (assignee, creator)
Task 1---* Comment
User 1---* Comment             (author)
User 1---* Attachment          (uploader)
Task *---* Attachment          (through TaskAttachment)
Project 1---* Activity
User 1---* Activity            (actor)
User 1---* Notification        (recipient)
```

## 13. Notes

- `Activity.entity_id` and `Notification.entity_id` are application-level polymorphic references rather than strict foreign keys.
- `User` has a deferred FK alias for `avatar_attachment_id` (`fk_users_avatar`) and `Project` has a similar alias for `cover_attachment_id` (`fk_projects_cover`).
- The implementation uses table names and field names directly from the current ORM model definitions rather than a separate migration-only layer.

### `__init__.py`

```python
```

### `enums.py`

```python
from sqlalchemy.dialects.postgresql import ENUM

# ===== ACCOUNT STATUS ENUM =====
account_status_enum = ENUM(
	"pending",
	"active",
	"rejected",
	"suspended",
	name="account_status_enum",
	create_type=False,
)

# ===== USER ROLE ENUM =====
user_role_enum = ENUM(
	"super_admin",
	"admin",
	"manager",
	"developer",
	"designer",
	"hr",
	"qa_tester",
	"viewer",
	name="user_role_enum",
	create_type=False,
)

# ===== TASK STATUS ENUM =====
task_status_enum = ENUM(
	"todo",
	"in_progress",
	"review",
	"done",
	name="task_status_enum",
	create_type=False,
)

# ===== TASK PRIORITY ENUM =====
task_priority_enum = ENUM(
	"low",
	"medium",
	"high",
	"urgent",
	name="task_priority_enum",
	create_type=False,
)

# ===== ATTACHMENT KIND ENUM =====
attachment_kind_enum = ENUM(
	"avatar",
	"project_cover",
	"task_attachment",
	"comment_attachment",
	name="attachment_kind_enum",
	create_type=False,
)
```

### `user.py`

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from app.models.user import User
	from app.models.attachment import Attachment


import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import user_role_enum, account_status_enum


class User(Base):
	__tablename__ = "users"

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		primary_key=True,
		default=uuid.uuid4,
	)

	name: Mapped[str] = mapped_column(
		String(120),
		nullable=False,
	)

	email: Mapped[str] = mapped_column(
		String(255),
		nullable=False,
		unique=True,
	)

	password_hash: Mapped[str] = mapped_column(
		String(255),
		nullable=False,
	)

	role: Mapped[str] = mapped_column(
		user_role_enum,
		nullable=False,
		default="viewer",
		index=True,
	)

	account_status: Mapped[str] = mapped_column(
		account_status_enum,
		nullable=False,
		default="pending",
		index=True,
	)

	rejection_reason: Mapped[str | None] = mapped_column(
		Text,
		nullable=True,
	)

	avatar_attachment_id: Mapped[uuid.UUID | None] = mapped_column(
		UUID(as_uuid=True),
		ForeignKey(
			"attachments.id",
			ondelete="SET NULL",
			use_alter=True,
			name="fk_users_avatar",
		),
		nullable=True,
	)

	requested_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		server_default=text("CURRENT_TIMESTAMP"),
		nullable=False,
	)

	approved_by: Mapped[uuid.UUID | None] = mapped_column(
		UUID(as_uuid=True),
		ForeignKey("users.id", ondelete="SET NULL"),
		nullable=True,
	)

	approved_at: Mapped[datetime | None] = mapped_column(
		DateTime(timezone=True),
		nullable=True,
	)

	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		server_default=text("CURRENT_TIMESTAMP"),
		nullable=False,
	)

	updated_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		server_default=text("CURRENT_TIMESTAMP"),
		nullable=False,
	)

	approver: Mapped[User | None] = relationship(
		"User",
		remote_side="User.id",
		foreign_keys=[approved_by],
	)

	avatar: Mapped[Attachment | None] = relationship(
		"Attachment",
		foreign_keys=[avatar_attachment_id],
	)
```

### `project.py`

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from app.models.user import User
	from app.models.attachment import Attachment

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Project(Base):
	__tablename__ = "projects"

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		primary_key=True,
		default=uuid.uuid4,
	)

	owner_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		ForeignKey("users.id", ondelete="RESTRICT"),
		nullable=False,
		index=True,
	)

	name: Mapped[str] = mapped_column(
		String(150),
		nullable=False,
	)

	description: Mapped[str | None] = mapped_column(
		Text,
		nullable=True,
	)

	cover_attachment_id: Mapped[uuid.UUID | None] = mapped_column(
		UUID(as_uuid=True),
		ForeignKey(
			"attachments.id",
			ondelete="SET NULL",
			use_alter=True,
			name="fk_projects_cover",
		),
		nullable=True,
	)

	is_archived: Mapped[bool] = mapped_column(
		Boolean,
		nullable=False,
		default=False,
	)

	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		server_default=text("CURRENT_TIMESTAMP"),
		nullable=False,
	)

	updated_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		server_default=text("CURRENT_TIMESTAMP"),
		onupdate=text("CURRENT_TIMESTAMP"),
		nullable=False,
	)

	owner: Mapped[User] = relationship(
		"User",
		foreign_keys=[owner_id],
	)

	cover: Mapped[Attachment | None] = relationship(
		"Attachment",
		foreign_keys=[cover_attachment_id],
	)
```

### `project_member.py`

```python
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.enums import user_role_enum
from app.models.user import User
from app.models.project import Project


class ProjectMember(Base):
	__tablename__ = "project_members"

	project_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		ForeignKey("projects.id", ondelete="CASCADE"),
		primary_key=True,
		nullable=False,
		# No separate index needed: project_id is the leading column of the
		# composite PK, so it's already indexed for lookups on this column alone.
	)

	user_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		ForeignKey("users.id", ondelete="CASCADE"),
		primary_key=True,
		nullable=False,
		index=True,  # idx_project_members_user — needed since user_id isn't the PK's leading column
	)

	role: Mapped[str] = mapped_column(
		user_role_enum,
		nullable=False,
		default="developer",
	)

	joined_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		server_default=text("CURRENT_TIMESTAMP"),
		nullable=False,
	)

	project: Mapped["Project"] = relationship(
		"Project",
		foreign_keys=[project_id],
	)

	user: Mapped["User"] = relationship(
		"User",
		foreign_keys=[user_id],
	)
```

### `task.py`

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from app.models.user import User
	from app.models.project import Project


import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.enums import task_status_enum, task_priority_enum


class Task(Base):
	__tablename__ = "tasks"

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		primary_key=True,
		default=uuid.uuid4,
	)

	project_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		ForeignKey("projects.id", ondelete="CASCADE"),
		nullable=False,
		index=True,
	)

	assignee_id: Mapped[uuid.UUID | None] = mapped_column(
		UUID(as_uuid=True),
		ForeignKey("users.id", ondelete="SET NULL"),
		nullable=True,
		index=True,
	)

	created_by_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		ForeignKey("users.id", ondelete="RESTRICT"),
		nullable=False,
	)

	title: Mapped[str] = mapped_column(
		String(200),
		nullable=False,
	)

	description: Mapped[str | None] = mapped_column(
		Text,
		nullable=True,
	)

	status: Mapped[str] = mapped_column(
		task_status_enum,
		nullable=False,
		default="todo",
	)

	priority: Mapped[str] = mapped_column(
		task_priority_enum,
		nullable=False,
		default="medium",
	)

	due_date: Mapped[datetime | None] = mapped_column(
		DateTime(timezone=True),
		nullable=True,
	)

	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		server_default=text("CURRENT_TIMESTAMP"),
		nullable=False,
	)

	updated_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		server_default=text("CURRENT_TIMESTAMP"),
		onupdate=text("CURRENT_TIMESTAMP"),
		nullable=False,
	)

	project: Mapped[Project] = relationship(
		"Project",
		foreign_keys=[project_id],
	)

	assignee: Mapped[User | None] = relationship(
		"User",
		foreign_keys=[assignee_id],
	)

	creator: Mapped[User] = relationship(
		"User",
		foreign_keys=[created_by_id],
	)

	__table_args__ = (
		Index(
			"idx_tasks_project_status",
			"project_id",
			"status",
		),
	)
```

### `comment.py`

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from app.models.user import User
	from app.models.task import Task


import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Comment(Base):
	__tablename__ = "comments"

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		primary_key=True,
		default=uuid.uuid4,
	)

	task_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		ForeignKey("tasks.id", ondelete="CASCADE"),
		nullable=False,
	)

	author_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		ForeignKey("users.id", ondelete="CASCADE"),
		nullable=False,
	)

	body: Mapped[str] = mapped_column(
		Text,
		nullable=False,
	)

	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		server_default=text("CURRENT_TIMESTAMP"),
		nullable=False,
	)

	updated_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		server_default=text("CURRENT_TIMESTAMP"),
		onupdate=text("CURRENT_TIMESTAMP"),
		nullable=False,
	)

	task: Mapped[Task] = relationship(
		"Task",
		foreign_keys=[task_id],
	)

	author: Mapped[User] = relationship(
		"User",
		foreign_keys=[author_id],
	)

	__table_args__ = (
		Index(
			"idx_comments_task_id",
			"task_id",
			"created_at",
		),
	)
```

### `attachment.py`

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from app.models.user import User
	from app.models.project import Project
	from app.models.task import Task
	from app.models.comment import Comment

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.enums import attachment_kind_enum


class Attachment(Base):
	__tablename__ = "attachments"

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		primary_key=True,
		default=uuid.uuid4,
	)

	uploader_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		ForeignKey("users.id", ondelete="CASCADE"),
		nullable=False,
	)

	project_id: Mapped[uuid.UUID | None] = mapped_column(
		UUID(as_uuid=True),
		ForeignKey("projects.id", ondelete="CASCADE"),
		nullable=True,
	)

	task_id: Mapped[uuid.UUID | None] = mapped_column(
		UUID(as_uuid=True),
		ForeignKey("tasks.id", ondelete="CASCADE"),
		nullable=True,
	)

	comment_id: Mapped[uuid.UUID | None] = mapped_column(
		UUID(as_uuid=True),
		ForeignKey("comments.id", ondelete="CASCADE"),
		nullable=True,
	)

	original_name: Mapped[str] = mapped_column(
		String(255),
		nullable=False,
	)

	stored_name: Mapped[str] = mapped_column(
		String(255),
		nullable=False,
	)

	mime_type: Mapped[str] = mapped_column(
		String(100),
		nullable=False,
	)

	size_bytes: Mapped[int] = mapped_column(
		nullable=False,
	)

	kind: Mapped[str] = mapped_column(
		attachment_kind_enum,
		nullable=False,
	)

	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		server_default=text("CURRENT_TIMESTAMP"),
		nullable=False,
	)

	uploader: Mapped[User] = relationship(
		"User",
		foreign_keys=[uploader_id],
	)

	project: Mapped[Project | None] = relationship(
		"Project",
		foreign_keys=[project_id],
	)

	task: Mapped[Task | None] = relationship(
		"Task",
		foreign_keys=[task_id],
	)

	comment: Mapped[Comment | None] = relationship(
		"Comment",
		foreign_keys=[comment_id],
	)

	__table_args__ = (
		Index("idx_attachments_uploader", "uploader_id"),
		Index("idx_attachments_project", "project_id"),
		Index("idx_attachments_task", "task_id"),
		Index("idx_attachments_comment", "comment_id"),
	)
```

### `task_attachment.py`

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from app.models.task import Task
	from app.models.attachment import Attachment

import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class TaskAttachment(Base):
	__tablename__ = "task_attachments"

	task_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		ForeignKey("tasks.id", ondelete="CASCADE"),
		primary_key=True,
		nullable=False,
	)

	attachment_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		ForeignKey("attachments.id", ondelete="CASCADE"),
		primary_key=True,
		nullable=False,
	)

	task: Mapped[Task] = relationship(
		"Task",
		foreign_keys=[task_id],
	)

	attachment: Mapped[Attachment] = relationship(
		"Attachment",
		foreign_keys=[attachment_id],
	)
```

### `activity.py`

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from app.models.user import User
	from app.models.project import Project


import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Activity(Base):
	__tablename__ = "activities"

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		primary_key=True,
		default=uuid.uuid4,
	)

	project_id: Mapped[uuid.UUID | None] = mapped_column(
		UUID(as_uuid=True),
		ForeignKey("projects.id", ondelete="CASCADE"),
		nullable=True,
	)

	actor_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		ForeignKey("users.id", ondelete="CASCADE"),
		nullable=False,
	)

	action: Mapped[str] = mapped_column(
		String(100),
		nullable=False,
	)

	entity_type: Mapped[str] = mapped_column(
		String(50),
		nullable=False,
	)

	entity_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		nullable=False,
	)

	extra_data: Mapped[dict] = mapped_column(
		"metadata",
		JSONB,
		nullable=False,
		server_default=text("'{}'::jsonb"),
	)

	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		server_default=text("CURRENT_TIMESTAMP"),
		nullable=False,
	)

	project: Mapped[Project | None] = relationship(
		"Project",
		foreign_keys=[project_id],
	)

	actor: Mapped[User] = relationship(
		"User",
		foreign_keys=[actor_id],
	)

	__table_args__ = (
		Index(
			"idx_activity_project_id",
			"project_id",
			text("created_at DESC"),
		),
	)
```

### `notification.py`

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from app.models.user import User

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Notification(Base):
	__tablename__ = "notifications"

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		primary_key=True,
		default=uuid.uuid4,
	)

	recipient_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		ForeignKey("users.id", ondelete="CASCADE"),
		nullable=False,
	)

	type: Mapped[str] = mapped_column(
		String(50),
		nullable=False,
	)

	message: Mapped[str] = mapped_column(
		Text,
		nullable=False,
	)

	entity_type: Mapped[str] = mapped_column(
		String(50),
		nullable=False,
	)

	entity_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		nullable=False,
	)

	read_at: Mapped[datetime | None] = mapped_column(
		DateTime(timezone=True),
		nullable=True,
	)

	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		server_default=text("CURRENT_TIMESTAMP"),
		nullable=False,
	)

	recipient: Mapped[User] = relationship(
		"User",
		foreign_keys=[recipient_id],
	)

	__table_args__ = (
		Index(
			"idx_notifications_recipient",
			"recipient_id",
			"read_at",
		),
	)
```