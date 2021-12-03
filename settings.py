import os
from pathlib import Path


class Settings:
    version: float = 0.1
    RootPath = Path(__file__)
    # 桌面上的anime文件夹
    AnimePath = os.path.join(os.path.join(os.path.expanduser("~"), "Desktop"), "anime")
    NewPatchPath = os.path.join(AnimePath, "NewPatch")
    ClientConfigPath = os.path.join(NewPatchPath, "config.ini")


settings = Settings()
