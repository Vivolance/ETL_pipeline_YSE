from integration_tests.conftest import integration_test_db_config
from integration_tests.src.utils.engine import ENGINE
from src.models.extracted_search_results import ExtractedSearchResult
from src.models.user import User
from src.service.dao.user_dao import UserDAO

from sqlalchemy import CursorResult, Row, TextClause, text


USER_DAO: UserDAO = UserDAO(
    integration_test_db_config()
)

class Insert:
    async def insert_user(self, user: User) -> None:
        """
        TODO: Integration test this
        """
        async with ENGINE.begin() as connection:
            insert_clause: TextClause = text(
                "INSERT into users("
                "   user_id, "
                "   created_at"
                ") values ("
                "   :user_id,"
                "   :created_at"
                ")"
            )
            # use named-params here to prevent SQL-injection attacks
            await connection.execute(
                insert_clause, {"user_id": user.user_id, "created_at": user.created_at}
            )

    async def insert_search(self, result: ExtractedSearchResult) -> None:
        async with ENGINE.begin() as connection:
            insert_clause: TextClause = text(
                "INSERT into extracted_search_results("
                "   id, "
                "   user_id, "
                "   url, "
                "   date, "
                "   body, "
                "   created_at"
                ") values ("
                "   :id,"
                "   :user_id, "
                "   :url, "
                "   :date, "
                "   :body, "
                "   :created_at "
                ")"
            )
            # use named-params here to prevent SQL-injection attacks
            await connection.execute(
                insert_clause,
                {
                    "id": result.id,
                    "user_id": result.user_id,
                    "url": result.url,
                    "date": result.date,
                    "body": result.body,
                    "created_at": result.created_at,
                },
            )