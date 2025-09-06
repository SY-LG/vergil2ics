"""
Contains functionality to build an iCalendar (.ics) Calendar object
from parsed VergilClass data.
"""
from __future__ import annotations

import datetime
from typing import List
from uuid import uuid5, NAMESPACE_URL

from dateutil.rrule import rrule, WEEKLY
from dateutil.relativedelta import relativedelta
from dateutil.tz import gettz
import ics

from core.models import VergilClass

TZ = gettz('America/New_York')


def build_calendar(vergil_classes: List[VergilClass]) -> ics.Calendar:
    """
    Constructs an ics.Calendar object populated with events from a list of VergilClass objects.

    Each meeting detail and time slot within a VergilClass is converted into
    recurring iCalendar events.

    Args:
        vergil_classes: A list of VergilClass objects to convert into calendar events.

    Returns:
        An ics.Calendar object containing all generated events.
    """
    calendar = ics.Calendar()
    for vergil_class in vergil_classes:
        for meeting_detail in vergil_class.meeting_details:
            for time_slot in meeting_detail.time_slots:
                days_ahead = (time_slot.day_of_week - meeting_detail.begin_date.weekday()) % 7
                first_occurrence_date = meeting_detail.begin_date + relativedelta(days=days_ahead)
                for class_date in rrule(
                    WEEKLY,
                    dtstart=first_occurrence_date,
                    until=meeting_detail.end_date,
                    interval=1,
                ):
                    dt_start = datetime.datetime.combine(class_date, time_slot.start, tzinfo=TZ)
                    dt_end = datetime.datetime.combine(class_date, time_slot.end, tzinfo=TZ)
                    uid = (
                        str(uuid5(NAMESPACE_URL,
                                  vergil_class.short_course_id + dt_start.isoformat()))
                        + '@vergil2ics.local'
                    )

                    event = ics.Event()
                    event.uid = uid
                    event.dtstamp = datetime.datetime.now(tz=TZ)
                    event.begin = dt_start
                    event.end = dt_end
                    event.name = f'{vergil_class.short_course_id} - {vergil_class.name}'
                    event.location = meeting_detail.location
                    event.description = f'Teacher: {meeting_detail.teacher}'
                    calendar.events.add(event)
    return calendar
