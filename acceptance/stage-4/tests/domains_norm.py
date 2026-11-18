import re

_LABEL = re.compile(r"[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?")


def norm_domain(raw):
    """§4 normalisation; '' when invalid."""
    d = (raw or "").strip().lower()
    if d.endswith("."):
        d = d[:-1]
    if d.startswith("www."):
        d = d[4:]
    labels = d.split(".")
    if len(d) > 253 or len(labels) < 2 or not all(_LABEL.fullmatch(x) for x in labels):
        return ""
    return d
