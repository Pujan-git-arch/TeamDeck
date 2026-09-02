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