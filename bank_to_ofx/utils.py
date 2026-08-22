import re
from collections import defaultdict


def assign_fitids(transactions):
    """
    Assign each transaction a FITID derived from its date and a per-day
    counter, unique within the account. Keeps FITIDs stable across reruns
    (so accounting software recognizes repeat imports as duplicates) and
    avoids collisions when merging transactions from multiple statement
    files that each numbered their own transactions starting at 1.
    """
    counters = defaultdict(int)
    for t in transactions:
        key = t["date"].strftime("%Y%m%d")
        counters[key] += 1
        t["seq"] = f"{key}-{counters[key]:03d}"


def to_kebab_case(s: str) -> str:
    """
    Convert any string to lowercase kebab-case:
    - spaces, underscores, and non-alphanumerics replaced by '-'
    - multiple dashes collapsed
    """
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")
