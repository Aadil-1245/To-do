# Database Relationships Documentation
## Todo Application - SQLAlchemy Models

**Date:** February 19, 2026  
**Total Models:** 9  
**Total Relationships:** 11 Direct + 2 Through Junction Tables

---

## 📊 Quick Summary

| Type | Count | Details |
|------|-------|---------|
| **One-to-Many** | 11 | Direct 1:N relationships |
| **Many-to-Many** | 2 | Through junction table/composite relationships |
| **Total Connections** | 13 | Complete relationship map |

---

## 🔗 One-to-Many (1:N) Relationships

### 1. **User ➜ Project (Owner)**
```
User (1) ────────────── (N) Project
         owner_id FK
```
- **Direction:** One user owns many projects
- **FK Column:** `projects.owner_id` → `users.id`
- **Model Code:**
  ```python
  # User Model
  projects = relationship("Project", back_populates="owner")
  
  # Project Model
  owner = relationship("User", back_populates="projects")
  ```
- **Example:** User 1 creates 5 different projects
- **Cascade:** `cascade="all, delete-orphan"` - Projects deleted if owner deleted

---

### 2. **User ➜ Task (Assigned To)**
```
User (1) ────────────── (N) Task
         assigned_to FK
```
- **Direction:** One user can be assigned many tasks
- **FK Column:** `tasks.assigned_to` → `users.id`
- **Model Code:**
  ```python
  # User Model
  assigned_tasks = relationship("Task", back_populates="assigned_user")
  
  # Task Model
  assigned_user = relationship("User", back_populates="assigned_tasks")
  ```
- **Example:** User 1 is assigned 10 tasks across projects
- **Nullable:** Yes (`assigned_to` can be NULL for unassigned tasks)

---

### 3. **User ➜ ProjectMember (Membership)**
```
User (1) ────────────── (N) ProjectMember
         user_id FK
```
- **Direction:** One user can be a member of many projects
- **FK Column:** `project_members.user_id` → `users.id`
- **Model Code:**
  ```python
  # User Model
  project_memberships = relationship("ProjectMember", back_populates="user")
  
  # ProjectMember Model
  user = relationship("User", back_populates="project_memberships")
  ```
- **Example:** User 1 is member of 3 different projects with different roles
- **Junction Table:** Allows many-to-many User ↔ Project

---

### 4. **User ➜ TaskComment (Comments Author)**
```
User (1) ────────────── (N) TaskComment
         user_id FK
```
- **Direction:** One user can write many comments
- **FK Column:** `task_comments.user_id` → `users.id`
- **Model Code:**
  ```python
  # User Model
  task_comments = relationship("TaskComment", back_populates="user")
  
  # TaskComment Model
  user = relationship("User", back_populates="task_comments")
  ```
- **Example:** User 1 has commented on 15 different tasks
- **Usage:** Task comments section - "Posted by User 1"

---

### 5. **User ➜ Notification (Recipient)**
```
User (1) ────────────── (N) Notification
         user_id FK
```
- **Direction:** One user receives many notifications
- **FK Column:** `notifications.user_id` → `users.id`
- **Model Code:**
  ```python
  # User Model
  notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
  
  # Notification Model
  user = relationship("User", back_populates="notifications")
  ```
- **Example:** User 1 has 25 notifications (read and unread)
- **Cascade:** Notifications deleted when user deleted
- **Usage:** NotificationBell component

---

### 6. **User ➜ AccessRequest (Requester)**
```
User (1) ────────────── (N) AccessRequest
         requester_id FK
```
- **Direction:** One user can send many access requests
- **FK Column:** `access_requests.requester_id` → `users.id`
- **Model Code:**
  ```python
  # User Model
  access_requests_sent = relationship(
    "AccessRequest", 
    foreign_keys="AccessRequest.requester_id", 
    back_populates="requester"
  )
  
  # AccessRequest Model
  requester = relationship("User", foreign_keys=[requester_id], back_populates="access_requests_sent")
  ```
- **Example:** User 1 sends 3 requests to create projects or join projects
- **Foreign Key Complexity:** Custom foreign_keys because AccessRequest has TWO User FKs

---

