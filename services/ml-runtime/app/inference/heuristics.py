import re

HIGH_RISK_KEYWORDS = (
    "urgent",
    "verify",
    "suspend",
    "confirm",
    "click",
    "prize",
    "winner",
    "claim",
    "account",
    "password",
    "security",
    "alert",
    "congratulations",
    "free",
    "limited time",
    "act now",
    "guarantee",
)

URL_PATTERN = re.compile(
    r"http[s]?://(?:[a-zA-Z]|[0-9]|[$\-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)


def detect_urls(text: str) -> list[str]:
    return URL_PATTERN.findall(text)


def detect_high_risk_keywords(text: str) -> list[str]:
    text_lower = text.lower()
    return [keyword for keyword in HIGH_RISK_KEYWORDS if keyword in text_lower]
