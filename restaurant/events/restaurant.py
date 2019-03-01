import uuid
from datetime import datetime
from uuid import UUID

from restaurant.events.base import BaseEvent, DjangoModelTranslatableBaseEvent
from restaurant.models import Event


class RestaurantOpened(DjangoModelTranslatableBaseEvent):

    def __init__(self, name:str, year:int, location:str, user_id: int, revision: int, timestamp=datetime.utcnow()):
        super(RestaurantOpened, self).__init__(user_id, revision, timestamp)
        self.name = name
        self.year = year
        self.location = location

    @staticmethod
    def get_event_type():
        return 'restaurant.opened'

    @staticmethod
    def create_from_event(event: Event):
        return RestaurantOpened(
            event.data['name'],
            event.data['year'],
            event.data['location'],
            event.user_id_id,
            event.revision,
            event.time
        )


class EmployeeHired(DjangoModelTranslatableBaseEvent):

    def __init__(self, employee_name: str, user_id, revision: int, timestamp=datetime.utcnow()):
        super().__init__(user_id, revision, timestamp)
        self.employee_name = employee_name
        # in a more robust system, we should model employee's with more information
        # todo: add employee events / entities in order to demonstrate relations / projection tables

    @staticmethod
    def get_event_type():
        return 'restaurant.employee.hired'

    @staticmethod
    def create_from_event(event: Event):
        return EmployeeHired(
            event.data['employee_name'],
            event.user_id_id,
            event.revision,
            event.time
        )


class EmployeeFired(DjangoModelTranslatableBaseEvent):

    def __init__(self, employee_name: str, user_id, revision: int, timestamp=datetime.utcnow()):
        super().__init__(user_id, revision, timestamp)
        self.employee_name = employee_name

    @staticmethod
    def get_event_type():
        return 'restaurant.employee.fired'

    @staticmethod
    def create_from_event(event: Event):
        return EmployeeFired(
            event.data['employee_name'],
            event.user_id_id,
            event.revision,
            event.time
        )


class MenuItemAdded(DjangoModelTranslatableBaseEvent):

    def __init__(self, menu_item_id: UUID, user_id: int, revision: int, timestamp=datetime.utcnow()):
        super().__init__(user_id, revision, timestamp)
        self.menu_item_id:UUID = menu_item_id

    @staticmethod
    def get_event_type():
        return 'restaurant.menuitem.added'

    def encode_data_before_save(self):
        self.menu_item_id = str(self.menu_item_id)

    def clean_data_post_save(self):
        self.menu_item_id = uuid.UUID(self.menu_item_id)

    @staticmethod
    def create_from_event(event: Event):
        return MenuItemAdded(
            event.data['menu_item_id'],
            event.user_id_id,
            event.revision,
            event.time
        )


class MenuItemRemoved(MenuItemAdded):

    @staticmethod
    def get_event_type():
        return 'restaurant.menuitem.removed'

    @staticmethod
    def create_from_event(event: Event):
        return MenuItemRemoved(
            event.data['menu_item_id'],
            event.user_id_id,
            event.revision,
            event.time
        )



