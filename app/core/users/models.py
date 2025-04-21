from app.infra.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import BIGINT, BOOLEAN

class User(Base):
    __tablename__ = 'users'
    user_id:Mapped[int] =mapped_column(BIGINT, primary_key=True)
    is_waiter:Mapped[bool] = mapped_column(BOOLEAN,nullable=False, default=False)
