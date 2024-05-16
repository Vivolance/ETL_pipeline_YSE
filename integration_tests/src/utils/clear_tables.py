from integration_tests.src.utils.engine import ENGINE
from sqlalchemy import CursorResult, Row, TextClause, text

class ClearTables:

    @staticmethod
    async def clear_users_table() -> None:
        """
        Runs at the start of every integration test
        - Truncate users table
        """
        truncate_clause: TextClause = text("TRUNCATE TABLE users CASCADE")
        async with ENGINE.begin() as connection:
            await connection.execute(truncate_clause)

    @staticmethod
    async def clear_extracted_search_results_table() -> None:
        """
        Runs at the start of every integration test
        - Truncate users table
        """
        truncate_clause: TextClause = text("TRUNCATE TABLE extracted_search_results")
        async with ENGINE.begin() as connection:
            await connection.execute(truncate_clause)