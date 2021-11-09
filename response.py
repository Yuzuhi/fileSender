from constant import *


class ResponseHandler:

    def __init__(self, conn):
        self.conn = conn

    def distribute(self, code: int):
        if code == GET_DIRS_COMMAND:
            pass
        elif code == GET_FILES_COMMAND:
            pass
        elif code == SINGLE_DOWNLOAD_COMMAND:
            pass
        elif code == MULTI_DOWNLOAD_COMMAND:
            pass
