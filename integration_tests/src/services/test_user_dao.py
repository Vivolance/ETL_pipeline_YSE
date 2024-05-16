from datetime import datetime

import pytest

from integration_tests.conftest import integration_test_db_config
from integration_tests.src.utils.clear_tables import ClearTables
from integration_tests.src.utils.engine import dummy_uuid
from integration_tests.src.utils.fetch import Fetch
from integration_tests.src.utils.insert import Insert
from src.models.user import User
from src.service.dao.user_dao import UserDAO


USER_DAO: UserDAO = UserDAO(integration_test_db_config())


class TestInsertUser:

    @pytest.mark.asyncio_cooperative
    async def test_insert_user(self) -> None:
        await ClearTables.clear_users_table()
        users: list[User] = [
            User(
                user_id=str(dummy_uuid),
                created_at=datetime(year=2024, month=5, day=16, hour=18),
            )
        ]

        for user in users:
            await USER_DAO.insert_user(user)
        results: list[User] = await Fetch.fetch_users()
        assert results == users
        await ClearTables.clear_users_table()

    @pytest.mark.asyncio_cooperative
    async def test_fetch_all_users(self) -> None:
        await ClearTables.clear_users_table()
        users: list[User] = [
            User(
                user_id=str(dummy_uuid),
                created_at=datetime(year=2024, month=5, day=18, hour=19),
            )
        ]

        for user in users:
            await Insert.insert_user(user)

        results: list[User] = await USER_DAO.fetch_all_users()
        assert results == users
        await ClearTables.clear_users_table()
