from datetime import datetime
import uuid

from pydantic import BaseModel, ConfigDict, SkipValidation


class SearchResults(BaseModel):
    search_id: str
    user_id: str
    search_term: str
    result: str | None
    created_at: SkipValidation[datetime]
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @staticmethod
    def create(user_id: str, search_term: str, result: str | None) -> "SearchResults":
        return SearchResults(
            search_id=str(uuid.uuid4()),
            user_id=user_id,
            search_term=search_term,
            result=result,
            created_at=datetime.utcnow(),
        )
