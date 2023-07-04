import logging
import requests
import openai
import typing as t
import tenacity

from pathlib import Path
from diskcache import Cache

parent_dir = Path(__file__).resolve().parent.parent
env_path = parent_dir / ".OPENAI_API_KEY"
openai.api_key_path = env_path

URL = "https://api.quotable.io/quotes/random"
CACHE_PATH = parent_dir / "cache"


def get_random_quotes(
    limit=1, maxLength=None, minLength=None, tags=None, authors=None
):
    """
    Retrieves random quotes from Quotable API.

    Args:
        limit (int): The maximum number of quotes to retrieve. Defaults to 1.
        maxLength (int): The maximum length of the quotes in characters.
        minLength (int): The minimum length of the quotes in characters.
        tags (list): A list of tags to filter the quotes by.
        authors (list): A list of authors to filter the quotes by.

    Returns:
        list or None: A list of randomly retrieved quotes in JSON format, or
            None if an error occurs.
    """
    params = {
        "limit": limit,
        "maxLength": maxLength,
        "minLength": minLength,
        "tags": tags,
        "author": authors,
    }

    response = requests.get(URL, params=params)

    if response.status_code == 200:
        quotes = response.json()
        return quotes
    else:
        logging.error(f"Error: {response.status_code}")
        return None


def generate_ai_quotes(quotes: t.List[dict]):
    """
    Generates summarized quotes from OpenAI API. Checks diskcache.Cache
    before querying the API.

    Args:
        quotes (list): A list of quotes to be summarized

    Returns:
        list: A list of AI-generated quotes in JSON format.
    """

    @tenacity.retry(
        wait=tenacity.wait_exponential(max=30),
        stop=tenacity.stop_after_attempt(4),
        retry=tenacity.retry_if_exception_type(Exception),
    )
    def _chat_completion_with_retry(messages):
        return openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )

    output = []

    messages = [
        {
            "role": "system",
            "content": (
                "I will give you a quote."
                "Summarize it with a witty sentence, in your own words."
            ),
        },
        None,
    ]

    with Cache(CACHE_PATH) as store:
        for quote in quotes:
            if quote["_id"] in store:
                output.append(store.get(quote["_id"]))
            else:
                messages[1] = {
                    "role": "user",
                    "content": quote["content"],
                }
                chat_completion = _chat_completion_with_retry(messages)
                stripped = (
                    chat_completion.choices[0]["message"]["content"]
                    .split("-")[0]
                    .replace('"', "")
                    .replace("!", ".")
                    .rstrip()
                )
                if stripped[-1] not in (".", "?"):
                    stripped += "."

                chat_completion.choices[0]["message"]["content"] = stripped
                output.append(chat_completion.choices[0]["message"])
                store.set(quote["_id"], chat_completion.choices[0]["message"])

    return output


def get_question_pairs():
    """
    Retrieves today's question pairs from a cache.

    Returns:
        list: A list of question pairs.
    """
    question_pairs = []
    with Cache(CACHE_PATH) as store:
        question_pairs = store.get("question_pairs")

    return question_pairs
