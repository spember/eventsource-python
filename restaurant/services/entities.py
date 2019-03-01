from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from restaurant.events.base import BaseEvent
from restaurant.events.menu_item import MenuItemCreated, PriceChanged
from restaurant.events.restaurant import RestaurantOpened, EmployeeHired, EmployeeFired, MenuItemAdded, MenuItemRemoved
from restaurant.models import User
from restaurant.projections.entities import Restaurant, MenuItem, EventableEntity
from restaurant.services.events import EventQueryService, EventPersistenceService


class BaseEntityService:

    def __init__(self):
        self._event_persistence_service = EventPersistenceService()
        self._event_query_service = EventQueryService()

    __metaclass__ = ABCMeta

    def _load_entity_up_to(self, event_stream_id: UUID, time=datetime.utcnow()):
        events = self._event_query_service.find_events_by_id(event_stream_id, time)
        if len(events) == 0:
            return None
        return self._build_entity_for_events(event_stream_id, events)

    def _load_multiple_up_to(self, ids: List[UUID], time=datetime.utcnow()) -> List:
        entities = []
        event_group = {}
        for event in self._event_query_service.find_events_for_id_in(ids, time):
            if event.event_stream_id not in event_group.keys():
                event_group[event.event_stream_id] = []
            event_group[event.event_stream_id].append(event)

        for event_stream_id in event_group.keys():
            entities.append(self._build_entity_for_events(event_stream_id, event_group[event_stream_id]))
        return entities

    def _build_entity_for_events(self, event_stream_id: UUID, events: List[BaseEvent]) -> EventableEntity:
        entity = self._get_base_entity(event_stream_id)
        for event in events:
            entity.apply(event)
        return entity

    @abstractmethod
    def _get_base_entity(self, event_stream_id: UUID) -> EventableEntity:
        pass


class RestaurantService(BaseEntityService):

    def get_current(self, id: UUID) -> Optional[Restaurant]:
       return self._load_entity_up_to(id)

    def get_multiple_current(self, ids: List[UUID]) -> List[Restaurant]:
        return self._load_multiple_up_to(ids)
    # todo: replace both of the above with a RestuarauntQuery object and the following with a Restaurant Command

    def load_associated(self, restaraunt: Restaurant) -> None:
        restaraunt.menu_items = MenuItemService().get_multiple_current(restaraunt.menu_item_ids)

    def open_restaurant(self, user: User, name:str, location:str, year=datetime.utcnow().year) -> Restaurant:
        restaurant = Restaurant()
        restaurant.apply(RestaurantOpened(name, year, location, user.id, 1))
        self._event_persistence_service.save(restaurant)
        return restaurant

    def hire_employees(self, user: User, restaurant: Restaurant, employees: List[str]) -> None:
        """Hire emplyees for a restaurant. Restaurant must be at current state"""
        for employee in employees:
            restaurant.apply(EmployeeHired(employee, user.id, restaurant.revision+1))
        self._event_persistence_service.save(restaurant)

    def fire_employee(self, user: User, restaurant: Restaurant, employee: str) -> None:
        if employee in restaurant.employees:
            restaurant.apply(EmployeeFired(employee, user.id, restaurant.revision+1))
            self._event_persistence_service.save(restaurant)
        else:
            raise ValueError("Employee {} doesn't work at {}".format(employee, restaurant.name))

    def add_items_to_menu(self, user: User, restaurant: Restaurant, items: List[MenuItem]) -> None:
        for item in items:
            restaurant.apply(MenuItemAdded(item.id, user.id, restaurant.revision + 1))
            restaurant.menu_items.append(item)
        self._event_persistence_service.save(restaurant)

    def remove_items_from_menu(self, user: User, restaurant: Restaurant, items: List[MenuItem]) -> None:
        for item in items:
            restaurant.apply(MenuItemRemoved(item.id, user.id, restaurant.revision + 1))
            restaurant.menu_items.remove(item)
        self._event_persistence_service.save(restaurant)

    def _get_base_entity(self, event_stream_id: UUID) -> EventableEntity:
        return Restaurant(event_stream_id)

    def _restaurant_exists(self, restaurant_id: UUID) -> bool:
        return self._event_query_service.count_events_by_id(restaurant_id) > 0


class MenuItemService(BaseEntityService):

    def get_current(self, id: UUID) -> Optional[MenuItem]:
        return self._load_entity_up_to(id)

    def get_multiple_current(self, ids: List[UUID]) -> List[MenuItem]:
        return self._load_multiple_up_to(ids)

    def create_menu_item(self, user: User, name: str, category: str, price_in_cents: int) -> MenuItem:
        menu_item = MenuItem()
        menu_item.apply(MenuItemCreated(name, category, user.id, 1))
        # menu_item.apply(PriceChanged(price_in_cents - menu_item.price_in_cents, user.id, 1))
        self._set_price_pure(user, menu_item, price_in_cents)
        self._event_persistence_service.save(menu_item)
        return menu_item

    def set_price(self, user: User, menu_item: MenuItem, new_price_in_cents: int) -> None:
        # menu_item.apply(PriceChanged(new_price_in_cents - menu_item.price_in_cents, user.id, menu_item.revision + 1))
        self._set_price_pure(user, menu_item, new_price_in_cents)
        self._event_persistence_service.save(menu_item)

    def _set_price_pure(self, user: User, menu_item: MenuItem, new_price_in_cents: int) -> None:
        menu_item.apply(PriceChanged(new_price_in_cents - menu_item.price_in_cents, user.id, menu_item.revision + 1))

    def _get_base_entity(self, event_stream_id: UUID) -> EventableEntity:
        return MenuItem(event_stream_id)
