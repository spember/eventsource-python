from datetime import datetime

from restaurant.events.base import BaseEvent
from restaurant.models import Event
from restaurant.services.translation import DjangoModelTranslatableBaseEvent


class MenuItemCreated(DjangoModelTranslatableBaseEvent):

    def __init__(self, name: str, category: str, user_id: int, revision: int, timestamp=datetime.utcnow()):
        super().__init__(user_id, revision, timestamp)
        self.name = name
        self.category = category

    @staticmethod
    def get_event_type():
        return 'menuitem.created'

    @staticmethod
    def create_from_event(event: Event):
        return MenuItemCreated(
            event.data['name'],
            event.data['category'],
            event.user_id_id,
            event.revision,
            event.time
        )


class PriceChanged(DjangoModelTranslatableBaseEvent):

    def __init__(self, delta: int, user_id: int, revision: int, timestamp=datetime.utcnow()):
        super().__init__(user_id, revision, timestamp)
        self.delta = delta

    @staticmethod
    def get_event_type():
        return 'menuitem.price.changed'

    @staticmethod
    def create_from_event(event: Event):
        return PriceChanged(
            event.data['delta'],
            event.user_id_id,
            event.revision,
            event.time
        )
