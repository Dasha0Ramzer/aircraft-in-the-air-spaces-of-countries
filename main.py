from typing import Any

from src.functions import filter_aeroplanes, get_aeroplanes_by_altitude, get_top_aeroplanes, sort_aeroplanes
from src.utils import Aeroplane, AeroplanesAPI, JSONSaver


def print_aeroplanes(aeroplanes: list[Any], country: str) -> None:
    """
    Функция, выводящая результат поиска самолетов по пользовательским критериям
    :param aeroplanes: список самолетов
    :param country: страна для поиска самолетов
    """

    print()
    print(f"Всего самолетов над страной {country}: {Aeroplane.aeroplane_count}")
    count = 1
    print()
    if len(aeroplanes) == 0:
        print("Самолетов по Вашим данным не найдено")
    else:
        print("Самолеты по Вашим данным:")
        for plane in aeroplanes:
            print(f"{count}. Страна регистрации ВС - {plane.country}, находится на высоте {plane.geo_altitude} м.")
            count += 1


def user_interaction() -> None:
    """
    Главная функция для взаимодействия с пользователем
    """

    country = input("Введите название страны: ")
    top_n = int(input("Введите количество самолетов для вывода в топ N: "))
    filter_words = input("Введите названия стран для фильтрации по стране регистрации: ").split()
    altitude_range = input("Введите диапазон высот полета (пример: 100000 - 150000): ")

    api = AeroplanesAPI()
    api.get_aeroplanes(country)
    aeroplanes_objects = Aeroplane.cast_to_object_list(api._aeroplanes)
    json_saver = JSONSaver()
    for aeroplane in aeroplanes_objects:
        json_saver.add_aeroplane(aeroplane)

    filtered_aeroplanes = filter_aeroplanes(aeroplanes_objects, filter_words)

    ranged_aeroplanes = get_aeroplanes_by_altitude(filtered_aeroplanes, altitude_range)

    sorted_aeroplanes = sort_aeroplanes(ranged_aeroplanes)

    top_aeroplanes = get_top_aeroplanes(sorted_aeroplanes, top_n)

    print_aeroplanes(top_aeroplanes, country)


user_interaction()
