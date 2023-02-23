"""import module"""
from pydantic import BaseModel, Field


class QueuesInDetail(BaseModel):  # pylint: disable
    current_message_count: int = Field(
        0, description="current message count for this queue"
    )
    delay_message_count: int = Field(
        0, description="current delay message count for this queue"
    )
    dead_message_count: int = Field(
        0, description="current dead message count for this queue"
    )


class ListOfQueues(BaseModel):
    queue_name: QueuesInDetail


class QueueResponse(BaseModel):
    all_messages_in_queues: int = Field(0, description="overall queue count")
    all_messages_in_delay_queues: int = Field(
        0, description="overall delay queue count"
    )
    all_messages_in_delay_queues: int = Field(
        0, description="overall delay queue count"
    )
    all_messages_in_dead_letter_queues: int = Field(
        0, description="overall dead queue count"
    )
    list_of_queues: ListOfQueues


class QueuePath(BaseModel):
    queue_name: str = Field(description="queue name")


class MessagePath(BaseModel):
    queue_name: str = Field(description="queue name")
    message_id: str = Field(description="message id")


class MessageResponse(BaseModel):
    actor_name: str = Field(description="actor name")
    args: dict = Field([], description="The values passed to the actor")
    kwargs: dict = Field({}, description="the keyword arguments passed to the actor")
    created_at: int = Field(0, description="how long ago the message was created")
    message_id: str = Field(description="the uuid of the message")
    message_timestamp: int = Field(
        0,
        description="the time that the message was created which is a unix timestamp in milliseconds",
    )
    retries: int = Field({}, description="number of retries for this job")
    traceback: str = Field(description="The error given from the worker")
    queue_name: str = Field(description="actor name")


class MessagesOutline(BaseModel):
    job_name: MessageResponse


class ListOfMessages(BaseModel):
    list_of_messages: MessagesOutline


class QueueDetailResponse(BaseModel):
    current_queue_msg: ListOfMessages
    delay_queue_msg: ListOfMessages
    dead_queue_msg: ListOfMessages


class StatusResponse(BaseModel):
    status: str = Field(description="The status of the operation")
