import shutil
import tempfile

from seed import populate_quotes
from unittest import mock


EXAMPLE_QUOTES = []
EXAMPLE_AI_QUOTES = []


def test_populate_quotes(mocker):
    temp_dir = tempfile.mkdtemp()

    try:
        mocker.patch("seed.get_random_quotes", return_value=EXAMPLE_QUOTES)
        mocker.patch("seed.generate_ai_quotes", return_value=EXAMPLE_AI_QUOTES)
        mocker.patch("seed.CACHE_PATH", side_effect=temp_dir)
        result = populate_quotes()
        assert result
    finally:
        shutil.rmtree(temp_dir)
