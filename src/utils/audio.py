import os
import logging

logger = logging.getLogger(__name__)

def cleanup_file(filename: str):
    """Deletes the temporary audio file."""
    try:
        if os.path.exists(filename):
            os.remove(filename)
            logger.info(f"Cleaned up {filename}")
    except Exception as e:
        logger.error(f"Cleanup Error: {e}")
