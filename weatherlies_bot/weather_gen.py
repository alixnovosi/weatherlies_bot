import logging
import random
from datetime import datetime, timedelta
from enum import Enum
from os import path

import botskeleton
import requests


HERE = path.abspath(path.dirname(__file__))
SECRETS_DIR = path.join(HERE, "SECRETS")

WEATHER_ROOT = "http://api.openweathermap.org/data/2.5/weather"

with open(path.join(SECRETS_DIR, "api_key"), "r") as f:
    API_KEY = f.read().strip()

OWNER_URL = "https://github.com/andrewmichaud/randweather_bot"
with open(path.join(path.join(HERE, ".."), "VERSION")) as f:
    VERSION = f.read().strip()

USER_AGENT = f"randweather_twitterbot/{VERSION} ({OWNER_URL})"
HEADERS = {"User-Agent": USER_AGENT}

LOG = logging.getLogger("root")


def produce_status():
    """Produce status from the current weather somewhere."""
    json = get_weather_from_api()
    LOG.debug(f"Full JSON from weather API: {json}")

    name_json = get_weather_from_api()
    place_name = name_json["name"]
    LOG.info(f"Producing weather lie for {place_name}")

    thing = random.choice(list(WeatherThings))

    if thing == WeatherThings.WIND_SPEED:
        return windspeed_handle(place_name, json)

    elif thing == WeatherThings.CLOUDINESS:
        return cloudiness_handle(place_name, json)

    elif thing == WeatherThings.HUMIDITY:
        return humidity_handle(place_name, json)

    elif thing == WeatherThings.TEMP:
        return temp_handle(place_name, json)

    elif thing == WeatherThings.SUNRISE or thing == WeatherThings.SUNSET:
        return sunthing_handle(thing, place_name, json)


# Individual status generators for different kinds of weather stuff.
def windspeed_handle(place_name, json):
    """Handle a status about wind speed."""
    LOG.info("Producing a status on wind speed.")
    wind_speed = float(json["wind"]["speed"])

    # Either show in m/s or mph.
    if random.choice([True, False]):
        return random.choice([
            f"The current wind speed in {place_name} is {wind_speed} meters/second.",
            f"The wind speed in {place_name} is currently {wind_speed} m/s.",
            f"The wind speed in {place_name} is {wind_speed} m/s at this moment.",
        ])

    else:
        # Close enough?
        imperial_speed = round(wind_speed * 2.237, 2)
        return random.choice([
            f"The current wind speed in {place_name} is {imperial_speed} miles per hour.",
            f"The wind speed in {place_name} is {imperial_speed} mph.",
            f"The wind speed in {place_name} is {imperial_speed} mph last I checked.",
        ])


def cloudiness_handle(place_name, json):
    """Handle a status about clouds."""
    LOG.info("Producing a status on cloudiness.")
    cloudiness = float(json["clouds"]["all"])

    # Provide either a status with the exact cloudiness, or one describing roughly how cloudy it
    # is.
    if random.choice([True, False]):
        return random.choice([
            f"The cloudiness in {place_name} is {cloudiness}%, currently.",
            f"It is {cloudiness}% cloudy in {place_name} right now.",
        ])

    else:
        # Rough encoding of http://forecast.weather.gov/glossary.php?word=sky%20condition.
        # I don't know if OWM's cloudiness percent is supposed to translate to Oktas, but whatever.
        # Clear/Sunny - 0/8 okta.
        if cloudiness < 12.5:
            cloudiness_phrase = random.choice([
                "It's clear",
                "There are almost no clouds",
                "Good luck finding clouds",
            ])

        # Mostly Clear/Mostly Sunny - 1/8 to 2.5/8 okta.
        elif cloudiness >= 12.5 and cloudiness < 31.25:
            cloudiness_phrase = random.choice([
                "It's not very cloudy",
                "There are not many clouds",
                "It's very clear",
                "It's mostly clear",
            ])

        # Partly Cloudy/Partly Sunny - 2.5/8 to 4.5/8 okta.
        elif cloudiness >= 31.25 and cloudiness < 56.25:
            cloudiness_phrase = random.choice([
                "It's kinda cloudy",
                "There are a few clouds",
                "It's partly clear",
                "It's partly cloudy",
            ])

        # Mostly Cloudy/Considerable Cloudiness - 4.5/8 to 7.5/8 okta.
        elif cloudiness >= 56.25 and cloudiness < 93.75:
            cloudiness_phrase = random.choice([
                "It's very cloudy",
                "It's mostly cloudy",
                "There are a bunch of clouds",
                "It's not very clear",
                "Wow! There are a lot of clouds",
            ])

        # Cloudy - 7.5/8 okta to 8/8 okta.
        else:
            cloudiness_phrase = random.choice([
                "It's cloudy",
                "It's not clear",
                "There are a ton of clouds",
            ])

    return f"{cloudiness_phrase} in {place_name}{get_time_descriptor()} " +\
            f"({cloudiness}% cloudiness)."


