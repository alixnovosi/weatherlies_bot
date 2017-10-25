"""Main class to run randomweather_bot."""

import os
import random
import time

import botskeleton
import tweepy

import weather_gen

# Delay between tweets in seconds.
DELAY = 2000
DELAY_VARIATION = 400

if __name__ == "__main__":
    SECRETS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "SECRETS")
    api = botskeleton.BotSkeleton(SECRETS_DIR, bot_name="weatherlies_bot")

    LOG = botskeleton.set_up_logging()

    while True:
        LOG.info("Sending a weather lie.")
        weather = weather_gen.produce_status()
        LOG.info(f"Sending:\n {weather}")

        api.send(weather)

        LOG.info(f"Sleeping for {DELAY} seconds.")
        time.sleep(random.choice(range(DELAY-DELAY_VARIATION, DELAY+DELAY_VARIATION+1)))
