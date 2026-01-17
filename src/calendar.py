"""
Google Calendar Tools for MCP Server
Provides calendar event management functionality
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class CalendarTools:
    """Google Calendar API tools for event management"""

    def __init__(self, credentials):
        """Initialize Calendar service with credentials"""
        self.service = build('calendar', 'v3', credentials=credentials)

    def list_events(
        self,
        max_results: int = 10,
        calendar_id: str = 'primary',
        time_min: Optional[str] = None,
        time_max: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List calendar events

        Args:
            max_results: Maximum number of events to return
            calendar_id: Calendar ID (default: 'primary')
            time_min: Lower bound (RFC3339 timestamp)
            time_max: Upper bound (RFC3339 timestamp)

        Returns:
            List of events
        """
        try:
            params = {
                'calendarId': calendar_id,
                'maxResults': max_results,
                'singleEvents': True,
                'orderBy': 'startTime'
            }

            if time_min:
                params['timeMin'] = time_min
            else:
                params['timeMin'] = datetime.utcnow().isoformat() + 'Z'

            if time_max:
                params['timeMax'] = time_max

            results = self.service.events().list(**params).execute()
            events = results.get('items', [])

            return [{
                'id': event.get('id', ''),
                'summary': event.get('summary', 'No title'),
                'start': event.get('start', {}).get('dateTime', event.get('start', {}).get('date', '')),
                'end': event.get('end', {}).get('dateTime', event.get('end', {}).get('date', '')),
                'description': event.get('description', ''),
                'location': event.get('location', ''),
                'attendees': [a.get('email', '') for a in event.get('attendees', [])],
                'htmlLink': event.get('htmlLink', '')
            } for event in events]

        except HttpError as error:
            return [{'error': f'Failed to list events: {error}'}]

    def get_event(self, event_id: str, calendar_id: str = 'primary') -> Dict[str, Any]:
        """
        Get a specific calendar event

        Args:
            event_id: The event ID
            calendar_id: Calendar ID (default: 'primary')

        Returns:
            Event details
        """
        try:
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()

            return {
                'success': True,
                'id': event.get('id', ''),
                'summary': event.get('summary', ''),
                'description': event.get('description', ''),
                'location': event.get('location', ''),
                'start': event.get('start', {}),
                'end': event.get('end', {}),
                'attendees': event.get('attendees', []),
                'htmlLink': event.get('htmlLink', '')
            }

        except HttpError as error:
            return {'success': False, 'error': f'Failed to get event: {error}'}

    def create_event(
        self,
        summary: str,
        start_time: str,
        end_time: str,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        calendar_id: str = 'primary'
    ) -> Dict[str, Any]:
        """
        Create a calendar event

        Args:
            summary: Event title
            start_time: Start time (RFC3339 timestamp)
            end_time: End time (RFC3339 timestamp)
            description: Event description
            location: Event location
            attendees: List of attendee emails
            calendar_id: Calendar ID (default: 'primary')

        Returns:
            Created event details
        """
        try:
            event = {
                'summary': summary,
                'start': {'dateTime': start_time, 'timeZone': 'UTC'},
                'end': {'dateTime': end_time, 'timeZone': 'UTC'}
            }

            if description:
                event['description'] = description

            if location:
                event['location'] = location

            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]

            created_event = self.service.events().insert(
                calendarId=calendar_id,
                body=event
            ).execute()

            return {
                'success': True,
                'event_id': created_event.get('id', ''),
                'summary': created_event.get('summary', ''),
                'start': created_event.get('start', {}).get('dateTime', ''),
                'end': created_event.get('end', {}).get('dateTime', ''),
                'htmlLink': created_event.get('htmlLink', '')
            }

        except HttpError as error:
            return {'success': False, 'error': f'Failed to create event: {error}'}

    def update_event(
        self,
        event_id: str,
        summary: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        calendar_id: str = 'primary'
    ) -> Dict[str, Any]:
        """
        Update a calendar event

        Args:
            event_id: The event ID
            summary: New event title
            start_time: New start time
            end_time: New end time
            description: New description
            location: New location
            calendar_id: Calendar ID (default: 'primary')

        Returns:
            Updated event details
        """
        try:
            # Get existing event
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()

            # Update fields
            if summary:
                event['summary'] = summary
            if start_time:
                event['start'] = {'dateTime': start_time, 'timeZone': 'UTC'}
            if end_time:
                event['end'] = {'dateTime': end_time, 'timeZone': 'UTC'}
            if description:
                event['description'] = description
            if location:
                event['location'] = location

            updated_event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event
            ).execute()

            return {
                'success': True,
                'event_id': updated_event.get('id', ''),
                'summary': updated_event.get('summary', ''),
                'htmlLink': updated_event.get('htmlLink', '')
            }

        except HttpError as error:
            return {'success': False, 'error': f'Failed to update event: {error}'}

    def delete_event(self, event_id: str, calendar_id: str = 'primary') -> Dict[str, Any]:
        """
        Delete a calendar event

        Args:
            event_id: The event ID
            calendar_id: Calendar ID (default: 'primary')

        Returns:
            Operation result
        """
        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()

            return {'success': True, 'message': 'Event deleted successfully'}

        except HttpError as error:
            return {'success': False, 'error': f'Failed to delete event: {error}'}

    def list_calendars(self) -> List[Dict[str, Any]]:
        """
        List all calendars

        Returns:
            List of calendars
        """
        try:
            calendar_list = self.service.calendarList().list().execute()
            calendars = calendar_list.get('items', [])

            return [{
                'id': cal.get('id', ''),
                'summary': cal.get('summary', ''),
                'description': cal.get('description', ''),
                'timeZone': cal.get('timeZone', ''),
                'primary': cal.get('primary', False)
            } for cal in calendars]

        except HttpError as error:
            return [{'error': f'Failed to list calendars: {error}'}]
