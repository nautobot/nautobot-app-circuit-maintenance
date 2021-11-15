"""Enumerations for use in nautobot-circuit-maintenance plugin."""

from enum import Enum


class MessageProcessingStatus(str, Enum):
    """Possible processing-status tags for email messages."""

    # Unable to process
    UNKNOWN_PROVIDER = "unknown-provider"
    # Error encountered in parsing
    PARSING_FAILED = "parsing-failed"
    # Identified as irrelevant to circuit-maintenance
    IGNORED = "ignored"
    # Successfully parsed
    PARSED = "parsed"
    # Out of sequence
    OUT_OF_SEQUENCE = "out-of-sequence"
    # Refers to circuits that Nautobot doesn't know about
    UNKNOWN_CIDS = "unknown-cids"
