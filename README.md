# Relative brightness light group
Light group for Home Assistant that maintains relative brightness between lights as group brightness is changed.

![](demo.gif)

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


