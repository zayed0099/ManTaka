
import sqlite3, time
from fastapi import HTTPException, status
# setup
conn = sqlite3.connect(":memory:")
cur = conn.cursor()
cur.execute(
	"""
	CREATE TABLE IF NOT EXISTS api_key (
		id_ TEXT PRIMARY KEY,
		api_key TEXT,
		user_id INTEGER,
		expires_at REAL,
		max_limit INTEGER CHECK (max_limit > 0),
		current_limit_count INTEGER DEFAULT 0,
		CONSTRAINT UQ_User_id UNIQUE (user_id)
	)
	""")

cur.execute(
	"""
	CREATE INDEX IF NOT EXISTS ix_current_max_limit
	ON api_key (user_id, current_limit_count, max_limit, expires_at);
	""")

conn.commit()

def api_limit_manage(user_id):
	cur.execute(
		"""SELECT max_limit, current_limit_count, expires_at 
		FROM api_key WHERE user_id=?""", (user_id,)
		)
	row = cur.fetchone()

	if not row:
		raise HTTPException(
				status_code=400,
				detail="An error occured while verifying jwt."
			)

	if row:
		current_time = time.time()
		max_limit, current_limit_count, expires_at = row

		if current_limit_count < max_limit and current_time < expires_at:
			new_count = current_limit_count + 1
			
			cur.execute(
				"""UPDATE api_key
					SET current_limit_count = ?
					WHERE user_id = ?""",
				(new_count, user_id)
			)
			conn.commit()
			return None

		else:
			cur.execute(
				"DELETE FROM api_key WHERE user_id=?", (user_id)
				)
			conn.commit()
			raise HTTPException(
				status_code=400,
				detail="Api key expired or limit reached."
			)

def api_key_set(id_, api_key, user_id, max_limit, ttl):
	expires_at = time.time() + ttl
	cur.execute(
			"""INSERT OR REPLACE INTO api_key (
			id_, api_key, user_id, expires_at, max_limit) VALUES (?, ?, ?, ?)""",
			(id_, api_key, user_id, expires_at, max_limit)
		)
	conn.commit()
