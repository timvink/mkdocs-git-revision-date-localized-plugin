"""
Custom jinja2 filters
"""

import timeago

def to_timeago(date, locale = "en"):
    return timeago.format(date, locale = locale)
