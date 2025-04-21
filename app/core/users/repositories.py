from dataclasses import dataclass

from sqlalchemy import select

from app.infra.postgres.db import DataBase
from sqlalchemy.dialects.postgresql import insert
from app.core.users.models import User
@dataclass
class UserRepository:
    database: DataBase


    async def create_user_if_not_exists(self,user_id:int,is_waiter:bool = False)->None:
        async with self.database.session() as session:
            stmt = insert(User).values(user_id = user_id, is_waiter=is_waiter).on_conflict_do_nothing()
            await session.execute(stmt)
            await session.commit()

    async def get_waiter_user_ids(self)->list[int]:
        async with self.database.session() as session:
            stmt = select(User.user_id).where(User.is_waiter==True)
            return list(await session.scalars(stmt))



