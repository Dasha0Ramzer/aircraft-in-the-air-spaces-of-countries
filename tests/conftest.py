from typing import Any

import pytest

from src.utils import Aeroplane, JSONSaver


@pytest.fixture
def aeroplanes_1() -> list[Any]:
    var = {
        "time": 1,
        "states": [
            ["test_1", "test_1", "China", 1, 1, 1, 1, 1, False, 1, 1, 1, None, 1, "2061", False, 0],
            ["test_2", "test_2", "Russia", 2, 2, 2, 2, 2, False, 2, 2, 2, None, 2, "2061", False, 0],
            ["test_3", "test_3", "Canada", 3, 3, 3, 3, 3, False, 3, 3, 3, None, 3, "2061", False, 0],
        ],
    }
    pl_1 = Aeroplane.cast_to_object_list(var)
    return pl_1


@pytest.fixture
def json_saver() -> "JSONSaver":
    return JSONSaver()


@pytest.fixture
def aeroplane() -> "Aeroplane":
    aeroplane_data = ["test_1", "test_1", "China", 1, 1, 1, 1, 1, False, 1, 1, 1, None, 1, "2061", False, 0]
    return Aeroplane(aeroplane_data)
