from .desjardins import DesjardinsParser
from .desjardins_credit import DesjardinsCreditCardParser
from .wealthsimple import WealthsimpleParser
from .wealthsimple_credit import WealthsimpleCreditCardParser

PARSERS = {
    "desjardins": DesjardinsParser,
    "desjardins-credit": DesjardinsCreditCardParser,
    "wealthsimple": WealthsimpleParser,
    "wealthsimple-credit": WealthsimpleCreditCardParser,
}
