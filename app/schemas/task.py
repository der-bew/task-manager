from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskBase(BaseModel):
	title: str = Field(min_length=1, max_length=255)
	description: str | None = Field(default=None, max_length=10000)


class TaskCreate(TaskBase):
	pass


class TaskUpdate(BaseModel):
	title: str | None = Field(default=None, min_length=1, max_length=255)
	description: str | None = None
	is_completed: bool | None = None
	model_config = ConfigDict(extra="forbid")


class TaskRead(TaskBase):
	model_config = ConfigDict(from_attributes=True)

	id: int
	title: str
	owner_id: int
	is_completed: bool 
	created_at: datetime
	updated_at: datetime
