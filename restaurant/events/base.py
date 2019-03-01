from abc import ABCMeta, abstractmethod
from datetime import datetime
from uuid import UUID

from restaurant.models import Event


class BaseEvent(object):
    """Essentially a wrapper around the Event Model, due to limitations within Django's ORM


    Event's maintain the id of the Event Stream they're attached to, the revision of the change, the user who affected
    the change, and some timestamps.
    An event does not necessarily need an id of it's own, uniqueness can be a composite key of stream_id and revision

    An Event also may or may not trigger a 'side_effect'; sending an email, triggering additional events, executing a
    report to be generated, etc. These 'side_effects' should occur only after the first time they're saved.

    This can generally be accomplished by *not* applying the event_stream_id when first creation. 'applying' an event
    should set the id if not already set, this recognizing that this event is first-observed. Reading from the database
    again should already maintain that id
    """

    def __init__(self, user_id: int, revision: int, timestamp=datetime.utcnow()):
        # no timestamp_recorded, that should happen farther down
        # event data is saved at the child class
        self.event_stream_id: UUID = None
        self.user_id: int = user_id
        self.revision: int = revision
        self.timestamp:datetime = timestamp
        self.first_observation = False

        if self.user_id is None:
            raise ValueError('User Id may not be None')
        if self.revision is None or self.revision < 0:
            raise ValueError('revision must be greater than 0')

    __metaclass__ = ABCMeta

    def set_event_stream_id(self, id: UUID):
        """Don't really need a setter, just here for explicitness"""
        self.event_stream_id = id

    @staticmethod
    @abstractmethod
    def get_event_type():
        pass

    def encode_data_before_save(self):
        pass

    def clean_data_post_save(self):
        pass

    # Considered putting a 'to_django_orm_event' method here - as well as a method to conver from models.Event to
    # a child of BaseEvent, but that would couple the django orm to this model.
    # Created the Adapter below to help with translation

class DjangoModelTranslatableBaseEvent(BaseEvent):

    __metaclass__ = ABCMeta

    @staticmethod
    @abstractmethod
    def create_from_event(event: Event):
        pass
