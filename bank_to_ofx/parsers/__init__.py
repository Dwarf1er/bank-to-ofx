from .desjardins import DesjardinsParser
from .desjardins_credit import DesjardinsCreditCardParser
from .wealthsimple import WealthsimpleParser

PARSERS = {
    "desjardins": DesjardinsParser,
    "desjardins-credit": DesjardinsCreditCardParser,
    "wealthsimple": WealthsimpleParser,
}
