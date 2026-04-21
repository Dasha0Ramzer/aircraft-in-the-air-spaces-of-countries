from src.functions import filter_aeroplanes, get_aeroplanes_by_altitude, sort_aeroplanes, get_top_aeroplanes, \
    print_aeroplanes
from src.utils import AeroplanesAPI, Aeroplane, JSONSaver


def user_interaction():
    country = input("Введите название страны: ")
    top_n = int(input("Введите количество самолетов для вывода в топ N: "))
    filter_words = input("Введите названия стран для фильтрации по стране регистрации: ").split()
    altitude_range = input("Введите диапазон высот полета: ") # Пример: 100000 - 150000

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