# How to install Home Assistant integration ?

The goal is to have a complete control of the device on solutions like Home Asssitant.I assume that you have a working installation of an MQTT server like Mosquitto
or have it installed as an addon to Home Assistant.

eBusd will take care of publishing most of the sensors with their respective read/write status.

Some bugs remain (01/2023):

- impossible to specify a range for a value other than the range deduced from its type (-32767;32767 for the SIN type)<br>
  => not fixable unless you do without the [MQTT Discovery] function (https://www.home-assistant.io/integrations/mqtt/#mqtt-discovery).
- impossible to automatically represent multiple choice inputs (ex: thermoregulation type).<br>
  => corrected by specific yaml statements
- hazardous naming of entities displayed in Home Assistant.<br>
  => essentially corrected by the `mqtt-hassio.cfg` file of this repository.

## Integration via MQTT Discovery

Command to enable MQTT integration of ebusd:

    ebusd -d 192.168.1.65:3333 --latency=200000 --configpath=/path_to_your_config_files/ --enablehex --receivetimeout=100 \
    --mqtthost 127.0.0.1 --mqttport 1883 --mqttuser=<mqtt_user> --mqttpass=<password> --mqttjson
    --pollinterval=10
    --mqttint=/path_to_your_mqtt_config_file/mqtt-hassio.cfg

The default `.cfg` should be at `/etc/ebusd/mqtt-hassio.cfg`.

Put the file `mqtt-hassio.cfg` of this repository at the place you have chosen.
This file supports some specific rules created for this particular brand of boiler
(the filtering of the entities to be published on the MQTT server is based on regexes).

## Specific widgets

For multiple choice inputs such as `z1_thermoreg_type` and `dhw_comfort_mode_status_w`,
you will need to add to the `~/.homeassistant/configuration.yaml` file (or in separate files to include) the code proposed in the file `./home_assistant_integration/widgets_and_automations.yaml`.

Result:
![](./home_assistant_integration/dhw_comfort_widget_screenshot_small.webp)
