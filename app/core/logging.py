import logging
import os
# making sure the logs folder exists
os.makedirs("logs", exist_ok=True)

# --- Admin logger 
admin_logger = logging.getLogger("myapp.admin")
admin_handler = logging.FileHandler("logs/admin.log")
admin_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

admin_handler.setFormatter(admin_formatter)
admin_logger.addHandler(admin_handler)
admin_logger.setLevel(logging.INFO)
admin_logger.propagate = False   # to not send messages up to root

# --- sqlalchemy logger
sqlalchemy_logger = logging.getLogger("sqlalchemy.orm")
sqlalchemy_handler = logging.FileHandler("logs/sqlalchemy.log")
sqlalchemy_formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
								
sqlalchemy_handler.setFormatter(sqlalchemy_formatter)
sqlalchemy_logger.addHandler(sqlalchemy_handler)
sqlalchemy_logger.setLevel(logging.INFO)
sqlalchemy_logger.propagate = False
							
# --- FastApi uvicorn logger
uvicorn_logger = logging.getLogger("uvicorn.access")
uvicorn_handler = logging.FileHandler("logs/access.log")
uvicorn_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
uvicorn_logger.addHandler(uvicorn_handler)
uvicorn_logger.setLevel(logging.INFO)
uvicorn_logger.propagate = False

# --- FastApi uvicorn logger
uvicorn_error_logger = logging.getLogger("uvicorn.error")
uvicorn_error_handler = logging.FileHandler("logs/error.log")
uvicorn_error_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
uvicorn_error_logger.addHandler(uvicorn_error_handler)
uvicorn_error_logger.setLevel(logging.INFO)
uvicorn_error_logger.propagate = False
