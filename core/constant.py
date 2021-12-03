from typing import List

GET_DIRS_COMMAND = 0
GET_FILES_COMMAND = 1
DOWNLOAD_COMMAND = 2
CHECK_UPDATE_COMMAND = 3
CHECK_HOST_COMMAND = 4

# ----------------------------------------------------- CONNECTION CODE ------------------------------------------------

SUCCESS_CODE = 200
FAIL_CODE = 400

# -----------------------------------------------------  CONSTANT -----------------------------------------------------

CONFIG_FILE: str = "config.ini"
VIDEO_FORMAT: List[str] = ["mp4", "mkv", "rmvb", "flv"]
