import os
import stat
import shutil
from pathlib import Path
from data.config import WORKING_DIR


EXTENSION_PATH = os.path.abspath(
    os.path.join(WORKING_DIR, Path("extension/metamask/12.9.3_0"))
)


def get_user_data_path(account_id: str | int) -> str | Path:
    path = os.path.abspath(os.path.join(WORKING_DIR, Path(f"tmp/user-{account_id}")))

    if os.path.exists(path):
        remove_user_data(account_id=account_id)

    os.mkdir(path=path)
    return path


def remove_user_data(account_id: str | int) -> bool:
    path = os.path.abspath(os.path.join(WORKING_DIR, Path(f"tmp/user-{account_id}")))

    if os.path.exists(path=path):
        shutil.rmtree(path, onerror=remove_readonly)

    return True


def remove_readonly(func, path, _):
    "Clear the readonly bit and reattempt the removal"
    os.chmod(path, stat.S_IWRITE)
    func(path)
