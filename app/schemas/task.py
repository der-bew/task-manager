from datetime import datetime
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TaskBase(BaseModel):
	title: str = Field(min_length=1, max_length=255)
	description: str | None = Field(default=None, max_length=10000)


class TaskCreate(TaskBase):
	pass


class TaskUpdate(BaseModel):
	title: str | None = Field(default=None, min_length=1, max_length=255)
	description: str | None = Field(default=None, max_length=10000)
	is_completed: bool | None = None
	model_config = ConfigDict(extra="forbid")

	@model_validator(mode="after")
	def validate_non_nullable_fields(self) -> Self:
		for name in ("title", "is_completed"):
			if name in self.model_fields_set and getattr(self, name) is None:
				raise ValueError(f"{name} cannot be null")
		return self


class TaskRead(TaskBase):
	model_config = ConfigDict(from_attributes=True)

	id: int
	title: str
	owner_id: int
	is_completed: bool 
	created_at: datetime
	updated_at: datetime