### 7. **Project ➜ Status (Columns)**
```
Project (1) ────────────── (N) Status
            project_id FK
```
- **Direction:** One project has many status columns
- **FK Column:** `statuses.project_id` → `projects.id`
- **Model Code:**
  ```python
  # Project Model
  statuses = relationship("Status", back_populates="project", cascade="all, delete-orphan")
  
  # Status Model
  project = relationship("Project", back_populates="statuses")
  ```
- **Example:** Project 1 has columns: Todo, In Progress, Done, Review
- **Cascade:** Statuses deleted when project deleted
- **Usage:** Kanban board columns (feature we implemented)

---

### 8. **Project ➜ Task (Tasks in Project)**
```
Project (1) ────────────── (N) Task
            project_id FK
```
- **Direction:** One project contains many tasks
- **FK Column:** `tasks.project_id` → `projects.id`
- **Model Code:**
  ```python
  # Project Model
  tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
  
  # Task Model
  project = relationship("Project", back_populates="tasks")
  ```
- **Example:** Project 1 has 50 total tasks
- **Cascade:** Tasks deleted when project deleted
- **Usage:** Kanban board tasks display

---

### 9. **Project ➜ ProjectMember (Team Members)**
```
Project (1) ────────────── (N) ProjectMember
            project_id FK
```
- **Direction:** One project has many team members
- **FK Column:** `project_members.project_id` → `projects.id`
- **Model Code:**
  ```python
  # Project Model
  team_members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
  
  # ProjectMember Model
  project = relationship("Project", back_populates="team_members")
  ```
- **Example:** Project 1 has team of 5 members
- **Cascade:** ProjectMembers deleted when project deleted
- **Usage:** Group by project to see who's in it

---

### 10. **Status ➜ Task (Tasks in Column)**
```
Status (1) ────────────── (N) Task
           status_id FK
```
- **Direction:** One status/column contains many tasks
- **FK Column:** `tasks.status_id` → `statuses.id`
- **Model Code:**
  ```python
  # Status Model
  tasks = relationship("Task", back_populates="status")
  
  # Task Model
  status = relationship("Status", back_populates="tasks")
  ```
- **Example:** Status "In Progress" has 8 tasks
- **Usage:** Rendering tasks in each Kanban column
- **Dynamic:** Columns can be added/edited/deleted (our new feature)

---

### 11. **Task ➜ TaskComment (Comments on Task)**
```
Task (1) ────────────── (N) TaskComment
         task_id FK
```
- **Direction:** One task has many comments
- **FK Column:** `task_comments.task_id` → `tasks.id`
- **Model Code:**
  ```python
  # Task Model
  comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")
  
  # TaskComment Model
  task = relationship("Task", back_populates="comments")
  ```
- **Example:** Task 1 has 7 comments from team members
- **Cascade:** Comments deleted when task deleted
- **Usage:** Comments section in task details modal

---

## 🔄 Many-to-Many (N:M) Relationships

### 1. **User ↔ Project (Through ProjectMember)**
```
User (N) ╭─────────────────╮ (N) Project
         │  ProjectMember  │
         │   (Junction)    │
         ╰─────────────────╯
```

- **Pattern:** Many users → Many projects (with roles)
- **Junction Table:** `project_members`
- **Foreign Keys:**
  - `project_members.user_id` → `users.id`
  - `project_members.project_id` → `projects.id`
- **Model Code:**
  ```python
  # ProjectMember (Junction Table)
  class ProjectMember(Base):
      project_id = Column(Integer, ForeignKey("projects.id"))
      user_id = Column(Integer, ForeignKey("users.id"))
      role = Column(String, default="member")  # leader or member
      
      project = relationship("Project", back_populates="team_members")
      user = relationship("User", back_populates="project_memberships")
  ```
- **Example:**
  - User 1 is LEADER in Project A
  - User 1 is MEMBER in Project B
  - User 2 is MEMBER in Project A
  - User 3 is MEMBER in Project B
- **Purpose:** 
  - Track which users are in which projects
  - Store different roles per user per project
  - One user can have different roles in different projects

---

### 2. **User ↔ Project (Through AccessRequest)**
```
User (N) ╭──────────────────╮ (N) Project
         │   AccessRequest  │
         │    (Temporary)   │
         ╰──────────────────╯
```

