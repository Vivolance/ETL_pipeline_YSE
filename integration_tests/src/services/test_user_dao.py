import pytest

from integration_tests.conftest import integration_test_db_config
from integration_tests.src.utils.clear_tables import ClearTables
from integration_tests.src.utils.engine import engine
from src.models.user import User
from src.service.dao.user_dao import UserDAO

from sqlalchemy import CursorResult, Row, TextClause, text


USER_DAO: UserDAO = UserDAO(
    integration_test_db_config()
)

class TestInsertUser:

    @pytest.mark.asyncio_cooperative
    async def insert_user(self, user: User) -> None:
        await ClearTables.clear_users_table()