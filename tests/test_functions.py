from typing import Any

from src.functions import filter_aeroplanes, get_aeroplanes_by_altitude, get_top_aeroplanes, sort_aeroplanes


def test_filter_aeroplanes(aeroplanes_1: list[Any]) -> None:
    assert [plane.country for plane in filter_aeroplanes(aeroplanes_1, ["China"])] == ["China"]


def test_get_aeroplanes_by_altitude(aeroplanes_1: list[Any]) -> None:
    assert [plane.geo_altitude for plane in get_aeroplanes_by_altitude(aeroplanes_1, "1-2")] == [1, 2]


def test_sort_aeroplanes(aeroplanes_1: list[Any]) -> None:
    assert sort_aeroplanes(aeroplanes_1) == aeroplanes_1


def test_get_top_aeroplanes(aeroplanes_1: list[Any]) -> None:
    assert get_top_aeroplanes(aeroplanes_1, 2) == aeroplanes_1[:2]
