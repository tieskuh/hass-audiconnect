"""Support for Audi Connect switches."""
from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberDeviceClass as dc
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from audiconnectpy import AudiException
from .const import DOMAIN
from .entity import AudiEntity
from .helpers import AudiNumberDescription

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES: tuple[AudiNumberDescription, ...] = (

    
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the switch."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for vin, vehicle in coordinator.data.items():
        for name, data in vehicle.states.items():
            for description in SENSOR_TYPES:
                if description.key == name:
                    entities.append(AudiNumber(coordinator, vin, description))

    async_add_entities(entities)


class AudiNumber(AudiEntity, NumberEntity):
    """Representation of a Audi switch."""

    @property
    def mode(self) -> str:
        """Mode."""
        return "box"

    @property
    def native_value(self) -> float:
        """Native value."""
        value = self.coordinator.data[self.vin].states.get(self.uid)
        if value and self.entity_description.value_fn:
            return self.entity_description.value_fn(value)
        return value

    async def async_set_native_value(self, value: float) -> None:
        """Set the text value."""
        try:
            await getattr(
                self.coordinator.api.services, self.entity_description.turn_mode
            )(self.vin, value)
            await self.coordinator.async_request_refresh()
        except AudiException as error:
            _LOGGER.error("Error to set value: %s", error)
