import json
import shutil
import tempfile

from seed import populate_quotes
from unittest import mock


def sample_quotes(quote_type):
    with open(f"test/sample_{quote_type}_quotes.json", "r") as json_file:
        json_data = json.load(json_file)
    return json_data


def test_populate_quotes(mocker):
    temp_dir = tempfile.TemporaryDirectory()

    try:
        mocker.patch("seed.QUOTES_PER_DAY", 5),
        mocker.patch(
            "seed.get_random_quotes", return_value=sample_quotes("human")
        )
        mocker.patch(
            "seed.generate_ai_quotes", return_value=sample_quotes("ai")
        )
        mocker.patch("seed.CACHE_PATH", temp_dir.name)
        result = populate_quotes()
        assert result
    finally:
        temp_dir.cleanup()
