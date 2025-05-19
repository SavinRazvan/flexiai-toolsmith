# FILE: flexiai/utils/context_utils.py

"""
Context utilities for managing token-based context window limits.
"""

import logging
import tiktoken

logger = logging.getLogger(__name__)


def return_context(
    text: str,
    max_tokens: int = 124000,
    model: str = "gpt-4o-mini"
) -> str:
    """
    Truncate a text string so that its token count does not exceed the specified max_tokens
    for the given model. If the text is longer than max_tokens, returns the last portion of the
    text that fits into max_tokens tokens, preserving as much context as possible.

    Args:
        text: The input string to be truncated.
        max_tokens: Maximum number of tokens allowed (default: 124000 for 128K context minus headroom).
        model: The model name for determining the token encoding (default: 'gpt-4o-mini').

    Returns:
        A substring of `text` whose encoding is <= max_tokens tokens. If an error occurs during
        encoding/decoding, returns the original text.
    """
    try:
        # Attempt to get the encoding for the specified model
        enc = tiktoken.encoding_for_model(model)
    except Exception as e:
        logger.warning(f"Encoding for model '{model}' unavailable, falling back: {e}")
        try:
            enc = tiktoken.get_encoding("cl100k_base")
        except Exception as e2:
            logger.error(f"Fallback encoding failed: {e2}", exc_info=True)
            return text

    try:
        tokens = enc.encode(text)
    except Exception as e:
        logger.error(f"Tokenization failed for model '{model}': {e}", exc_info=True)
        return text

    token_count = len(tokens)
    logger.debug(f"Text token count: {token_count}, max allowed: {max_tokens}")

    # If within limit, return original text
    if token_count <= max_tokens:
        return text

    # Otherwise, truncate to the last max_tokens tokens
    try:
        truncated_tokens = tokens[-max_tokens:]
        truncated_text = enc.decode(truncated_tokens)
        logger.info(f"Truncated text from {token_count} to {max_tokens} tokens")
        return truncated_text
    except Exception as e:
        logger.error(f"Decoding truncated tokens failed: {e}", exc_info=True)
        # Fall back to returning the tail substring of the raw text
        return text[-max_tokens * 4 :]  # approximate character fallback
