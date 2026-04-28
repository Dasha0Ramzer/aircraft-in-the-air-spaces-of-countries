import json
import os
from typing import Any
from unittest.mock import MagicMock, mock_open, patch

import pytest
import requests_mock

from src.utils import Aeroplane, AeroplanesAPI, JSONSaver


def test_constructor_initialization() -> None:
    obj = AeroplanesAPI()
    assert obj._openstreetmap_url == "https://nominatim.openstreetmap.org/search"
    assert obj._opensky_url == "https://opensky-network.org/api/states/all?"
    assert obj._aeroplanes is None


def test_connect_to_api_success() -> None:
    with requests_mock.Mocker() as m:
        # Успешный ответ от API
        m.get("http://example.com", json={"key": "value"}, status_code=200)
        result = AeroplanesAPI._connect_to_api("http://example.com", {"param": "value"})
        assert result == {"key": "value"}


def test_connect_to_api_error() -> None:
    with requests_mock.Mocker() as m:
        # Ответ с ошибкой от API
        m.get("http://example.com", status_code=404)
        try:
            AeroplanesAPI._connect_to_api("http://example.com", {"param": "value"})
        except Exception as e:
            assert str(e) == "Ошибка при подключении к API"


def test_get_aeroplanes() -> None:
    api = AeroplanesAPI()

    with requests_mock.Mocker() as m:
        m.get(api._openstreetmap_url, json=[{"boundingbox": ["1", "2", "3", "4"]}], status_code=200)
        m.get(api._opensky_url, json={"states": []}, status_code=200)

        api.get_aeroplanes("Russia")

        assert api._aeroplanes == {"states": []}


def test_get_aeroplanes_error(capsys) -> None:
    api = AeroplanesAPI()
    api.get_aeroplanes("123")

    captured = capsys.readouterr()
    assert "Данные для страны 123 не найдены." in captured.out


def test_validate_velocity(aeroplanes_1: list[Any]) -> None:
    with pytest.raises(ValueError, match="Скорость не может быть отрицательной"):
        Aeroplane._validate_velocity(-100)


def test_validate_altitude(aeroplanes_1: list[Any]) -> None:
    with pytest.raises(ValueError, match="Высота не может быть отрицательной"):
        Aeroplane._validate_altitude(-100)


def test_lt(aeroplanes_1: list[Any]) -> None:
    assert aeroplanes_1[1] < aeroplanes_1[2]


def test_gt(aeroplanes_1: list[Any]) -> None:
    assert not aeroplanes_1[1] > aeroplanes_1[2]


def test_eq(aeroplanes_1: list[Any]) -> None:
    assert not aeroplanes_1[1] == aeroplanes_1[2]


def test_to_dict(aeroplanes_1: list[Any]) -> None:
    assert aeroplanes_1[1].to_dict() == {
        "ICAO24": "test_2",
        "callsign": "test_2",
        "country": "Russia",
        "geo_altitude": 2,
        "on_ground": False,
        "velocity": 2,
    }


def test_json_saver() -> None:
    saver_default = JSONSaver()
    expected_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data", "aeroplanes.json"))
    assert saver_default._filename == expected_path


def test_load_data_file_exists() -> None:
    data = [{"key": "value"}]
    json_data = json.dumps(data)

    with patch("builtins.open", mock_open(read_data=json_data)):
        saver = JSONSaver("dummy_file.json")
        result = saver._load_data()
        assert result == data


def test_load_data_file_not_found() -> None:
    with patch("builtins.open", side_effect=FileNotFoundError):
        saver = JSONSaver("non_existent_file.json")
        result = saver._load_data()
        assert result == []


@patch("builtins.open", new_callable=mock_open)
@patch("os.makedirs")
def test_save_data(mocked_makedirs: MagicMock, mocked_open: MagicMock) -> None:
    data = [{"key": "value"}]
    expected_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data", "dummy_file.json"))
    saver = JSONSaver("dummy_file.json")
    saver._save_data(data)
    mocked_open.assert_called_once_with(expected_path, "w")


def test_add_aeroplane(json_saver: "JSONSaver", aeroplane: "Aeroplane") -> None:
    json_saver.add_aeroplane(aeroplane)
    data = json_saver._load_data()
    assert aeroplane.to_dict() in data


def test_delete_aeroplane(json_saver: "JSONSaver", aeroplane: "Aeroplane") -> None:
    json_saver.add_aeroplane(aeroplane)
    json_saver.delete_aeroplane(aeroplane)
    data = json_saver._load_data()
    assert aeroplane.to_dict() not in data
