import os
from itertools import cycle
from pathlib import Path
from core.utils.helpers import read_txt, decipher, read_yaml

WORKING_DIR = Path(os.getcwd())

PRIVATE_KEY_ITEM_FILE = os.path.join(WORKING_DIR, Path("data/private_keys.txt"))

PRIVATE_KEYS = [decipher(item) for item in read_txt(PRIVATE_KEY_ITEM_FILE)]

ACCOUNT_NAMES = tuple([i for i, _ in enumerate(PRIVATE_KEYS, start=1)])

PROXIES = read_txt(os.path.join(WORKING_DIR, Path("data/proxies.txt")))

EMAILS = read_txt(os.path.join(WORKING_DIR, Path("data/emails.txt")))

PROXY_CYCLE = cycle(PROXIES)

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

CONFIG_FILE = read_yaml(os.path.join(WORKING_DIR, Path("settings.yaml")))
