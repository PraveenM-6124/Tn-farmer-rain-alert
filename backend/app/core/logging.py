"""Structured logging configuration with automatic PII masking."""

import logging
import re
import sys

# Regex matching Indian phone numbers with optional +91 and spacing/hyphens
INDIAN_PHONE_REGEX = re.compile(r"(\+91[\-\s]?)?([6-9]\d{9})")


def mask_pii(text: str) -> str:
    """Mask sensitive PII such as phone numbers in text."""
    if not isinstance(text, str):
        return text

    def replacer(match: re.Match[str]) -> str:
        num = match.group(2)
        masked_num = f"******{num[-4:]}"
        prefix = match.group(1) or ""
        return f"{prefix}{masked_num}"

    return INDIAN_PHONE_REGEX.sub(replacer, text)


class PIIMaskingFilter(logging.Filter):
    """Logging filter to mask phone numbers and PII in all emitted records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = mask_pii(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {
                    k: (mask_pii(v) if isinstance(v, str) else v)
                    for k, v in record.args.items()
                }
            elif isinstance(record.args, tuple):
                record.args = tuple(
                    mask_pii(arg) if isinstance(arg, str) else arg
                    for arg in record.args
                )
        return True


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Initialize structured application logger with PII masking."""
    logger = logging.getLogger("tn_farmer")
    logger.setLevel(level)

    # Avoid duplicate handlers on re-init
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        handler.addFilter(PIIMaskingFilter())
        logger.addHandler(handler)

    return logger


logger = setup_logging()
