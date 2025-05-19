# FILE: chat.py

import logging
import asyncio
import os
import uuid
from pathlib import Path

from flexiai.config.logging_config import setup_logging
from flexiai.controllers.cli_chat_controller import CLIChatController

USER_ID_FILE = Path.home() / ".flexiai_user_id"

async def main():
    # ─── Logging Setup ───────────────────────────────────────────────
    setup_logging(
        root_level=logging.DEBUG,
        file_level=logging.DEBUG,
        console_level=logging.ERROR,
        enable_file_logging=True,
        enable_console_logging=False
    )
    logger = logging.getLogger(__name__)
    logger.info("[chat.py] CLI Chat application started.")
    
    # ─── Predefined assistant ID ─────────────────────────────────────
    assistant_id = 'asst_OALzK1cjDBAH5hceWAGjqmBM'  # Columbus

    # ─── Determine or generate a user_id for this session ────────────
    # 1) Check file
    if USER_ID_FILE.exists():
        user_id = USER_ID_FILE.read_text().strip()
        logger.debug(f"[chat.py] Loaded persisted user_id from {USER_ID_FILE}: {user_id}")
    else:
        # 2) Fallback to env var
        user_id = os.getenv("FLEXIAI_USER_ID")
        if not user_id:
            # 3) Generate new
            user_id = str(uuid.uuid4())
        # Persist for future runs
        try:
            USER_ID_FILE.write_text(user_id)
            logger.debug(f"[chat.py] Persisted new user_id to {USER_ID_FILE}")
        except Exception as e:
            logger.warning(f"[chat.py] Failed to write user_id file: {e}")

    # Log final choice
    logger.info(f"[chat.py] Using user_id: {user_id}")

    # ─── Async‐construct the controller (builds client & thread) ─────
    chat_controller = await CLIChatController.create_async(
        assistant_id,
        user_id
    )

    # ─── Start the interactive loop ─────────────────────────────────
    await chat_controller.run_chat_loop(
        user_name="👤 You",
        assistant_name="🌺 Assistant"
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting chat due to keyboard interrupt.")
    except Exception as e:
        logging.getLogger(__name__).error(
            f"[chat.py] Unexpected error at startup: {e}",
            exc_info=True
        )
