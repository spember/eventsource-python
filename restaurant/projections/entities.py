import uuid
from abc import ABCMeta, abstractmethod
from typing import Dict, Callable, Any, List

from restaurant.events.base import BaseEvent
from restaurant.events.menu_item import MenuItemCreated, PriceChanged
from restaurant.events.restaurant import RestaurantOpened, EmployeeHired, EmployeeFired, MenuItemAdded, MenuItemRemoved


class EventableEntity(object):
    """Provides functionality for receiving BaseEvents and applying them"""

    __metaclass__= ABCMeta

    def __init__(self, id: uuid.UUID=None, revision:int=0):
        if id is None:
            self.id = uuid.uuid4()
        else:
            self.id = id
        self.revision = revision
        self.uncommitted_events = []

    @abstractmethod
    def event_map(self) -> Dict[Any, Callable]:
        pass

    def apply(self, event: BaseEvent) -> None:
        if event.revision <= self.revision:
            raise ValueError('Current entity revision is {}. Attempted to apply an event with revision {}'.format(
                self.revision, event.revision))
        if event.revision != self.revision + 1:
            raise ValueError(
                'Attempted to apply an event with revision {} to an entity at revision {}. Possibly missing {} events'
                    .format(event.revision, self.revision, (event.revision - self.revision)))
        self.revision = event.revision
        if event.event_stream_id is None:
            event.set_event_stream_id(self.id)
            event.first_observation = True
            self.uncommitted_events.append(event)
        self.event_map()[event.__class__](event)


class Restaurant(EventableEntity):
    def __init__(self, id: uuid.UUID=None):
        super().__init__(id)
        self.name = ''
        self.year_opened = None
        self.address = ''
        self.employees = []
        self.menu_items: List[MenuItem] = []
        self.menu_item_ids = []

    def event_map(self) -> Dict[Any, Callable]:
        return {
            RestaurantOpened: self.apply_opened,
            EmployeeHired: self.apply_hired,
            EmployeeFired: self.apply_fired,
            MenuItemAdded: self.apply_menu_item_added,
            MenuItemRemoved: self.apply_menu_item_removed
        }

    def apply_opened(self, event:RestaurantOpened) -> None:
        self.name = event.name
        self.year_opened = event.year
        self.address = event.location

    def apply_hired(self, event: EmployeeHired) -> None:
        if event.employee_name not in self.employees:
            self.employees.append(event.employee_name)

    def apply_fired(self, event: EmployeeFired) -> None:
        if event.employee_name in self.employees:
            self.employees.remove(event.employee_name)

    def apply_menu_item_added(self, event: MenuItemAdded) -> None:
        if event.menu_item_id not in self.menu_item_ids:
            self.menu_item_ids.append(event.menu_item_id)

    def apply_menu_item_removed(self, event: MenuItemRemoved) -> None:
        if event.menu_item_id in self.menu_item_ids:
            self.menu_item_ids.remove(event.menu_item_id)


class MenuItem(EventableEntity):
    CATEGORY_APPETIZER = 'appetizer'
    CATEGORY_DRINK = 'drink'
    CATEGORY_ENTREE = 'entre'
    CATEGORY_DESSERT = 'dessert'

    def __init__(self, id: uuid.UUID = None):
        super().__init__(id)
        self.name = ''
        self.category = ''
        self.price_in_cents = 0

    def event_map(self) -> Dict[Any, Callable]:
        return {
            MenuItemCreated: self.apply_created,
            PriceChanged: self.apply_price_delta
        }

    def apply_created(self, event: MenuItemCreated) -> None:
        self.name = event.name
        self.category = event.category

    def apply_price_delta(self, event: PriceChanged) -> None:
        self.price_in_cents = self.price_in_cents + event.delta