- **Pattern:** Many users request access to many projects
- **Special Table:** `access_requests` (intermediate, not permanent membership)
- **Foreign Keys:**
  - `access_requests.requester_id` → `users.id` (who requests)
  - `access_requests.approver_id` → `users.id` (who approves)
  - `access_requests.project_id` → `projects.id` (which project)
- **Model Code:**
  ```python
  # AccessRequest (Semi-Permanent Junction)
  class AccessRequest(Base):
      requester_id = Column(Integer, ForeignKey("users.id"))  # Who's asking
      approver_id = Column(Integer, ForeignKey("users.id"))   # Who approves
      project_id = Column(Integer, ForeignKey("projects.id")) # For what
      status = Column(String, default="pending")  # pending, approved, rejected
      
      requester = relationship("User", foreign_keys=[requester_id], ...)
      approver = relationship("User", foreign_keys=[approver_id], ...)
      project = relationship("Project", foreign_keys=[project_id], ...)
  ```
- **Example:**
  - User 3 requests to create projects → AccessRequest (pending) → Admin approves → User 3 can create
  - User 4 requests to join Project A → AccessRequest (pending) → Project leader approves → ProjectMember added
- **Difference from ProjectMember:**
  - **AccessRequest:** Temporary, waiting for approval (workflow)
  - **ProjectMember:** Permanent, already member of project

---

## 📋 All Models Overview

### Users Table
```
id (PK)           → Primary Key
name              → User name
email (UNIQUE)    → User email
hashed_password   → Encrypted password
role              → admin, user
can_create_projects → Boolean (permission)
```

### Projects Table
```
id (PK)           → Primary Key
title             → Project title
description       → Project description
owner_id (FK)     → Points to users.id
start_date        → Project start
end_date          → Project end
technology_stack  → JSON string of tech
team_size         → Number of team members
```

### Statuses Table
```
id (PK)           → Primary Key
name              → Status name (Todo, In Progress, etc.)
position          → UUID for ordering
project_id (FK)   → Points to projects.id
```

### Tasks Table
```
id (PK)           → Primary Key
title             → Task title
description       → Task description
priority          → Task priority level
due_date          → Task deadline
status_id (FK)    → Points to statuses.id
project_id (FK)   → Points to projects.id
assigned_to (FK)  → Points to users.id (nullable)
```

### ProjectMembers Table
```
id (PK)           → Primary Key
project_id (FK)   → Points to projects.id
user_id (FK)      → Points to users.id
role              → leader or member
```

### TaskComments Table
```
id (PK)           → Primary Key
task_id (FK)      → Points to tasks.id
user_id (FK)      → Points to users.id
comment (TEXT)    → Comment content
```

### Notifications Table
```
id (PK)           → Primary Key
user_id (FK)      → Points to users.id
message (TEXT)    → Notification message
type              → project_assigned, task_assigned, comment_added, access_approved, access_rejected
is_read           → Boolean (read/unread)
related_id        → ID of related project/task/comment
```

### AccessRequests Table
```
id (PK)           → Primary Key
requester_id (FK) → Points to users.id (who requests)
approver_id (FK)  → Points to users.id (who approves, nullable)
project_id (FK)   → Points to projects.id (nullable)
request_type      → create_project or join_project
reason (TEXT)     → Why they request
status            → pending, approved, rejected
```

---

## 🎯 Entity Relationship Diagram (Text Version)

