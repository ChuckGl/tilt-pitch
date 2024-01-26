from ..configuration import PitchConfig
from .json_serialize import JsonSerialize
import datetime

class TiltStatus(JsonSerialize):

    def __init__(self, color, temp_fahrenheit, current_gravity, config: PitchConfig):
        self.timestamp = datetime.datetime.now()
        self.color = color
        self.name = config.get_brew_name(color)
        self.temp_fahrenheit = temp_fahrenheit + config.get_temp_offset(color)
        self.temp_celsius = TiltStatus.get_celsius(self.temp_fahrenheit)
        self.original_gravity = config.get_original_gravity(color)
        self.gravity = current_gravity + config.get_gravity_offset(color)
        self.plato = self.get_plato(self.gravity)
        self.alcohol_by_volume = TiltStatus.get_alcohol_by_volume(self.original_gravity, self.gravity)
        self.apparent_attenuation = TiltStatus.get_apparent_attenuation(self.original_gravity, self.gravity)
        self.temp_valid = (config.temp_range_min < self.temp_fahrenheit and self.temp_fahrenheit < config.temp_range_max)
        self.gravity_valid = (config.gravity_range_min < self.gravity and self.gravity < config.gravity_range_max)

    @staticmethod
    def get_celsius(temp_fahrenheit):
        """Convert Fahrenheit to Celsius."""
        celsius = (temp_fahrenheit - 32) * 5.0 / 9.0
        return round(celsius, 2)

    @staticmethod
    def get_alcohol_by_volume(original_gravity, current_gravity):
        """Calculate Alcohol by Volume (ABV)."""
        if original_gravity is None:
            return 0
        alcohol_by_volume = (original_gravity - current_gravity) * 131.25
        return round(alcohol_by_volume, 2)

    @staticmethod
    def get_apparent_attenuation(original_gravity, current_gravity):
        """Calculate Apparent Attenuation."""
        if original_gravity is None:
            return 0
        aa = ((original_gravity - current_gravity) / original_gravity) * 2 * 1000
        return round(aa, 2)

    @staticmethod
    def get_gravity_points(gravity):
        """Converts gravity reading like 1.035 to just 35"""

    def get_plato(self, current_gravity):
        """Calculate Plato."""
        plato = (0.005 - 616.868 + 1111.14 * current_gravity - 630.272 * current_gravity * current_gravity + 135.997 * current_gravity * current_gravity * current_gravity)
        return round(plato, 2)

