import pytest

import app as flask_app


@pytest.fixture
def client():
    flask_app.app.config.update(TESTING=True)
    flask_app.CURRENT.update(puzzle=None, solution=None, hints_used=0)
    with flask_app.app.test_client() as test_client:
        yield test_client
    flask_app.CURRENT.update(puzzle=None, solution=None, hints_used=0)


@pytest.fixture
def solved_board():
    return [
        [((row * 3 + row // 3 + col) % 9) + 1 for col in range(9)]
        for row in range(9)
    ]