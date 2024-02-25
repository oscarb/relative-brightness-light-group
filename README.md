# Relative brightness light group
Light group for Home Assistant that maintains relative brightness between lights as group brightness is changed.

![](demo.gif)

> **Note**: Since this light group is built on top of the core light group, it also has that "bouncy" brightness slider [behavior](https://community.home-assistant.io/t/light-groups-bouncy-brightness-slider-behaviour/501539) depending on your setup. 


## Usage

Using this is as easy as using a normal [light group](https://www.home-assistant.io/integrations/group/). 

In your `configuration.yaml`, add: 

```yaml
light:
  - platform: relative_brightness_light_group
    name: The Office
    entities:
      - light.office_desk
      - light.office_spotlights
```


