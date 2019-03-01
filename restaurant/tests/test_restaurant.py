from pytest import raises

from restaurant.events.restaurant import RestaurantOpened
from restaurant.projections.entities import Restaurant


class TestRestaurantEvents:

    def test_opened(self):
        restaurant = Restaurant()
        assert restaurant.name == ''
        assert restaurant.year_opened is None
        assert restaurant.address == ''
        assert restaurant.id is not None
        assert restaurant.revision == 0

        user_id = 100
        event = RestaurantOpened('Bob\'s Cafe', 2019, '123 Test Street, Fake City, MA 02144', user_id, 1)

        restaurant.apply(event)
        assert restaurant.revision == 1
        assert restaurant.name == 'Bob\'s Cafe'
        assert restaurant.year_opened == 2019
        assert restaurant.address == '123 Test Street, Fake City, MA 02144'
        assert event.event_stream_id == restaurant.id
        assert event.first_observation is True

    def test_events_can_be_corrective(self):
        restaurant = Restaurant()
        user_id = 100
        event = RestaurantOpened('Bob\'s Cafeeeeee', 2019, '300 Foo Street, Fake City, MA 02144', user_id, 1)
        correction = RestaurantOpened('Bob\'s Cafe', 2019, '123 Test Street, Fake City, MA 02144', user_id, 2)

        restaurant.apply(event)
        restaurant.apply(correction)

        assert restaurant.revision == 2
        assert restaurant.name == 'Bob\'s Cafe'
        assert restaurant.year_opened == 2019
        assert restaurant.address == '123 Test Street, Fake City, MA 02144'
        assert len(restaurant.uncommitted_events) == 2

    def test_events_must_be_aware_of_and_increment_revision(self):
        restaurant = Restaurant()
        user_id = 50
        event = RestaurantOpened('Bob\'s Cafeeeeee', 2019, '300 Foo Street, Fake City, MA 02144', user_id, 1)
        not_incremented = RestaurantOpened('Bob\'s Cafe', 2019, '123 Test Street, Fake City, MA 02144', user_id, 1)
        less_than = RestaurantOpened('Bob\'s Cafe', 2019, '123 Test Street, Fake City, MA 02144', user_id, 0)
        too_far = RestaurantOpened('Bob\'s Cafe', 2019, '123 Test Street, Fake City, MA 02144', user_id, 3)

        restaurant.apply(event)
        with raises(ValueError):
            restaurant.apply(not_incremented)

        with raises(ValueError):
            restaurant.apply(less_than)

        with raises(ValueError):
            restaurant.apply(too_far)
