"""Platform to enable smart relative dimming of light groups, extending the core light group."""

from __future__ import annotations

from typing import Any

from homeassistant.components import light
from homeassistant.components.group.light import (
    CONF_ALL,
    FORWARDED_ATTRIBUTES,
    PLATFORM_SCHEMA as LIGHT_GROUP_PLATFORM_SCHEMA,
    LightGroup,
)
from homeassistant.components.light import ATTR_BRIGHTNESS
from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_ENTITIES,
    CONF_NAME,
    CONF_UNIQUE_ID,
    SERVICE_TURN_ON,
    STATE_ON,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .util import coerce_in

BRIGHTNESS_MAX = 255
BRIGHTNESS_MIN = 1
BRIGHTNESS_OFF = 0

DOMAIN = "relative_brightness_light_group"

# Validation of the user's configuration
PLATFORM_SCHEMA = LIGHT_GROUP_PLATFORM_SCHEMA


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Initialize relative_brightness_group platform."""
    async_add_entities(
        [
            RelativeBrightnessLightGroup(
                config.get(CONF_UNIQUE_ID),
                config[CONF_NAME],
                config[CONF_ENTITIES],
                config.get(CONF_ALL),
            )
        ]
    )


class RelativeBrightnessLightGroup(LightGroup):
    """Representation of a light group maintaining relative brightness between lights."""

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Forward the turn_on command to all lights in the light group."""

        # Set default data
        data = {
            key: value for key, value in kwargs.items() if key in FORWARDED_ATTRIBUTES
        }
        data[ATTR_ENTITY_ID] = self._entity_ids

        # Check if any lights are on
        lights_on = [
            state
            for entity_id in self._entity_ids
            if (state := self.hass.states.get(entity_id)) is not None
            and state.state == STATE_ON
        ]

        # For each light on, calculate relative brightness to group brightness
        if ATTR_BRIGHTNESS in data and lights_on:
            group_brightness_current = self._attr_brightness
            group_brightness_new = data.get(ATTR_BRIGHTNESS)
            group_brightness_change = group_brightness_new - group_brightness_current

            light_entity_ids = [state.entity_id for state in lights_on]

            brightness_change_factor = (
                group_brightness_change / (BRIGHTNESS_MAX - group_brightness_current)
                if group_brightness_change > 0
                else group_brightness_change / group_brightness_current
            )

            def brightness_offset(brightness):
                """Adjust brightness proportionally to light group brightness change."""
                if group_brightness_change == 0:
                    return 0

                return (
                    brightness_change_factor * (BRIGHTNESS_MAX - light_brightness)
                    if group_brightness_change > 0
                    else brightness_change_factor * brightness
                )

            # Calculate new brightness level for each light
            light_brightness_levels = (
                [
                    coerce_in(
                        round(light_brightness + brightness_offset(light_brightness)),
                        1,
                        255,
                    )
                    for state in lights_on
                    if (light_brightness := state.attributes.get(ATTR_BRIGHTNESS))
                    is not None
                ]
                if group_brightness_change
                else []
            )

            # Group by new brightness level to reduce number of calls
            brightness_groups = {}
            for entity_id, brightness in zip(light_entity_ids, light_brightness_levels):
                if brightness in brightness_groups:
                    brightness_groups[brightness].append(entity_id)
                else:
                    brightness_groups[brightness] = [entity_id]

            # Create service call tasks
            for brightness, entity_ids in brightness_groups.items():
                data[ATTR_BRIGHTNESS] = brightness
                data[ATTR_ENTITY_ID] = entity_ids
                await self.hass.services.async_call(
                    light.DOMAIN,
                    SERVICE_TURN_ON,
                    data,
                    blocking=True,
                    context=self._context,
                )
        else:
            # No lights on or other adjustments than brightness
            await self.hass.services.async_call(
                light.DOMAIN,
                SERVICE_TURN_ON,
                data,
                blocking=True,
                context=self._context,
            )
