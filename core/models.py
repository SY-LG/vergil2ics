"""
Defines the data models used to represent Vergil classes and their meeting details.
"""
from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class TimeSlot:
    """Represents a specific time range on a given day of the week for a class meeting."""
    day_of_week: int # 0=Mon … 6=Sun
    start: datetime.time
    end: datetime.time


@dataclass(frozen=True)
class MeetingDetail:
    """
    Represents the details of a recurring meeting block for a Vergil class,
    including location, teacher, date range, and specific time slots.
    """
    location: str
    teacher: str
    begin_date: datetime.date
    end_date: datetime.date
    time_slots: List[TimeSlot] = field(default_factory=list)


@dataclass(frozen=True)
class VergilClass:
    """
    Represents a single class retrieved from Vergil, encompassing its name,
    short identifier, and all associated meeting details.
    """
    name: str
    short_course_id: str
    meeting_details: List[MeetingDetail] = field(default_factory=list)

    def __str__(self) -> str:
        chunks = []
        for md in self.meeting_details:
            time_slot_strs = [
                ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][ts.day_of_week] +
                f' {ts.start.strftime("%I:%M %p")} - {ts.end.strftime("%I:%M %p")}'
                for ts in md.time_slots
            ]
            chunks.append(
                f'Location: {md.location}\n'
                f'Teacher: {md.teacher}\n'
                f'Dates: {md.begin_date:%B %d, %Y} to {md.end_date:%B %d, %Y}\n'
                f'Schedule: {"; ".join(time_slot_strs)}'
            )
        return (
            f'VergilClass: {self.short_course_id} {self.name}\n'
            + '\n'.join(chunks)
        )
