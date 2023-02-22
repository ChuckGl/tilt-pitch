# Payload docs: https://forum.bierbot.com/biewtopic.php?t=51
# {
#  "apikey": "J1okPxXwdFoSvt9Bnz5V",
#  "type": "tilt",
#  "brand": "tilt_bridge",
#  "version": "0.0.1",
#  "chipid": "ORANGE",
#  "s_number_wort_0": 7.9,
#  "s_number_temp_0": 14.3,
#  "s_number_voltage_0": 4.09,
#  "s_number_wifi_0": -90,
#  "s_number_tilt_0": 40.23,
# }
# URL: https://brewbricks.com/api/iot/v1

from ..models import TiltStatus
from ..abstractions import CloudProviderBase
from ..configuration import PitchConfig
from ..rate_limiter import DeviceRateLimiter
from interface import implements
import requests
import json


class BierBotCustomStreamCloudProvider(implements(CloudProviderBase)):

    def __init__(self, config: PitchConfig):
        self.api_key = config.bierbot_api_key
        self.url = "https://brewbricks.com/api/iot/v1"
        self.str_name = "BierBot ({})".format(self.url)
        self.rate_limiter = DeviceRateLimiter(rate=1, period=(60 * 15))  # 15 minutes
        self.headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        self.temp_unit = BierBotCustomStreamCloudProvider._get_temp_unit(config)

    def __str__(self):
        return self.str_name

    def start(self):
        pass

    def update(self, tilt_status: TiltStatus):
        self.rate_limiter.approve(tilt_status.color)
        payload = self._get_payload(tilt_status)
        result = requests.post(self.url, headers=self.headers, data=json.dumps(payload))
        result.raise_for_status()

    def enabled(self):
        return True if self.api_key else False

    def _get_payload(self, tilt_status: TiltStatus):
        return {
            'apikey': self.api_key,
            'type': "tilt",
            'brand': "tilt_bridge",
            'version': "0.0.1",
            'chipid': tilt_status.color,
            's_number_wort_0': tilt_status.gravity,
            's_number_temp_0': self._get_temp_value(tilt_status),
            's_number_voltage_0': "4.09",
            's_number_wifi_0': "-90",
            's_number_tilt_0': "40.23"
        }

    def _get_temp_value(self, tilt_status: TiltStatus):
        if self.temp_unit == "F":
            return tilt_status.temp_fahrenheit
        else:
            return tilt_status.temp_celsius

    @staticmethod
    def _get_temp_unit(config: PitchConfig):
        temp_unit = config.bierbot_temp_unit.upper()
        if temp_unit in ["C", "F"]:
            return temp_unit

        raise ValueError("BierBot's temp unit must be F or C")

