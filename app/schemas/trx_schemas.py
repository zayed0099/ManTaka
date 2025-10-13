from pydantic import BaseModel
from datetime import date
from typing import Any, Optional

class NewTrx(BaseModel):
	amount : int
	trx_type : str
	trx_at : date

	# Fk's
	wallet_id : int
	catg_id : int

class UpdateTrx(NewTrx):
	amount : Optional[int] = None
	trx_type : Optional[str] = None
	trx_at : Optional[date] = None

	# Fk's
	wallet_id : Optional[int] = None
	catg_id : Optional[int] = None
