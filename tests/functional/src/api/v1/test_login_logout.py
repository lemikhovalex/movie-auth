import pytest

# All test coroutines will be treated as marked with this decorator.
pytestmark = pytest.mark.asyncio


async def test_films_check_no_films(pg_connection):
    pg_connection
