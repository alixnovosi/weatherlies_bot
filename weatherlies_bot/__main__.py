"""Main class to run randomweather_bot."""

import os
import random
import time

import botskeleton

import weather_gen

# Delay between tweets in seconds.
DELAY = 2000
DELAY_VARIATION = 400

if __name__ == "__main__":
    SECRETS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "SECRETS")
    BOT_SKELETON = botskeleton.BotSkeleton(SECRETS_DIR, bot_name="weatherlies_bot")

    LOG = botskeleton.set_up_logging()

    while True:
        try:
            weather = weather_gen.produce_status()
        except Exception as e:
            BOT_SKELETON.send_dm_sos(f"Bot {BOT_SKELETON.bot_name} " +\
                                     f"had an error it can't recover from!\n{e}")
            raise

        LOG.info(f"Sending:\n {weather}")

        BOT_SKELETON.send(weather)

        BOT_SKELETON.delay = random.choice(range(DELAY-DELAY_VARIATION, DELAY+DELAY_VARIATION+1))
        BOT_SKELETON.nap()
