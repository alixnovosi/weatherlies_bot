"""Main class to run weatherlies."""

import random
from os import path

import weatherbotskeleton

# Delay between tweets in seconds.
DELAY = 3600
DELAY_VARIATION = 369

if __name__ == "__main__":
    SECRETS_DIR = path.join(path.abspath(path.dirname(__file__)), "SECRETS")
    BOT_SKELETON = weatherbotskeleton.WeatherbotSkeleton(
        secrets_dir=SECRETS_DIR,
        owner_url="https://github.com/alixnovosi/weatherlies_bot",
        bot_name="weatherlies_bot",
        cities_file=path.join(SECRETS_DIR, "city.list.json"),
        lies=True
    )

    LOG = BOT_SKELETON.log

    while True:
        LOG.info("Sending a weather tweet.")
        weather = BOT_SKELETON.produce_status()

        LOG.info(f"Sending:\n {weather}")
        BOT_SKELETON.send(weather)

        BOT_SKELETON.set_delay(random.choice(range(DELAY-DELAY_VARIATION,
                                                   DELAY+DELAY_VARIATION+1))
        BOT_SKELETON.nap()
