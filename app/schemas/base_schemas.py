from pydantic import BaseModel
from datetime import datetime
from typing import Any, Optional

class APIResponse(BaseModel):
	message: Optional[str] = None
	data: Optional[Any] = None

class PaginatedResponse(APIResponse):
	total_pages : int
	page : int
	page_size : int

class AddCatg(BaseModel):
	category : str
