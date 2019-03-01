import logging
from datetime import datetime
from typing import List
from uuid import UUID

from restaurant.events.base import BaseEvent
from restaurant.models import Event
from restaurant.projections.entities import EventableEntity
from restaurant.services.translation import DjangoEventTranslatorService

log = logging.getLogger(__name__)


class EventPersistenceService(object):

    def __init__(self):
        self.translation_service = DjangoEventTranslatorService()

    def save(self, entity: EventableEntity) -> None:
        log.debug('Persisting {} events for entity {}'.format(len(entity.uncommitted_events), entity.id))
        Event.objects.bulk_create(self.translation_service.translate_to_django_models(entity.uncommitted_events),
                                  batch_size=100)
        entity.uncommitted_events = []


class EventQueryService(object):

    def __init__(self):
        self.translation_service = DjangoEventTranslatorService()

    def find_events_by_id(self, event_stream_id: UUID, max_date=datetime.utcnow()) -> List[BaseEvent]:
        return list(map(self.translation_service.translate_event_to_domain_event,
                   Event.objects.filter(event_stream_id=event_stream_id, time__lte=max_date).order_by('revision').all()))

    def count_events_by_id(self, event_stream_id: UUID) -> int:
        return Event.objects.filter(event_stream_id=event_stream_id).count()

    def find_events_for_id_in(self, event_stream_ids: List[UUID], max_date=datetime.utcnow()) -> List[BaseEvent]:
        return list(map(self.translation_service.translate_event_to_domain_event,
                        Event.objects.filter(event_stream_id__in=event_stream_ids, time__lte=max_date)
                        .order_by('revision').all()))
