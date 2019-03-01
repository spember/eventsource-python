
from typing import List, Dict
from django.utils import timezone

from restaurant.events.base import BaseEvent, DjangoModelTranslatableBaseEvent
from restaurant.models import Event, User

class DjangoEventTranslatorService(object):

    def __init__(self):
        # put together base event keys with a dummy base_event
        self.root_event_attrs = dir(DjangoModelTranslatableBaseEvent(1, 0))
        self.event_mapping: Dict[str, DjangoModelTranslatableBaseEvent] = {}
        for subclass in DjangoModelTranslatableBaseEvent.__subclasses__():
            self.event_mapping[subclass.get_event_type()] = subclass

    def translate_to_django_models(self, events: List[BaseEvent]) -> List[Event]:
        # maintain list of users
        user_cache = {}
        return list(map(lambda event: self._translate_individual_event(event, user_cache), events))

    def translate_event_to_domain_event(self, event: Event)->BaseEvent:
        domain_event = self.event_mapping[event.type].create_from_event(event)
        domain_event.set_event_stream_id(event.event_stream_id)
        domain_event.clean_data_post_save()
        return domain_event

    def _translate_individual_event(self, event:BaseEvent, user_cache: Dict) -> Event:
        #extract data from non-core events
        # There are more pythonic ways to do the following, but I'm explicit here to make it clear what's happening
        # as we translate the DomainEvents into the Django ORM models
        if event.user_id in user_cache.keys():
            user = user_cache[event.user_id]
        else:
            user = User.objects.get(id=event.user_id)
            user_cache[user.id] = user
        outcome = Event()
        outcome.event_stream_id = event.event_stream_id
        outcome.revision = event.revision
        outcome.user_id = user
        outcome.time = timezone.make_aware(event.timestamp, timezone.get_current_timezone())
        outcome.type = event.__class__.get_event_type()
        outcome.data = self._build_data_blob(event)
        return outcome

    def _build_data_blob(self, event: BaseEvent) -> Dict:
        data = {}
        event.encode_data_before_save()
        for attr in dir(event):
            if attr not in self.root_event_attrs and not attr.startswith("_"):
                data[attr] = event.__getattribute__(attr)

        return data
