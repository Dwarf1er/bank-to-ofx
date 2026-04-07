from .desjardins import DesjardinsParser
from .wealthsimple import WealthsimpleParser

PARSERS = {
    "desjardins": DesjardinsParser,
    "wealthsimple": WealthsimpleParser,
}
