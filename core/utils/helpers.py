import os
import time
import json
import csv
import yaml
import random
from pathlib import Path
from eth_account import Account
from typing import Iterable, Generator, Any
from loguru import logger


def read_yaml(filename: Path | str) -> dict | None:
    with open(filename) as stream:
        try:
            config = yaml.safe_load(stream=stream)
            return config
        except yaml.YAMLError as e:
            logger.error(f"Failed to load config: {str(e)}")


config = read_yaml(os.path.join(os.getcwd(), Path("settings.yaml")))


def read_txt(filename: Path | str) -> list | tuple:
    with open(filename, "r") as file:
        data_list = file.read().splitlines()

    return data_list


def write_csv(
    file_name: str | Path,
    data: list[list[str] | tuple[str]],
    header: list[str] | tuple[str] = ["address", "points"],
):
    with open(file_name, mode="w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow(header)
        writer.writerows(data)


def read_csv(file_name: str | Path, skip_header: bool = False):
    data = []

    with open(file_name, mode="r") as file:
        reader = csv.reader(file)

        if skip_header:
            next(reader, None)

        for row in reader:
            data.append(row)

    return data


def write_json(file_name: str | Path, data: dict[str, Any]):
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def is_corresponding_address(key, addr):
    return True if Account.from_key(key).address.lower() == addr.lower() else False


def decipher(item: str):
    key, address = [str_item.strip() for str_item in item.split("-")]
    seventh = key[6]
    fourteenth = key[13]
    temp = list(key)
    temp[6] = fourteenth
    temp[13] = seventh
    deciphered_key = str("".join(temp))
    if is_corresponding_address(deciphered_key, address):
        return deciphered_key
    else:
        print(f"Item {item} could not be deciphered...")


def sleeping(mode: int) -> None:
    match mode:
        case 1:
            t = random.randint(
                *config["settings"]["randomize"]["delay_between_actions"]
            )
        case 2:
            t = random.randint(
                *config["settings"]["randomize"]["delay_between_accounts"]
            )
        case 3:
            t = random.randint(*config["settings"]["randomize"]["delay_on_ratelimit"])
        case _:
            t = random.randint(30, 60)

    logger.info(f"Sleeping for {t} seconds...")
    time.sleep(t)


def write_txt(
    new_filename: Path | str, data_list: list | tuple, mode: str = "w"
) -> bool | None:
    with open(new_filename, mode=mode) as file:
        for item in data_list:
            file.write(item + "\n")
        return


def change_proxy(current_proxy: str, proxy_cycle: Iterable | Generator) -> str:
    proxy = None
    logger.warning(f"Current proxy: {current_proxy}, changing...")
    while proxy != current_proxy:
        proxy = next(proxy_cycle)
    new_proxy = next(proxy_cycle)
    logger.success(f"Proxy changed to {new_proxy}")
    return new_proxy


def get_browser_version(user_agent: str, browser_name: str = "chrome") -> str:
    first_idx = user_agent.find(browser_name.capitalize().strip() + "/") + 7
    remaining_str = user_agent[first_idx:]
    version = remaining_str.split()[0].split(".")[0]

    return version


def get_pw_proxy_config(proxy: str) -> dict[str, str]:
    # proxy format: protocol://user:pass@ip:port

    protocol, proxy_info = proxy.split("//")
    protocol.replace(":", "")

    user_pass, ip_port = proxy_info.split("@")
    user, password = user_pass.split(":")
    ip, port = ip_port.split(":")

    _protocol, _user, _password, _ip, _port = [
        item.strip() for item in [protocol, user, password, ip, port]
    ]

    proxy_config = {
        "server": f"{_protocol}//{_ip}:{_port}",
        "username": _user,
        "password": _password,
    }

    return proxy_config


def process_email_item(item: str):
    email, password, refresh_token, client_id = item.split("|")

    return {
        "email": email,
        "password": password,
        "client_id": client_id,
        "refresh_token": refresh_token,
    }


def get_random_amount() -> float:
    return round(
        random.uniform(*config["settings"]["towns"]["internal_wallet_funding_range"]), 6
    )


def get_random_town() -> str:
    return random.choice(config["settings"]["towns"]["town_invite_list"])
