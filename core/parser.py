"""
Handles parsing class data from the Vergil API into VergilClass objects.
"""
from __future__ import annotations

import datetime
from typing import List

import requests

from core.models import VergilClass, TimeSlot, MeetingDetail


class ClassNotFoundError(Exception):
    """Raised when no class data is found for a given identifier."""

class MultipleClassError(Exception):
    """
    Raised when multiple class data entries are found for an identifier
    that is expected to return a single result.
    """


def _fetch_class_json(class_id: str, calendar_code: str) -> dict:
    """
    Fetches raw JSON data for a specific class from the Vergil API.

    Args:
        class_id: The identifier for the class (e.g., 'ECBM4040E001').
        calendar_code: The academic calendar code (e.g., '20253' for Fall 2025).

    Returns:
        A dictionary containing the raw JSON response from the API.

    Raises:
        requests.exceptions.RequestException: If the API request fails.
    """
    params = {
        'class_identifier': class_id,
        'course_term.term_calendar.term_calendar_code': calendar_code,
    }
    resp = requests.get(
        'https://sas-class.api.columbia.edu/search/classes/',
        params=params,
        timeout=10
    )
    resp.raise_for_status()
    return resp.json()


def _parse_single(data: dict) -> VergilClass:
    """
    Parses a single class's raw data dictionary into a VergilClass object.

    Args:
        data: A dictionary containing the 'attributes' of a single class from the API response.

    Returns:
        A VergilClass object representing the parsed class.
    """
    course_term_json = data['attributes']['course_term']
    meeting_details_json = data['attributes']['meeting_details']
    meeting_details: List[MeetingDetail] = []
    for detail_json in meeting_details_json:
        last_name = detail_json['class_instructor'].get('instructor_last_name', '')
        teacher = detail_json['class_instructor']['instructor_first_name']
        if last_name:
            teacher += ' ' + last_name
        time_slots: List[TimeSlot] = []
        for pattern in detail_json['meeting_pattern']['meetingpatterndetail_set']:
            time_slots.append(
                TimeSlot(
                    day_of_week={'Mo': 0, 'Tu': 1, 'We': 2, 'Th': 3,'Fr': 4,
                                'Sa': 5, 'Su': 6}[pattern['week_day']],
                    start=datetime.time.fromisoformat(pattern['from_time']),
                    end=datetime.time.fromisoformat(pattern['to_time']),
                )
            )
        meeting_details.append(
            MeetingDetail(
                location=detail_json['room']['room_name'],
                teacher=teacher,
                begin_date=datetime.date.fromisoformat(detail_json['begin_date']),
                end_date=datetime.date.fromisoformat(detail_json['end_date']),
                time_slots=time_slots
            )
        )
    return VergilClass(
        name=course_term_json['course_official_title'],
        short_course_id=course_term_json['course_identifier2'],
        meeting_details=meeting_details
    )


def parse(class_ids: List[str], calendar_code: str) -> List[VergilClass]:
    """
    Fetches and parses class data for a list of class IDs.

    Args:
        class_ids: A list of class identifiers to parse.
        calendar_code: The calendar code for the semester.

    Returns:
        A list of VergilClass objects.

    Raises:
        ClassNotFoundError: If no data is found for a specific class ID.
        MultipleClassError: If multiple data entries are found for a class ID.
    """
    classes: List[VergilClass] = []
    for class_id in class_ids:
        raw = _fetch_class_json(class_id, calendar_code)
        datas = raw.get('data', [])
        if len(datas) == 0:
            raise ClassNotFoundError(
                f'No class data found for {class_id}.\n'
                'Check your class ID or semester code!'
            )
        if len(datas) > 1:
            raise MultipleClassError(
                f'Found {len(datas)} class data for {class_id}.\n'
                'Please contact the developer to add more filter!'
            )
        classes.append(_parse_single(datas[0]))
    return classes
