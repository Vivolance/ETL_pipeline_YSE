from integration_tests.src.utils.engine import engine
from sqlalchemy import TextClause, text


class ClearTables:

    @staticmethod
    async def clear_users_table() -> None:
        """
        Runs at the start of every integration test
        - Truncate users table
        """
        truncate_clause: TextClause = text("TRUNCATE TABLE users CASCADE")
        async with engine.begin() as connection:
            await connection.execute(truncate_clause)

    @staticmethod
    async def clear_extracted_search_results_table() -> None:
        """
        Runs at the start of every integration test
        - Truncate extracted_search_results_table table
        """
        truncate_clause: TextClause = text("TRUNCATE TABLE extracted_search_results")
        async with engine.begin() as connection:
            await connection.execute(truncate_clause)

    @staticmethod
    async def clear_search_results_table() -> None:
        """
        Runs at the start of every integration test
        - Truncate search_results_table table
        """
        truncate_clause: TextClause = text("TRUNCATE TABLE search_results")
        async with engine.begin() as connection:
            await connection.execute(truncate_clause)

    @staticmethod
    async def clear_last_extracted_user_status() -> None:
        """
        Runs at the start of every integration test
        - Truncate last_extracted_user_status table
        """
        truncate_clause: TextClause = text(
            "TRUNCATE TABLE last_extracted_user_status CASCADE"
        )
        async with engine.begin() as connection:
            await connection.execute(truncate_clause)
