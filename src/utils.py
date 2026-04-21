import json
from abc import ABC, abstractmethod
from requests import get


class AbstractAeroplanesAPI(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def get_aeroplanes(self, country: str) -> None:
        pass


class AeroplanesAPI(AbstractAeroplanesAPI):

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


# api = AeroplanesAPI()
# api.get_aeroplanes("Canada")
# pretty_json = json.dumps(api.aeroplanes, indent=4)
# print(pretty_json)


class Aeroplane:
    __slots__ = ('ICAO24', 'callsign', 'country', 'on_ground', 'velocity', 'geo_altitude')

    aeroplane_count = 0

    def __init__(self, list_aeroplanes):
        self._validate_velocity(list_aeroplanes[9], list_aeroplanes[8])
        self._validate_altitude(list_aeroplanes[13], list_aeroplanes[8])

        self.ICAO24 = list_aeroplanes[0]  # уникальный идентификатор
        self.callsign = list_aeroplanes[1]  # позывной рейса
        self.country = list_aeroplanes[2]  # Страна регистрации ВС
        self.on_ground = list_aeroplanes[8]  # находится ли самолёт на земле
        self.velocity = list_aeroplanes[9]  # горизонтальная скорость (м/с)
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

    def to_dict(self):
        return {
            "ICAO24": self.ICAO24,
            "callsign": self.callsign,
            "country": self.country,
            "on_ground": self.on_ground,
            "velocity": self.velocity,
            "geo_altitude": self.geo_altitude
        }


# api = AeroplanesAPI()
# aeroplanes = api.get_aeroplanes("Russia")
# aeroplanes = Aeroplane.cast_to_object_list(aeroplanes)
# print(Aeroplane.aeroplane_count)


class AbstractJSONSaver(ABC):

    @abstractmethod
    def __init__(self, filename):
        pass

    @abstractmethod
    def add_aeroplane(self, aeroplane) -> None:
        pass

    @abstractmethod
    def delete_aeroplane(self, aeroplane):
        pass


class JSONSaver(AbstractJSONSaver):

    def __init__(self, filename='./data/aeroplanes.json'):
        self._filename = filename

    def _load_data(self):
        """Загружает данные из JSON-файла."""
        try:
            with open(self._filename, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return []  # Если файл не найден, возвращаем пустой список

    def _save_data(self, data):
        """Сохраняет данные в JSON-файл."""
        with open(self._filename, 'w') as file:
            json.dump(data, file, indent=4)

    def add_aeroplane(self, aeroplane):
        """Добавляет информацию о самолёте в файл."""
        data = self._load_data()
        aeroplane_dict = aeroplane.to_dict()
        if aeroplane_dict not in data:  # Проверка на дублирование
            data.append(aeroplane_dict)
            self._save_data(data)

    def delete_aeroplane(self, aeroplane):
        """Удаляет информацию о самолёте из файла."""
        data = self._load_data()
        try:
            data.remove(aeroplane)
        except ValueError:
            print("Самолёт не найден в списке")
        self._save_data(data)


# api = AeroplanesAPI()
# aeroplanes_data = api.get_aeroplanes('Canada')
#
# # Преобразование данных в объекты
# aeroplanes_objects = Aeroplane.cast_to_object_list(aeroplanes_data)
#
# # Сохранение в JSON
# json_saver = JSONSaver()
# for aeroplane in aeroplanes_objects:
#     json_saver.add_aeroplane(aeroplane)



