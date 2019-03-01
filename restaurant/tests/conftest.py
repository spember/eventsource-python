from typing import List

from pytest import fixture

from restaurant.models import User


@fixture(scope="function")
def test_users(transactional_db) -> List[User]:
    User.objects.create(
        id=100,
        first_name='Test',
        last_name='Testington',
        email='test@test.com'
    )

    User.objects.create(
        id=25,
        first_name='Alice',
        last_name='Tester',
        email='alice@test.com'
    )
    return User.objects.all()
