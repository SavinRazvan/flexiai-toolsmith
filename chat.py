# FILE: chat.py

import logging
import asyncio

from flexiai.config.models       import GeneralSettings
from flexiai.config.logging_config import setup_logging
from flexiai.controllers.cli_chat_controller import CLIChatController

async def main():
    setup_logging(
        root_level=logging.DEBUG,
        file_level=logging.DEBUG,
        console_level=logging.ERROR,
        enable_file_logging=True,
        enable_console_logging=False,
    )
    logger = logging.getLogger(__name__)
    logger.info("[chat.py] CLI Chat application started.")

    # load & validate all required settings
    settings = GeneralSettings()

    # will always be present (else Pydantic already errored)
    assistant_id = settings.ASSISTANT_ID
    user_id      = settings.USER_ID

    logger.info(f"Using assistant_id={assistant_id} and user_id={user_id}")

    # build controller & run loop
    chat_controller = await CLIChatController.create_async(
        assistant_id,
        user_id
    )
    await chat_controller.run_chat_loop(
        user_name=settings.USER_NAME,
        assistant_name=settings.ASSISTANT_NAME
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting chat due to keyboard interrupt.")
    except Exception as e:
        logging.getLogger(__name__).error(
            f"Unexpected error at startup: {e}", exc_info=True
        )
