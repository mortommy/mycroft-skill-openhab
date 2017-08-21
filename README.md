# Openhab skill for Mycroft

This skill adds [Openhab](http://www.openhab.org/) support to [Mycroft](https://mycroft.ai).
The skill takes advantage of Openhab REST API so it works both with the v1.0 and v2.0 of OH.  

In order to make the oh items public to Mycroft will need to be [tagged](http://docs.openhab.org/addons/io/homekit/readme.html).

Some sample commands are:

```
- Hey Mycroft, turn on Diningroom Light
- Hey Mycroft, switch off Kitchen Light
- Hey Mycroft, put on Good Night
- Hey Mycroft, set Diningroom to 50
- Hey Mycroft, dim Kitchen
- Hey Mycroft, brighten Kitchen
- Hey Mycroft, dim Kitchen by 20
- Hey Mycroft, what's Bedroom temperature?
- Hey Mycroft, what's Bedroom humidity?
- Hey Mycroft, adjust Main Thermostat to 21 degrees
- Hey Mycroft, regulate Main Thermostat to 20 degrees
- Hey Mycroft, decrease Main Thermostat by 2 degrees
- Hey Mycroft, increase Main Thermostat by 1 degrees
- Hey Mycroft, what is Main Thermostat regulated to?
- Hey Mycroft, what is Main Thermostat tuned to?
```

The items are searched by label, so the items for the above examples could be:

```
Color DiningroomLight "Diningroom Light" <light> (gKitchen) [ "Lighting" ] {channel="hue:0200:1:bloom1:color"}
Color KitchenLight "Kitchen Light" <light> (gKitchen) [ "Lighting" ] {channel="hue:0200:1:bloom1:color"}
Switch GoodNight "Good Night"	[ "Switchable" ]	

Number MqttID1Temperature "Bedroom Temperature" <temperature> [ "CurrentTemperature" ] {mqtt="<[mosquitto:mysensors/SI/1/1/1/0/0:state:default]"}
Number MqttID1Humidity "Bedroom Humidity" [ "CurrentHumidity" ] {mqtt="<[mosquitto:mysensors/SI/1/0/1/0/1:state:default]"}

Group gThermostat "Main Thermostat" [ "gMainThermostat" ]
Number MainThermostatCurrentTemp "Main Thermostat Current Temperature" (gMainThermostat) [ "CurrentTemperature" ]
Number MainThermostatTargetTemperature "Main Thermostat Target Temperature" (gMainThermostat) [ "TargetTemperature" ]
String MainThermostatHeatingCoolingMode "Main Thermostat Heating/Cooling Mode" (gMainThermostat) [ "homekit:HeatingCoolingMode" ]
```

If items are modified in openhab, a refresh in Mycroft is needed by the command:

```
- Hey Mycroft, refresh openhab items
```

## Versions Change log
* 1.0 added support to item tagged as Thermostat, CurrentTemperature, CurrentHumidity
* 0.9 added dimming command to item tagged as Lighting
* 0.8 supports only Lighting and Switchable tags, commands ON and OFF

## Installation

Clone the repository into your `~/.mycroft/skills` directory. Then install the
dependencies inside your mycroft virtual environment:

If on picroft just skip the workon part and the directory will be /opt/mycroft/skills

```
cd ~/.mycroft/skills
git clone https://github.com/mortommy/skill-openhab skill-openhab
workon mycroft
cd skill-openhab
pip install -r requirements.txt
```
## Configuration

Add the block below to your mycoft.conf file

```
 "OpenHabSkill": {
        "host": "openhab server ip",
        "port": "openhab server port"
      }
```
Restart mycroft