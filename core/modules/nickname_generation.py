import random
from pathlib import Path
from core.utils.helpers import read_txt

adjectives = [
    "Happy",
    "Starry",
    "Mighty",
    "Swift",
    "Bright",
    "Gentle",
    "Brave",
    "Clever",
    "Bold",
    "Sunny",
    "Dreamy",
    "Fierce",
    "Jolly",
    "Kind",
    "Quiet",
    "Shiny",
    "Wild",
    "Calm",
    "Cheerful",
    "Zesty",
    "Sassy",
    "Snappy",
    "Charming",
    "Witty",
    "Lively",
    "Daring",
    "Majestic",
    "Epic",
    "Noble",
    "Serene",
    "Vibrant",
    "Graceful",
    "Fearless",
    "Radiant",
    "Whimsical",
    "Mystic",
    "Cunning",
    "Dynamic",
    "Skibidi",
    "Drippy",
    "Rizzy",
    "Nonchalant",
    "Ohio",
    "Gallant",
    "Elegant",
    "Jovial",
    "Peppy",
    "Steady",
    "Savvy",
    "Bubbly",
    "Quirky",
    "Spunky",
    "Vivacious",
    "Magical",
    "Dashing",
    "Playful",
    "Cheeky",
    "Resourceful",
    "Eager",
    "Gentle",
    "Chipper",
    "Harmonic",
    "Optimistic",
    "Gritty",
    "Wanderlust",
    "Perceptive",
    "Merry",
    "Thoughtful",
]

nouns = [
    "Explorer",
    "Dreamer",
    "Coder",
    "Wanderer",
    "Thinker",
    "Creator",
    "Seeker",
    "Builder",
    "Painter",
    "Writer",
    "Traveler",
    "Inventor",
    "Maker",
    "Dancer",
    "Hero",
    "Pilot",
    "Guardian",
    "Adventurer",
    "Scholar",
    "Ranger",
    "Wizard",
    "Knight",
    "Philosopher",
    "Visionary",
    "Nomad",
    "Juggler",
    "Tinkerer",
    "Alchemist",
    "Strategist",
    "Navigator",
    "Virtuoso",
    "Pioneer",
    "Chronicler",
    "Artisan",
    "Innovator",
    "Harbinger",
    "Mystic",
    "Wayfarer",
    "Guardian",
    "Sentinel",
    "Gooner",
    "Rizzler",
    "YN",
    "Storyteller",
    "Sculptor",
    "Challenger",
    "Enchanter",
    "Naturalist",
    "Prophet",
    "Cartographer",
    "Explorer",
    "Voyager",
    "Pathfinder",
    "Architect",
    "Trailblazer",
    "Enthusiast",
    "Dreamcatcher",
    "Oracle",
    "Warden",
    "Crusader",
    "Peacemaker",
    "Guardian",
    "Hustler",
    "Visionary",
    "Beacon",
    "Skibidi",
    "Gooning",
]

town_list = [
    "Town",
    "City",
    "Valley",
    "Boulevard",
    "Street",
    "Square",
    "Ville",
    "Village",
    "Scene",
    "Canyon",
    "Mountain",
]


def generate_town_name():
    startname = ""

    for _ in range(2):
        startname.join(random.choice(adjectives))

    startname.join(random.choice(town_list))

    return startname


def generate_nicknames(n: int) -> list:
    use_special_symbols = random.choice([True, False])
    use_numbers = random.choice([True, False])
    use_lowercase = random.choice([True, False])

    if use_special_symbols:
        symbol = random.choice(["-", "_"])
    else:
        symbol = None

    if use_numbers:
        number = str(random.randint(1984, 2007))
    else:
        number = None

    if n > len(adjectives) * len(nouns) * 48:
        raise ValueError(
            "Requested number of nicknames exceeds possible unique combinations."
        )

    all_combinations = list(
        set(
            [
                (
                    f"{adj}{symbol if symbol is not None else ''}{noun}{number if number is not None else ''}".lower()
                    if use_lowercase
                    else f"{adj}{symbol if symbol is not None else ''}{noun}{number if number is not None else ''}"
                )
                for adj in adjectives
                for noun in nouns
            ]
        )
    )
    return random.sample(all_combinations, n)


def is_nickname_used(nickname: str, filename: str | Path) -> bool:
    return nickname in read_txt(filename)
