from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.task_comment import TaskComment
from app.models.user import User
from app.schemas.task_comment import TaskCommentCreate

async def create_comment(db: AsyncSession, task_id: int, comment: TaskCommentCreate, user_id: int):
    db_comment = TaskComment(
        task_id=task_id,
        user_id=user_id,
        comment=comment.comment
    )
    db.add(db_comment)
    await db.flush()
    await db.refresh(db_comment)
    return db_comment

async def get_task_comments(db: AsyncSession, task_id: int):
    result = await db.execute(
        select(TaskComment, User.name).join(User).where(
            TaskComment.task_id == task_id
        ).order_by(TaskComment.created_at.desc())
    )
    comments = []
    for comment, user_name in result.all():
        comment_dict = {
            "id": comment.id,
            "task_id": comment.task_id,
            "user_id": comment.user_id,
            "comment": comment.comment,
            "created_at": comment.created_at,
            "user_name": user_name
        }
        comments.append(comment_dict)
    return comments
