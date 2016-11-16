import logging
import os
import random
from datetime import datetime, timedelta
from enum import Enum

import requests

import util


WEATHER_ROOT = "http://api.openweathermap.org/data/2.5/weather"

with open(os.path.join(util.HERE, "api_key"), "r") as f:
    API_KEY = f.read().strip()


OWNER_URL = "https://github.com/andrewmichaud/randweather_bot"
USER_AGENT = "randweather_twitterbot/" + util.VERSION + "(" + OWNER_URL + ")"
HEADERS = {"User-Agent": USER_AGENT}

LOG = logging.getLogger("root")


def produce_status():
    """Produce status from the current weather somewhere."""
    json = get_weather_from_api()
    LOG.debug("Full JSON from weather API: {}".format(json))

    name_json = get_weather_from_api()
    place_name = name_json["name"]
    LOG.info("Producing weather lie for {}".format(place_name))

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
            "The current wind speed in {} is {} meters/second.",
            "The wind speed in {} is currently {} m/s.",
            "The wind speed in {} is {} m/s at this moment.",
        ]).format(place_name, wind_speed)

    else:
        # Close enough?
        imperial_speed = round(wind_speed * 2.237, 2)
        return random.choice([
            "The current wind speed in {} is {} miles per hour.",
            "The wind speed in {} is {} mph.",
            "The wind speed in {} is {} mph, last I checked.",
        ]).format(place_name, imperial_speed)


def cloudiness_handle(place_name, json):
    """Handle a status about clouds."""
    LOG.info("Producing a status on cloudiness.")
    cloudiness = float(json["clouds"]["all"])

    # Provide either a status with the exact cloudiness, or one describing roughly how cloudy it
    # is.
    if random.choice([True, False]):
        return random.choice([
            "The cloudiness in {} is {}%, currently.".format(place_name, cloudiness),
            "It is {}% cloudy in {} right now.".format(cloudiness, place_name),
        ])

    else:
        # Rough encoding of http://forecast.weather.gov/glossary.php?word=sky%20condition.
        # I don't know if OWM's cloudiness percent is supposed to translate to Oktas, but whatever.
        # Clear/Sunny - 0/8 okta.
        if cloudiness < 12.5:
            return random.choice([
                "It's clear in {} right now ({}% cloudiness).",
                "There are almost no clouds in {} right now ({}% cloudiness).",
                "Good luck finding clouds in {} right now ({}% cloudiness).",
            ]).format(place_name, cloudiness)

        # Mostly Clear/Mostly Sunny - 1/8 to 2.5/8 okta.
        elif cloudiness >= 12.5 and cloudiness < 31.25:
            return random.choice([
                "It's not very cloudy in {} right now ({}% cloudiness).",
                "There are not many clouds in {} right now ({}% cloudiness).",
                "It's very clear in {} right now ({}% cloudiness).",
                "It's mostly clear in {} right now ({}% cloudiness).",
            ]).format(place_name, cloudiness)

        # Partly Cloudy/Partly Sunny - 2.5/8 to 4.5/8 okta.
        elif cloudiness >= 31.25 and cloudiness < 56.25:
            return random.choice([
                "It's kinda cloudy in {} right now ({}% cloudiness).",
                "There are a few clouds in {} right now ({}% cloudiness).",
                "It's partly clear in {} right now ({}% cloudiness).",
                "It's partly cloudy in {} right now ({}% cloudiness).",
            ]).format(place_name, cloudiness)

        # Mostly Cloudy/Considerable Cloudiness - 4.5/8 to 7.5/8 okta.
        elif cloudiness >= 56.25 and cloudiness < 93.75:
            return random.choice([
                "It's very cloudy in {} right now ({}% cloudiness).",
                "It's mostly cloudy in {} right now ({}% cloudiness).",
                "There are a bunch of clouds in {} right now ({}% cloudiness).",
                "It's not very clear in {} right now ({}% cloudiness).",
                "Wow! There are a lot of clouds in {} right now ({}% cloudiness).",
            ]).format(place_name, cloudiness)

        # Cloudy - 7.5/8 okta to 8/8 okta.
        else:
            return random.choice([
                "It's cloudy in {} right now ({}% cloudiness).",
                "It's not clear in {} right now ({}% cloudiness).",
                "There are a ton of clouds in {} right now ({}% cloudiness).",
            ]).format(place_name, cloudiness)


def humidity_handle(place_name, json):
    """Handle a status about humidity."""
    LOG.info("Producing a status on humidity.")
    humidity = float(json["main"]["humidity"])

    # Provide either a status with the exact humidity, or one describing roughly how wet it is.
    if random.choice([True, False]):
        return random.choice([
            "The humidity in {} is {}%, currently.".format(place_name, humidity),
            "It is {}% humid in {} right now.".format(humidity, place_name),
        ])

    else:
        if humidity < 40:
            return random.choice([
                "It is very dry in {} right now ({}% humidity).",
                "It's very dry in {} ({}% humidity).",
            ]).format(place_name, humidity)

        elif humidity >= 40 and humidity < 75:
            return random.choice([
                "It's mildly humid in {} ({}% humid).",
                "It's kinda wet in {} ({}% humid).",
            ]).format(place_name, humidity)

        else:
            return random.choice([
                "It's very humid in {} ({}% humid).",
                "It's quite wet in {} right now ({}% humid).",
            ]).format(place_name, humidity)


def temp_handle(place_name, json):
    """Handle a status about the temperature."""
    LOG.info("Producing a status on temperature.")
    temp = json["main"]["temp"]

    if random.choice(range(2)) > 0:
        celsius_temp = round(float(temp) - 273.15, 2)
        return "It's {} °C in {} right now.".format(celsius_temp, place_name)

    else:
        fahrenheit_temp = round((float(temp) * (9.0 / 5)) - 459.67, 2)
        return "It's {} °F in {}.".format(fahrenheit_temp, place_name)


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
            "The {} is happening now in {}.",
            "You can watch the {} now in {}.",
            "You're missing the {} in {}.",
        ]).format(sunthing, place_name)

    if now > sunthing_datetime:
        return random.choice([
            "The last {} in {} happened at {} UTC.",
            "Sorry, you missed the {} in {}, it was at {}.",
            "You could have seen the {} in {}. It was at {}.",
        ]).format(sunthing, place_name, formatted_datetime)

    else:
        return random.choice([
            "The next {} in {} will happen at {} UTC.",
            "You could watch the {} in {} at {} UTC.",
        ]).format(sunthing, place_name, formatted_datetime)


# Wrappers around Open Weather Map API, to get weather info.
def get_weather_from_api():
    """Get weather blob for a random city from the openweathermap API."""
    zip = util.random_line("ZIP_CODES")
    LOG.info("Random zip code is {}.".format(zip))
    url = get_zip_url(zip)

    weather = openweathermap_api_call(url)

    return weather.json()


def get_zip_url(zip):
    """Format a URL to get weather by zip code from the OpenWeatherMap API."""
    return "{}?zip={},us&appid={}".format(WEATHER_ROOT, zip, API_KEY)


# Actual rate-limited API calls here.
# Be cautious, because this is the second app I have behind this API_KEY.
@util.rate_limited(900)
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
