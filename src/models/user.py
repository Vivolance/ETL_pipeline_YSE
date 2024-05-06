import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, SkipValidation


class User(BaseModel):
    user_id: str
    created_at: SkipValidation[datetime]
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @staticmethod
    def create_user() -> "User":
        return User(
            user_id=str(uuid.uuid4()),
            created_at=datetime.utcnow(),
        )
