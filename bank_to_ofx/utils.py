import re

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
