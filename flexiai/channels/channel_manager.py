# FILE: flexiai/channels/channel_manager.py

"""
Channel manager module.

Selects and instantiates active channels based on application settings.
"""

import logging
from flexiai.config.models import GeneralSettings
from flexiai.channels.cli_channel import CLIChannel
from flexiai.channels.redis_channel import RedisChannel
from flexiai.channels.quart_channel import QuartChannel

logger = logging.getLogger(__name__)


def get_active_channels() -> list:
    """Create channel instances according to the ACTIVE_CHANNELS setting.

    Reads the `ACTIVE_CHANNELS` environment variable (comma-separated list),
    and returns a list of the corresponding channel objects.

    Returns:
        list: A list of initialized BaseChannel instances. Unknown channel names
            are ignored, with a warning logged.
    """
    settings = GeneralSettings()
    channels_list = [ch.strip().lower() for ch in settings.ACTIVE_CHANNELS.split(",")]

    active_channels = []
    for channel in channels_list:
        if channel == "cli":
            active_channels.append(CLIChannel())
        elif channel == "redis":
            active_channels.append(RedisChannel())
        elif channel == "quart":
            active_channels.append(QuartChannel())
        else:
            logger.warning("Unknown channel '%s' specified in ACTIVE_CHANNELS", channel)

    return active_channels
