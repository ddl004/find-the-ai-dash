import logging
import numpy as np

from diskcache import Cache
from dash_app.quotes import get_random_quotes, generate_ai_quotes, CACHE_PATH
from dash_app.app import QUOTES_PER_DAY


def populate_quotes():
    """
    Creates question pairs of randomly shuffled question pairs from
    humans and AI, and updates the cache for today's questions.

    Returns:
        bool: True if the quotes are successfully populated and cached.
    """
    human_quotes = get_random_quotes(QUOTES_PER_DAY)
    ai_quotes = generate_ai_quotes(human_quotes)
    question_pairs = list(
        zip(
            [{**quote, "type": "human"} for quote in human_quotes],
            [{**quote, "type": "ai"} for quote in ai_quotes],
        )
    )
    # Shuffle the quotes
    for idx in range(QUOTES_PER_DAY):
        random_number = np.random.randint(0, 2)
        if random_number:
            question_pairs[idx] = [
                question_pairs[idx][1],
                question_pairs[idx][0],
            ]

    with Cache(CACHE_PATH) as store:
        store.set("question_pairs", question_pairs)
        logging.info(f"Loaded question pairs to cache: {question_pairs}")

    return True


if __name__ == "__main__":
    populate_quotes()
