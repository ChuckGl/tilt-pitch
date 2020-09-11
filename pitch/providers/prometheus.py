from ..models import TiltStatus
from ..abstractions import CloudProviderBase
from ..configuration import PitchConfig
from interface import implements
from prometheus_client import Counter, Gauge, start_http_server

counter_beacons_received = Counter('pitch_beacons_received', 'Number of beacons received', ['color'])
gauge_temperature_fahrenheit = Gauge('pitch_temperature_fahrenheit', 'Temperature in fahrenheit', ['color'])
gauge_temperature_celcius = Gauge('pitch_temperature_celcius', 'Temperature in celcius', ['color'])
gauge_gravity = Gauge('pitch_gravity', 'Gravity of the beer', ['color'])

class PrometheusCloudProvider(implements(CloudProviderBase)):

    def __init__(self, config: PitchConfig):
        self.is_enabled = config.prometheus_enabled
        self.port = config.prometheus_port

    def __str__(self):
        return "Prometheus"

    def start(self):
        start_http_server(self.port)
        return "(127.0.0.1:{}/metrics)".format(self.port)

    def update(self, tilt_status: TiltStatus):
        counter_beacons_received.labels(color=tilt_status.color).inc()
        gauge_temperature_fahrenheit.labels(color=tilt_status.color).set(tilt_status.temp_f)
        gauge_temperature_celcius.labels(color=tilt_status.color).set(tilt_status.temp_c)
        gauge_gravity.labels(color=tilt_status.color).set(tilt_status.gravity)

    def enabled(self):
        return self.is_enabled