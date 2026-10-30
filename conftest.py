from contextlib import closing

import pytest

from inventory_db import connect, initialize_database


@pytest.fixture
def db():
    with closing(connect(":memory:")) as connection:
        initialize_database(connection)
        yield connection