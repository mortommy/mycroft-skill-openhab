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
```

The items are searched by label, so the items for the above examples could be:

```
Color DiningroomLight "Diningroom Light" <light> (gKitchen) [ "Lighting" ] {channel="hue:0200:1:bloom1:color"}
Color KitchenLight "Kitchen Light" <light> (gKitchen) [ "Lighting" ] {channel="hue:0200:1:bloom1:color"}
Switch 	GoodNight "Good Night"	[ "Switchable" ]	
```

If items are modified in openhab, a refresh in Mycroft is needed by the command:

```
- Hey Mycroft, refresh the openhab items
```

## Versions Change log
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

Add the block below to your mycoft.ini file (`~/.mycroft/mycroft.ini`)

```
 "OpenHabSkill": {
        "host": "openhab server ip",
        "port": "openhab server port"
      }
```
Restart mycroft

## TODO

 * add current item status request
 * add support for Thermostat tagged items
