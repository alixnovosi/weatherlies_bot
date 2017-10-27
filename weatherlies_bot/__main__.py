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
    api = botskeleton.BotSkeleton(SECRETS_DIR, bot_name="weatherlies_bot")

    LOG = botskeleton.set_up_logging()

    while True:
        try:
            weather = weather_gen.produce_status()
        except Exception as e:
            api.send_dm_sos(f"Bot {api.bot_name} had an error it can't recover from!\n{e}")
            raise

        LOG.info(f"Sending:\n {weather}")

        try:
            api.send(weather)

        except tweepy.TweepError as e:
            if e.message == "Status is a duplicate.":
                LOG.warning("Duplicate status.")
                continue
            else:
                api.send_dm_sos(f"Bot {api.bot_name} had an error it can't recover from!\n{e}")
                raise

        LOG.info(f"Sleeping for {DELAY} seconds.")
        time.sleep(random.choice(range(DELAY-DELAY_VARIATION, DELAY+DELAY_VARIATION+1)))
