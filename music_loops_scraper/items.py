# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from dataclasses import dataclass


@dataclass
class MusicLoopItem:
    name: str
    bpm: int
    genre: str
    key: str
    description: str
    url: str


@dataclass
class CategoryLoopsItem:
    cat_name: str
    loops: list[MusicLoopItem]
