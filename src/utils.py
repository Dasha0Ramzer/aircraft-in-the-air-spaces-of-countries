import json
from abc import ABC, abstractmethod
from requests import get


class AbstractWorkingWithTheAPI(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def get_aeroplanes(self, country: str) -> None:
        pass


class WorkingWithTheAPI(AbstractWorkingWithTheAPI):

    def __init__(self) -> None:
        self._openstreetmap_url = "https://nominatim.openstreetmap.org/search"
        self._opensky_url = "https://opensky-network.org/api/states/all?"
        self._aeroplanes = None

    @staticmethod
    def _connect_to_api(url, params, headers=None):
        response = get(url=url, params=params, headers=headers)
        if response.status_code != 200:
            raise Exception("Ошибка при подключении к API")
        return response.json()

    def get_aeroplanes(self, country: str) -> None:

        # Headers с user-agent - обязательный параметр при запросе к nominatim.openstreetmap.
        # Вы можете использовать любое название вместо test-app/1.0, например просто test-app.
        headers_nominatim = {
            "User-Agent": "test-app/1.0",
        }

        # Указываем параметры: в каком формате возвращать данные и максимальную длину списка стран в ответе.
        params_nominatim = {
            "country": country,
            "format": "json",
            "limit": 1,
        }

        data = self._connect_to_api(self._openstreetmap_url, params_nominatim, headers_nominatim)
        geo_coordinates = data[0].get("boundingbox")

        # Параметры для фильтрации самолетов по их географическим координатам.
        params = {
            "lamin": geo_coordinates[0],
            "lamax": geo_coordinates[1],
            "lomin": geo_coordinates[2],
            "lomax": geo_coordinates[3],
        }

        response_data = self._connect_to_api(self._opensky_url, params)
        self._aeroplanes = response_data
        return self._aeroplanes


# api = WorkingWithTheAPI()
# api.get_aeroplanes("Canada")
# pretty_json = json.dumps(api.aeroplanes, indent=4)
# print(pretty_json)


class Aeroplane:
    __slots__ = ('ICAO24', 'callsign', 'country', 'longitude', 'latitude', 'on_ground', 'velocity', 'true_track',
                 'geo_altitude')

    aeroplane_count = 0

    def __init__(self, list_aeroplanes):
        self._validate_velocity(list_aeroplanes[9], list_aeroplanes[8])
        self._validate_altitude(list_aeroplanes[13], list_aeroplanes[8])

        self.ICAO24 = list_aeroplanes[0]  # уникальный идентификатор
        self.callsign = list_aeroplanes[1]  # позывной рейса
        self.country = list_aeroplanes[2]  # Страна регистрации ВС
        self.longitude = list_aeroplanes[5]  # долгота (°)
        self.latitude = list_aeroplanes[6]  # широта (°)
        self.on_ground = list_aeroplanes[8]  # находится ли самолёт на земле
        self.velocity = list_aeroplanes[9]  # горизонтальная скорость (м/с)
        self.true_track = list_aeroplanes[10]  # курс (градусы)
        self.geo_altitude = list_aeroplanes[13]  # геометрическая высота (м)

        Aeroplane.aeroplane_count += 1

    @staticmethod
    def _validate_velocity(velocity, on_ground):
        if velocity is not None and velocity < 0 and on_ground != False:
            raise ValueError("Скорость не может быть отрицательной")

    @staticmethod
    def _validate_altitude(geo_altitude, on_ground):
        if geo_altitude is not None and geo_altitude < 0 and on_ground != False:
            raise ValueError("Высота не может быть отрицательной")

    @staticmethod
    def cast_to_object_list(aeroplanes_list):
        # Создаем список объектов Aeroplane
        objects_list = []
        for aeroplane_data in aeroplanes_list['states']:
            try:
                # Создаем объект Aeroplane для каждого вложенного списка
                aeroplane = Aeroplane(aeroplane_data)
                objects_list.append(aeroplane)
            except ValueError as e:
                print(f"Ошибка при создании объекта Aeroplane: {e}")
        return objects_list

    def __lt__(self, other):
        return self.geo_altitude < other.geo_altitude

    def __gt__(self, other):
        return self.geo_altitude > other.geo_altitude

    def __eq__(self, other):
        return self.geo_altitude == other.geo_altitude


api = WorkingWithTheAPI()
aeroplanes = api.get_aeroplanes("Russia")
aeroplanes = Aeroplane.cast_to_object_list(aeroplanes)
print(Aeroplane.aeroplane_count)


# class APIAdapter:
#
#     def __init__(self) -> None:
#         self.openstreetmap_url = 'https://nominatim.openstreetmap.org/search'
#         self.opensky_url = 'https://opensky-network.org/api/states/all?'
#         self.aeroplanes = None
#
#     def get_aeroplanes(self, country: str) -> None:
#         #Headers с user-agent - обязательный параметр при запросе к nominatim.openstreetmap.
#         #Вы можете использовать любое название вместо test-app/1.0, например просто test-app.
#         headers_nominatim = {
#             'User-Agent': 'test-app/1.0',
#         }
#
#         #Указываем параметры: в каком формате возвращать данные и максимальную длину списка стран в ответе.
#         params_nominatim = {
#             'country': country,
#             'format': 'json',
#             'limit': 1,
#         }
#
#         response = get(url=self.openstreetmap_url, params=params_nominatim, headers=headers_nominatim)
#
#         data = response.json()
#
#         #Пример ответа от nominatim.openstreetmap можно посмотреть в задании курсовой.
#         geo_coordinates = data[0].get('boundingbox')
#
#         #Параметры для фильтрации самолетов по их географическим координатам.
#         params = {
#             'lamin': geo_coordinates[0],
#             'lamax': geo_coordinates[1],
#             'lomin': geo_coordinates[2],
#             'lomax': geo_coordinates[3],
#         }
#
#         response = get(url=self.opensky_url, params=params)
#
#         #Пример ответа от opensky-network можно посмотреть в задании курсовой.
#         self.aeroplanes = response.json()
#
# api = APIAdapter()
# api.get_aeroplanes('Canada')
# print(api.aeroplanes)
