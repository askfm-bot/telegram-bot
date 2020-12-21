from typing import Optional
from datetime import datetime
from enum import IntEnum


class QuestionQueueItemStatus(IntEnum):
    Unprocessed = 0
    Processed = 1
    InProgress = 2
    Error = 3
    InstantlyInserted = 4


class QuestionQueueItem:
    def __init__(self, text: str, time_created: datetime, time_planned: datetime, time_sent: Optional[datetime],
                 status: QuestionQueueItemStatus, added_by_id: int, added_by_name: str, has_answer: bool):
        self.id = None
        self.text = text
        self.time_created = time_created
        self.time_planned = time_planned
        self.time_sent = time_sent
        self.status = status
        self.added_by_id = added_by_id
        self.added_by_name = added_by_name
        self.has_answer = has_answer
