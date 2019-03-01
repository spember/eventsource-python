import pytest
from pytest import mark

from restaurant.projections.entities import MenuItem
from restaurant.services.entities import RestaurantService, MenuItemService


@mark.integration
class TestRestaurantService:

    def test_restaurant_commands(self, transactional_db, test_users):
        service = RestaurantService()
        bobs = service.open_restaurant(test_users[0], 'Bob\'s Coffee Shop', '123 Test Street')
        service.hire_employees(test_users[0], bobs, ['Sam', 'Mark', 'Alice'])

        with pytest.raises(ValueError):
            service.fire_employee(test_users[1], bobs, 'Blah')

        service.fire_employee(test_users[1], bobs, 'Mark')

        bobs = service.get_current(bobs.id)
        assert len(bobs.employees) == 2
        assert 'Mark' not in bobs.employees
        # wait, why'd user [1] fire Mark?

        service.hire_employees(test_users[0], bobs, ['Mark'])
        bobs = service.get_current(bobs.id)
        assert len(bobs.employees) == 3
        assert 'Mark' in bobs.employees


    def test_menu(self, transactional_db, test_users):
        service = RestaurantService()
        menu_item_service = MenuItemService()
        coffee_shop = service.open_restaurant(test_users[0], 'The Corner Shop', '123 Test Street')
        service.hire_employees(test_users[0], coffee_shop, ['Sam', 'Sally'])

        coffee_large = menu_item_service.create_menu_item(test_users[0], 'Coffee - L', MenuItem.CATEGORY_DRINK, 250)
        coffee_medium = menu_item_service.create_menu_item(test_users[0], 'Coffee - M', MenuItem.CATEGORY_DRINK, 250)
        menu_item_service.set_price(test_users[0], coffee_large, 299)

        service.add_items_to_menu(test_users[0], coffee_shop, [coffee_large, coffee_medium])

        refreshed = service.get_current(coffee_shop.id)
        service.load_associated(refreshed)

        assert len(refreshed.menu_items) == 2


@mark.integration
class TestMenuItemService:

    def test_menu_item(self, transactional_db, test_users):
        service = MenuItemService()
        lasagna = service.create_menu_item(test_users[0], 'House Special: Lasagna', MenuItem.CATEGORY_ENTREE, 1499)
        cola = service.create_menu_item(test_users[0], 'Coca Cola - L', MenuItem.CATEGORY_DRINK, 299)

        service.set_price(test_users[0], lasagna, 1699)
        service.set_price(test_users[0], cola, 325)
        service.set_price(test_users[0], lasagna, 1299)
        service.set_price(test_users[0], lasagna, 1995)

        service.set_price(test_users[0], cola, 125)
        service.set_price(test_users[0], cola, 225)
        service.set_price(test_users[0], cola, 275)

        l2 = service.get_current(lasagna.id)
        assert l2 is not None

        items = service.get_multiple_current([lasagna.id, cola.id])
        assert len(items) == 2

        assert items[0].id == lasagna.id
        assert items[0].name == 'House Special: Lasagna'
        assert items[0].category == MenuItem.CATEGORY_ENTREE
        assert items[0].price_in_cents == 1995

        assert items[1].id == cola.id
        assert items[1].name == 'Coca Cola - L'
        assert items[1].category == MenuItem.CATEGORY_DRINK
        assert items[1].price_in_cents == 275



