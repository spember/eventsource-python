from pytest import mark

from restaurant.events.restaurant import RestaurantOpened, EmployeeHired, EmployeeFired
from restaurant.projections.entities import Restaurant
from restaurant.services.entities import RestaurantService
from restaurant.services.events import EventPersistenceService


@mark.integration
class TestEntityEventSave:

    def test_basic_save_and_restore(self, transactional_db, test_users):
        restaurant = Restaurant()
        user_id = test_users[0].id
        # typically we don't operate with the events at this 'low' level, but rather have events be the outcome of some
        # service method or user command (e.g. 'OpenRestaurant') which then validates the entity
        event = RestaurantOpened('Bob\'s Cafeeeeee', 2019, '300 Foo Street, Fake City, MA 02144', user_id, 1)
        correction = RestaurantOpened('Bob\'s Cafe', 2019, '123 Test Street, Fake City, MA 02144', user_id, 2)

        restaurant.apply(event)
        restaurant.apply(correction)

        service = EventPersistenceService()
        service.save(restaurant)

        restored_restaurant = RestaurantService().get_current(restaurant.id)

        assert restored_restaurant.revision == 2
        assert restored_restaurant.name == 'Bob\'s Cafe'
        assert restored_restaurant.id == restaurant.id

    def test_multiple_event_types(self, transactional_db, test_users):
        restaurant = Restaurant()
        user_id = test_users[0].id
        restaurant.apply(RestaurantOpened('Bobbie\'s super store', 2019, 'blah', user_id, 1))
        restaurant.apply(RestaurantOpened('Bob\'s Cafe', 2019, '123 Test Street, Fake City, MA 02144', user_id, 2))
        restaurant.apply(EmployeeHired('Jim Bob', user_id, 3))
        restaurant.apply(EmployeeHired('Carl', user_id, 4))
        restaurant.apply(EmployeeHired('Sally', user_id, 5))
        restaurant.apply(EmployeeFired('Carl', user_id, 6))
        service = EventPersistenceService()
        service.save(restaurant)

        restored_restaurant = RestaurantService().get_current(restaurant.id)
        assert restored_restaurant.revision == 6
        assert restored_restaurant.name == 'Bob\'s Cafe'
        assert len(restored_restaurant.employees) == 2
        assert 'Carl' not in restored_restaurant.employees
        assert 'Jim Bob' in restored_restaurant.employees
        assert 'Sally' in restored_restaurant.employees

    def test_multiple_entities(self, transactional_db, test_users):
        restaurant_one = Restaurant()
        restaurant_two = Restaurant()
        user_id = test_users[0].id

        restaurant_one.apply(RestaurantOpened('Bob\'s Cafe', 2019, '123 Test Street, Fake City, MA 02144', user_id, 1))
        restaurant_one.apply(EmployeeHired('Carl', user_id, 2))

        restaurant_two.apply(RestaurantOpened('The Testing Bar', 2017, '125 Test Street, Fake City, MA 02144', user_id, 1))
        restaurant_two.apply(EmployeeHired('Carl', user_id, 2)) #oh no, same person at two restaurants!
        restaurant_two.apply(EmployeeHired('Sam', user_id, 3))

        service = EventPersistenceService()
        service.save(restaurant_one)
        service.save(restaurant_two)
        restaurants = RestaurantService().get_multiple_current([restaurant_one.id, restaurant_two.id])

        assert len(restaurants) == 2