def humidity_handle(place_name, json):
    """Handle a status about humidity."""
    LOG.info("Producing a status on humidity.")
    humidity = float(json["main"]["humidity"])

    # Provide either a status with the exact humidity, or one describing roughly how wet it is.
    if random.choice([True, False]):
        return random.choice([
            f"The humidity in {place_name} is {humidity}%, currently.",
            f"It is {humidity}% humid in {place_name} right now.",
        ])

    else:
        if humidity < 40:
            return random.choice([
                f"It is very dry in {place_name} right now ({humidity}% humidity).",
                f"It's very dry in {place_name} ({humidity}% humidity).",
            ])

        elif humidity >= 40 and humidity < 75:
            return random.choice([
                f"It's mildly humid in {place_name} ({humidity}% humid).",
                f"It's kinda wet in {place_name} ({humidity}% humid).",
            ])

        else:
            return random.choice([
                f"It's very humid in {place_name} ({humidity}% humid).",
                f"It's quite wet in {place_name} right now ({humidity}% humid).",
            ])


def temp_handle(place_name, json):
    """Handle a status about the temperature."""
    LOG.info("Producing a status on temperature.")
    temp = json["main"]["temp"]

    if random.choice(range(2)) > 0:
        celsius_temp = round(float(temp) - 273.15, 2)
        return f"It's {celsius_temp} °C in {place_name} right now."

    else:
        fahrenheit_temp = round((float(temp) * (9.0 / 5)) - 459.67, 2)
        return f"It's {fahrenheit_tmep} °F in {place_name}."


def sunthing_handle(thing, place_name, json):
    """Handle a status about the sunset or sunrise."""
    if thing == WeatherThings.SUNRISE:
        LOG.info("Producing a status on the sunrise.")
        sunthing_time = json["sys"]["sunrise"]
        sunthing = "sunrise"

    else:
        LOG.info("Producing a status on the sunset.")
        sunthing_time = json["sys"]["sunset"]
        sunthing = "sunset"

    sunthing_datetime = datetime.utcfromtimestamp(int(sunthing_time))
    formatted_datetime = sunthing_datetime.strftime("%H:%M:%S")

    now = datetime.utcnow()

    if abs(now - sunthing_datetime) > timedelta(seconds=60) == sunthing_datetime:
        return random.choice([
            f"The {sunthing} is happening now in {place_name}.",
            f"You can watch the {sunthing} now in {place_name}.",
            f"You're missing the {sunthing} in {place_name}.",
        ])

    if now > sunthing_datetime:
        return random.choice([
            f"The last {sunthing} in {place_name} happened at {formatted_datetime} UTC.",
            f"Sorry, you missed the {sunthing} in {place_name}, it was at {formatted_datetime}.",
            f"You could have seen the {sunthing} in {place_name}. It was at {formatted_datetime}.",
        ])

    else:
        return random.choice([
            f"The next {sunthing} in {place_name} will happen at {formatted_datetime} UTC.",
            f"You could watch the {sunthing} in {place_name} at {formatted_datetime} UTC.",
        ])

def get_time_descriptor():
    """Get a phrase like "currently" or "right now", or nothing at all. Provides leading space."""
    return random.choice([" currently", " right now", " this moment", ""])

# Wrappers around Open Weather Map API, to get weather info.
def get_weather_from_api():
    """Get weather blob for a random city from the openweathermap API."""
    zip = botskeleton.random_line(path.join(HERE, "ZIP_CODES"))
    LOG.info(f"Random zip code is {zip}.")
    url = get_zip_url(zip)

    weather = openweathermap_api_call(url)

    return weather.json()


def get_zip_url(zip):
    """Format a URL to get weather by zip code from the OpenWeatherMap API."""
    return f"{WEATHER_ROOT}?zip={zip},us&appid={API_KEY}"


# Actual rate-limited API calls here.
# Be cautious, because this is the second app I have behind this API_KEY.
@botskeleton.rate_limited(900)
def openweathermap_api_call(url):
    """Perform a rate-limited API call."""
    return requests.get(url)


class WeatherThings(Enum):
    """Kinds of weather we can pull out of a weather blob from the OWM API."""
    WIND_SPEED = 000
    CLOUDINESS = 100
    SUNRISE = 200
    SUNSET = 300
    HUMIDITY = 400
    TEMP = 500
