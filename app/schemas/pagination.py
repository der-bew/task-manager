import math
from typing import Generic, Sequence, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')

class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=100, description="Number of items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size

class PaginatedResponse(BaseModel, Generic[T]):
    items: Sequence[T]
    total: int
    page: int
    size: int
    pages: int

    @classmethod
    def create(cls, items: Sequence[T], total: int, params: PaginationParams) -> "PaginatedResponse[T]":
        return cls(
            items=items, 
            total=total, 
            page=params.page, 
            size=params.size, 
            pages=math.ceil(total / params.size) if total > 0 else 0
            )
    