"""

settings for logger please read ↓
https://github.com/Delgan/loguru

"""
import os

from loguru import logger

# locate log file
log_base_path: str = "../log"

# divide log type to info&warning
log_path_info: str = os.path.join(log_base_path, 'info')
log_path_warning: str = os.path.join(log_base_path, 'warning')

# logger for trace,debug,info,success
logger.add(
    sink=os.path.join(log_path_info, "runtime_{time:%Y-%m-%d}.info.log"),
    filter=lambda x: x["level"].no < logger.level("WARNING").no,
    rotation="00:00",
    retention="30 days",
    enqueue=True,
    encoding="utf-8",
    level="INFO"
)

# logger for warning,error,critical
logger.add(
    sink=os.path.join(log_path_warning, "runtime_{time:%Y-%m-%d}.err.log"),
    rotation="00:00",
    retention="30 days",
    enqueue=True,
    encoding="utf-8",
    level="WARNING"
)

__all__ = ["logger"]
