from os import path
from setuptools import setup, find_packages

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, "VERSION"), encoding="utf-8") as f:
    VERSION = f.read().strip()

setup(author="Andrew Michaud",
      author_email="bots+weatherlies@mail.andrewmichaud.com",

      entry_points={
          "console_scripts": ["weatherlies_bot = weatherlies_bot.__main__:main"]
      },

      install_requires=["weatherbotskeleton>=1.0.6", "requests>=2.18.4"],
      python_requires=">=3.6",

      license="BSD3",

      name="weatherlies_bot",

      packages=find_packages(),

      # Project"s main homepage
      url="https://github.com/andrewmichaud/weatherlies_bot",

      version=VERSION)
