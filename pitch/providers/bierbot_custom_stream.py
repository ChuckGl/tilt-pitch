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

from datetime import datetime
from ..models import TiltStatus
from ..abstractions import CloudProviderBase
from ..configuration import PitchConfig
from ..rate_limiter import DeviceRateLimiter
from interface import implements
import requests
import json
import logging

class BierBotCustomStreamCloudProvider(implements(CloudProviderBase)):

    VERSION = "0.2"  # Version control number

    def __init__(self, config: PitchConfig):
        self.api_key = config.bierbot_api_key
        self.url = "https://brewbricks.com/api/iot/v1"
        self.str_name = f"BierBot ({self.url}, Version {self.VERSION})"
        self.rate_limiter = DeviceRateLimiter(rate=1, period=(60 * 2))  # 2 minutes
        self.headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        self.temp_unit = BierBotCustomStreamCloudProvider._get_temp_unit(config)

    def __str__(self):
        return self.str_name

    def start(self):
        pass

    def update(self, tilt_status: TiltStatus):
        self.rate_limiter.approve(tilt_status.color)

        payload = self._get_payload(tilt_status)

        # Print payload with timestamp
        print(f"[{datetime.now()}] Payload set: {payload}")

        result = requests.post(self.url, headers=self.headers, data=json.dumps(payload))

        # Print status code and response text with timestamp
        print(f"[{datetime.now()}] Status Code: {result.status_code}")
        print(f"[{datetime.now()}] Response Text: {result.text}")

        result.raise_for_status()

        # Extract 'next_request_ms' from the response JSON
        try:
            response_json = result.json()
            next_request_ms = response_json.get('next_request_ms')
            if next_request_ms is not None:
                self.rate_limiter.period = next_request_ms / 1000  # Convert milliseconds to seconds
                print(f"[{datetime.now()}] Next Request Period (seconds): {self.rate_limiter.period}")
        except json.JSONDecodeError:
            print(f"[{datetime.now()}] Error decoding JSON response.")

    def enabled(self):
        return True if self.api_key else False

    def _get_payload(self, tilt_status: TiltStatus):
        return {
            'apikey': self.api_key,
            'type': "tilt",
            'brand': "tilt_pitch",
            'version': self.VERSION,
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

