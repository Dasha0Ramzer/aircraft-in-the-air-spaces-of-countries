from typing import Any

from src.utils import Aeroplane


def filter_aeroplanes(aeroplanes: list["Aeroplane"], countries: list[str]) -> list["Aeroplane"]:
    """
    Функция, фильтрующая самолеты по названиям стран их регистрации
    :param aeroplanes: список самолетов
    :param countries: страны регистрации самолетов для фильтрации
    :return: отфильтрованный список самолетов
    """

    filtered_aeroplanes = [plane for plane in aeroplanes if plane.country in countries]
    return filtered_aeroplanes


def get_aeroplanes_by_altitude(aeroplanes: list[Any], altitude_range: str) -> list[Any]:
    """
    Функция, фильтрующая самолеты по диапазону высот полета
    :param aeroplanes: список самолетов
    :param altitude_range: диапазон высот полета
    :return: отфильтрованный список самолетов
    """

    start_str, end_str = altitude_range.replace(" ", "").split("-")

    start = int(start_str)
    end = int(end_str)
    ranged_aeroplanes = [
        plane for plane in aeroplanes if plane.geo_altitude is not None and start <= plane.geo_altitude <= end
    ]

    return ranged_aeroplanes


def sort_aeroplanes(aeroplanes: list[Any]) -> list[Any]:
    """
    Функция, сортирующая самолеты от большего к меньшему по высоте полета
    :param aeroplanes: список самолетов
    :return: отсортированный список
    """

    aeroplanes.sort(key=lambda plane: plane.geo_altitude, reverse=True)
    return aeroplanes


def get_top_aeroplanes(aeroplanes: list[Any], top: int) -> list[Any]:
    """
    Функция, возвращающая самолеты, входящие в ТОП-N
    :param aeroplanes: список самолетов
    :param top: значение ТОП-N
    :return: список самолетов
    """

    return aeroplanes[:top]
