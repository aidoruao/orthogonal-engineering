# PIPELINE_LOGGER.py
# Universal logging configuration for all pipeline scripts
# Import this instead of configuring logging in each script

import logging
import sys

# CONFIGURE LOGGING ONCE - UTF-8 file output
logging.basicConfig(
    filename='pipeline_run_log.txt',
    level=logging.INFO,
    encoding='utf-8',
    format='%(asctime)s - %(message)s'
)

def safe_print(message):
    """
    Console-safe print that handles Unicode gracefully.
    For detailed Unicode output, use logging.info() instead.
    """
    try:
        print(message)
    except UnicodeEncodeError:
        # Fallback: strip non-ASCII characters
        print(message.encode('ascii', errors='ignore').decode('ascii'))

# Export functions
__all__ = ['logging', 'safe_print']
