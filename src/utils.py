import json
from abc import ABC, abstractmethod
from typing import Any, Optional, Union

from requests import get


class AbstractAeroplanesAPI(ABC):
    """
    Абстрактный класс для класса получения данных по API
    """

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_aeroplanes(self, country: str) -> None:
        pass


class AeroplanesAPI(AbstractAeroplanesAPI):
    """
    Класс для получения данных по API
    о координатах страны и самолетах, находящихся в пределах этих координат
    """

    def __init__(self) -> None:
        """
        Метод-конструктор
        """

        self._openstreetmap_url = "https://nominatim.openstreetmap.org/search"
        self._opensky_url = "https://opensky-network.org/api/states/all?"
        self._aeroplanes = None

    @staticmethod
    def _connect_to_api(url: str, params: dict[str, Any], headers: Optional[dict[str, str]] = None) -> Any:
        """
        Статический метод проверки на подключение к API
        :param url: ссылка на интернет-ресурс
        :param params: параметры для запроса
        :param headers: обязательный параметр
        :return: полученные данные в формате json
        """
        response = get(url=url, params=params, headers=headers)
        if response.status_code != 200:
            raise Exception("Ошибка при подключении к API")
        return response.json()

    def get_aeroplanes(self, country: str) -> None:
        """
        Метод получения данных по API и объединение между собой
        :param country: страна для получения данных о самолетах
        :return: данные о самолетах
        """

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


class Aeroplane:
    """
    Класс для работы с информацией о самолетах
    """

    __slots__ = ("ICAO24", "callsign", "country", "on_ground", "velocity", "geo_altitude")

    aeroplane_count = 0

    def __init__(self, list_aeroplanes: list[Union[str, float, bool]]) -> None:
        """
        Метод-конструктор
        :param list_aeroplanes: список данных о самолете
        """

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
    def _validate_velocity(velocity: Any, on_ground: Union[str, float, bool]) -> None:
        """
        Метод-валидатор проверки на отрицательную скорость полета
        :param velocity: скорость самолета
        :param on_ground: находится ли самолет в воздухе
        :return: если скорость отрицательная, то появится ошибка ValueError
        """

        if velocity is not None and velocity < 0 and not on_ground:
            raise ValueError("Скорость не может быть отрицательной")

    @staticmethod
    def _validate_altitude(geo_altitude: Any, on_ground: Union[str, float, bool]) -> None:
        """
        Метод-валидатор проверки на отрицательную высоту полета
        :param geo_altitude: географическая высота самолета
        :param on_ground: находится ли самолет в воздухе
        :return: если высота отрицательная, то появится ошибка ValueError
        """

        if geo_altitude is not None and geo_altitude < 0 and not on_ground:
            raise ValueError("Высота не может быть отрицательной")

    @staticmethod
    def cast_to_object_list(aeroplanes_list: Any) -> list["Aeroplane"]:
        """
        Метод преобразования набора данных в список объектов
        :param aeroplanes_list: словарь с данными о самолетах
        :return: список объектов класса
        """

        objects_list = []
        for aeroplane_data in aeroplanes_list["states"]:
            try:
                aeroplane = Aeroplane(aeroplane_data)
                objects_list.append(aeroplane)
            except ValueError as e:
                print(f"Ошибка при создании объекта Aeroplane: {e}")
        return objects_list

    def __lt__(self, other: Any) -> Any:
        """
        Магический метод проверки на меньшее
        :param other: иной объект
        :return: булево значение
        """

        return self.geo_altitude < other.geo_altitude

    def __gt__(self, other: Any) -> Any:
        """
        Магический метод проверки на большее
        :param other: иной объект
        :return: булево значение
        """

        return self.geo_altitude > other.geo_altitude

    def __eq__(self, other: Any) -> Any:
        """
        Магический метод проверки на равенство объектов
        :param other: иной объект
        :return: булево значение
        """

        return self.geo_altitude == other.geo_altitude

    def to_dict(self) -> dict[str, Any]:
        """
        Метод преобразования объекта класса в соответствующем виде для сохранения в файл
        :return: словарь с данными
        """

        return {
            "ICAO24": self.ICAO24,
            "callsign": self.callsign,
            "country": self.country,
            "on_ground": self.on_ground,
            "velocity": self.velocity,
            "geo_altitude": self.geo_altitude,
        }


class AbstractJSONSaver(ABC):
    """
    Абстрактный класс для класса сохранения данных в файл
    """

    @abstractmethod
    def __init__(self, filename: str) -> None:
        pass

    @abstractmethod
    def add_aeroplane(self, aeroplane: "Aeroplane") -> None:
        pass

    @abstractmethod
    def delete_aeroplane(self, aeroplane: "Aeroplane") -> None:
        pass


class JSONSaver(AbstractJSONSaver):
    """
    Класс для сохранения данных в файл в формате json
    """

    def __init__(self, filename: str = "./data/aeroplanes.json") -> None:
        """
        Метод-конструктор
        :param filename: путь к файлу, по умолчанию "./data/aeroplanes.json"
        """

        self._filename = filename

    def _load_data(self) -> Any:
        """
        Метод загружает данные из JSON-файла
        """

        try:
            with open(self._filename, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def _save_data(self, data: Any) -> None:
        """
        Метод сохраняет данные в JSON-файл
        """

        with open(self._filename, "w") as file:
            json.dump(data, file, indent=4)

    def add_aeroplane(self, aeroplane: "Aeroplane") -> None:
        """
        Добавляет информацию о самолёте в файл
        """

        data = self._load_data()
        aeroplane_dict = aeroplane.to_dict()
        if aeroplane_dict not in data:  # Проверка на дублирование
            data.append(aeroplane_dict)
            self._save_data(data)

    def delete_aeroplane(self, aeroplane: "Aeroplane") -> None:
        """
        Удаляет информацию о самолёте из файла
        """

        data = self._load_data()
        try:
            data.remove(aeroplane)
        except ValueError:
            print("Самолёт не найден в списке")
        self._save_data(data)
