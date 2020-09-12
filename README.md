# Pitch (Tilt Hydrometer tool)

Pitch is an unofficial replacement for Tilt Hydrometer mobile apps and TiltPi software.  Tilt hardware is required.  It is designed to be easy to use and integrated with other tools like Promethues for metrics, or any generic third party source using webhooks.

# Why

The Tilt hardware is impressive, but the mobile apps and TiltPi are confusing and buggy.  This project aims to provide a better more reliable solution, but is focused on more tech-savvy brewers than the official Tilt projects.  

# Features

The following features are implemented, planned, or will be investigated in the future:

* [x] Track multiple Tilts at once
* [x] Prometheus Metrics
* [x] Tilt status log file (JSON)
* [X] InfluxDB Metrics
* [X] Multiple logging and metric sources simultaneously
* [X] Webhooks for supporting generic integrations (similar to Tilt's Cloud Logging feature)
* [ ] Brewing Cloud Services (Brewstats, Brewer's Friend, etc.)
* [ ] Google Sheets (using any Google Drive)


# Name

It's an unofficial tradition to name tech projects using nautical terms.  Pitch is a term used to describe the tilting/movement of a ship at sea.  Given pitching is also a brewing term, it seemed like a good fit.

#Configuration

Custom configurations can be used by creating a file `pitch.json` in the working directory you are running Pitch from.

| Option                       | Purpose                      | Default               |
| ---------------------------- | ---------------------------- | --------------------- |
| `simulate_beacons` (bool) | Creates fake Tilt beacon events instead of scanning, useful for testing | False |
| `webhook_urls` (array) | Adds webhook URLs for Tilt status updates | None/empty |
| `log_file_path` (str) | Path to file for JSON event logging | `pitch_log.json` |
| `log_file_max_mb` (int) | Max JSON log file size in megabytes | `10` |
| `prometheus_enabled` (bool) | Enable/Disable Prometheus metrics | `true` |
| `prometheus_port` (int) | Port number for Prometheus Metrics | `8000` |
| `influxdb_hostname` (str) | Hostname for InfluxDB database | None/empty |
| `influxdb_port` (int) | Port for InfluxDB database | None/empty |
| `influxdb_database` (str) | Name of InfluxDB database | None/empty |
| `influxdb_username` (str) | Username for InfluxDB | None/empty |
| `influxdb_batch_size` (int) | Number of events to batch | `10` |
| `influxdb_timeout_seconds` (int) | Timeout of InfluxDB reads/writes | `5` |


# Integrations

## Prometheus Metrics

Prometheus metrics are hosted on port 8000.  For each Tilt the followed Prometheus metrics are created:

```
# HELP pitch_beacons_received_total Number of beacons received
# TYPE pitch_beacons_received_total counter
pitch_beacons_received_total{color="purple"} 3321.0

# HELP pitch_temperature_fahrenheit Temperature in fahrenheit
# TYPE pitch_temperature_fahrenheit gauge
pitch_temperature_fahrenheit{color="purple"} 69.0

# HELP pitch_temperature_celcius Temperature in celcius
# TYPE pitch_temperature_celcius gauge
pitch_temperature_celcius{color="purple"} 21.0

# HELP pitch_gravity Gravity of the beer
# TYPE pitch_gravity gauge
pitch_gravity{color="purple"} 1.035
```

## Webhook

Unlimited webhooks can be configured using the config option `webhook_urls`.  Each Tilt status broadcast will result in a webhook call to all URLs.

Webhooks are sent as HTTP POST with the following json payload:

```
{
    "color": "purple",
    "temp_f": 69,
    "temp_c": 21,
    "gravity": 1.035
}
```

## JSON Log File

Tilt status broadcast events can be logged to a json file using the config option `log_file_path`.  Each event is a newline.  Example file:

```
{"timestamp": "2020-09-11T02:15:30.525232", "color": "purple", "temp_f": 70, "temp_c": 21, "gravity": 0.997}
{"timestamp": "2020-09-11T02:15:32.539619", "color": "purple", "temp_f": 70, "temp_c": 21, "gravity": 0.997}
{"timestamp": "2020-09-11T02:15:33.545388", "color": "purple", "temp_f": 70, "temp_c": 21, "gravity": 0.997}
{"timestamp": "2020-09-11T02:15:34.548556", "color": "purple", "temp_f": 70, "temp_c": 21, "gravity": 0.997}
{"timestamp": "2020-09-11T02:15:35.557411", "color": "purple", "temp_f": 70, "temp_c": 21, "gravity": 0.997}
{"timestamp": "2020-09-11T02:15:36.562158", "color": "purple", "temp_f": 70, "temp_c": 21, "gravity": 0.996}
```

## InfluxDB Metrics

Metrics can be sent to an InfluxDB database.  See [Configuration section](#Configuration) for setting this up.  Pitch does not create the database
so it must be created before using Pitch.  

Each beacon event from a Tilt will create a measurement like this:

```json
{
    "measurement": "tilt",
    "tags": {
        "color": "purple"
    },
    "fields": {
        "temp_f": 70,
        "temp_c": 21,
        "gravity": 1.035
    }
}
```  

and can be queried with something like:

```sql
SELECT mean("gravity") AS "mean_gravity" FROM "pitch"."autogen"."tilt" WHERE time > :dashboardTime: AND time < :upperDashboardTime: AND "color"='purple' GROUP BY time(:interval:) FILL(previous)
```

# Examples

See the examples directory for:

* InfluxDB Grafana Dashboard
* Running Pitch as a systemd service