```
┌─────────────────────────────────────────────────────────────────┐
│                         USERS TABLE                             │
│  (PK: id) - name, email, hashed_password, role, can_create... │
│                                                                 │
│  Relationships:                                                 │
│  • 1:N → Projects (owner_id)                                   │
│  • 1:N → Tasks (assigned_to)                                   │
│  • 1:N → ProjectMembers (user_id) ─────┐                       │
│  • 1:N → TaskComments (user_id)        │                       │
│  • 1:N → Notifications (user_id)       │  Many-to-Many        │
│  • 1:N → AccessRequests (requester_id) │  via M2M table ─────┐ │
└─────────────────────────────────────────────────────────────────┘
       ▲                                                           │
       │                                    ┌──────────────────┐   │
       │ (owner_id)                         │PROJECT_MEMBERS   │   │
       │ One user                           │(Junction Table)  │   │
       │ owns many projects                 │              │   │
       │                                    └──────────────────┘
       │
┌─────────────────────────────────────────────────────────────────┐
│                      PROJECTS TABLE                             │
│  (PK: id) - title, description, owner_id(FK), start_date...   │
│                                                                 │
│  Relationships:                                                 │
│  • N:1 ← User (owner_id)                                        │
│  • 1:N → Statuses (project_id) ──────────────────────┐         │
│  • 1:N → Tasks (project_id) ───────────────┐        │         │
│  • 1:N → ProjectMembers (project_id) ──┐   │        │         │
│  • N:M ← Users (via ProjectMembers) ───┘   │        │         │
└─────────────────────────────────────────────────────────────────┘
                         ▲                   │        │
                         │                   │        ▼
                         │        ┌──────────────────────────────┐
                         │        │      STATUSES TABLE          │
                         │        │  (PK: id) - name, position│
                         │        │         project_id(FK)       │
                         │        │                              │
                         │        │  • N:1 ← Project             │
                         │        │  • 1:N → Tasks (status_id)───┼─┐
                         │        │                              │ │
                         │        └──────────────────────────────┘ │
                         │                                          │
                         │                          ▼               │
                         │        ┌──────────────────────────────┐ │
                         │        │       TASKS TABLE            │ │
                         │        │  (PK: id) - title, desc...│ │
                         └────────┼─ project_id(FK)           │ │
                                  │  status_id(FK) ◄──────────┘ │
                                  │  assigned_to(FK)            │
                                  │                              │
                                  │  • N:M ← Users (assigned_to)│
                                  │  • N:1 ← Project            │
                                  │  • N:1 ← Status             │
                                  │  • 1:N → TaskComments       │
                                  │                              │
                                  └──────────────────────────────┘
                                           │
                                           ▼
                        ┌──────────────────────────────┐
                        │   TASK_COMMENTS TABLE        │
                        │  (PK: id) - comment, ...    │
                        │  task_id(FK), user_id(FK)   │
                        │                              │
                        │  • N:1 ← Task                │
                        │  • N:1 ← User                │
                        │                              │
                        └──────────────────────────────┘

```

---

## 📊 Relationship Types Summary

| Relationship | Tables | Type | Via | Count |
|--------------|--------|------|-----|-------|
| User → Project | users, projects | 1:N | owner_id | 1 |
| User → Task | users, tasks | 1:N | assigned_to | 1 |
| User → ProjectMember | users, project_members | 1:N | user_id | 1 |
| User → TaskComment | users, task_comments | 1:N | user_id | 1 |
| User → Notification | users, notifications | 1:N | user_id | 1 |
| User → AccessRequest | users, access_requests | 1:N | requester_id | 1 |
| Project → Status | projects, statuses | 1:N | project_id | 1 |
| Project → Task | projects, tasks | 1:N | project_id | 1 |
| Project → ProjectMember | projects, project_members | 1:N | project_id | 1 |
| Status → Task | statuses, tasks | 1:N | status_id | 1 |
| Task → TaskComment | tasks, task_comments | 1:N | task_id | 1 |
| User ↔ Project | users, project_members, projects | N:M | ProjectMember (junction) | 1 |
| User ↔ Project | users, access_requests, projects | N:M | AccessRequest | 1 |

---

## 🔑 Key Concepts

### One-to-Many (1:N)
- **One parent** can have **multiple children**
- Example: 1 Project has N Tasks
- **Implementation:** Foreign key in child table pointing to parent
- **Count:** 11 in this database

### Many-to-Many (N:M)
- **Multiple parents** can have **multiple children**
- Example: N Users can be in N Projects
- **Implementation:** Junction/Bridge table with two foreign keys
- **Count:** 2 in this database

### Cascade Delete
- When parent is deleted, all children are deleted
- **Used:**
  - Project deletion → deletes all Statuses, Tasks, ProjectMembers
  - Task deletion → deletes all TaskComments
  - User deletion → deletes all Notifications sent to them

### Foreign Keys Marked Nullable
- `tasks.assigned_to` - Task can be unassigned
- `access_requests.approver_id` - Request waiting approval (no approver yet)
- `access_requests.project_id` - For create_project requests (no specific project)

---

**End of Documentation**
