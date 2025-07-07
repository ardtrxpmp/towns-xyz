import os
import random
from pathlib import Path
from playwright.sync_api import Page
from core.modules.towns import Towns
from core.utils.helpers import read_txt, write_txt
from data.config import WORKING_DIR
from core.modules.nickname_generation import generate_nicknames, generate_town_name


def towns_login(
    towns: Towns, link_wallet: bool = False, persistent_context: bool = False
):
    return towns.login(is_for_link=link_wallet, persistent_context=persistent_context)


def join_town_from_invite(towns: Towns, page: Page):
    used_nicknames = read_txt(
        os.path.join(WORKING_DIR, Path("data/used_nicknames.txt"))
    )
    if len(used_nicknames) == 0:
        generated_nickname = generate_nicknames(1)[0]
    else:
        while True:
            generated_nickname = generate_nicknames(1)[0]
            if generated_nickname not in used_nicknames:
                break
            else:
                continue

    if len(generated_nickname) >= 16:
        generated_nickname = generated_nickname[:8]

    write_txt(
        new_filename=os.path.join(WORKING_DIR, Path("data/used_nicknames.txt")),
        data_list=[generated_nickname],
        mode="a",
    )

    return towns.join_from_invite_link(page=page, username=generated_nickname)


def create_town(towns: Towns, page: Page):
    directory = os.path.join(WORKING_DIR, Path("images"))
    files = [
        file
        for file in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, file))
    ]
    town_name = generate_town_name()
    file_path = os.path.join(directory, Path(random.choice(files)))
    used_nicknames = read_txt(
        os.path.join(WORKING_DIR, Path("data/used_nicknames.txt"))
    )
    if len(used_nicknames) == 0:
        generated_nicknames = generate_nicknames(1)
    else:
        while True:
            generated_nicknames = generate_nicknames(1)
            for nick in generated_nicknames:
                if nick not in used_nicknames:
                    break
            else:
                continue

    write_txt(
        new_filename=os.path.join(WORKING_DIR, Path("data/used_nicknames.txt")),
        data_list=generated_nicknames,
        mode="a",
    )

    return towns.create_town(
        page=page,
        town_name=town_name,
        file_path=file_path,
        username=generated_nicknames[0],
        is_paid=random.choice(True, False),
    )


def fund_towns_wallet(towns: Towns, page: Page):
    internal_wallet = towns.fetch_internal_wallet(page=page)
    return towns.fund_internal_wallet(internal_wallet_address=internal_wallet)


def link_wallet(towns: Towns, page: Page):
    return towns.link_wallet(page=page)


def daily_tap(towns: Towns, page: Page):
    return towns.daily_task(page=page)


def greet_chat(towns: Towns, page: Page, chat_link: str):
    return towns.chat(page=page, chat_link=chat_link)
