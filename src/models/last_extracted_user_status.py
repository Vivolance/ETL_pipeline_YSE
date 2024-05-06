import uuid
from datetime import datetime

from pydantic import BaseModel


class LastExtractedUserStatus(BaseModel):
    id: str
    user_id: str
    last_run: datetime

    @staticmethod
    def create_user_status(user_id: str) -> "LastExtractedUserStatus":
        return LastExtractedUserStatus(
            id=str(uuid.uuid4()), user_id=user_id, last_run=datetime.utcnow()
        )
