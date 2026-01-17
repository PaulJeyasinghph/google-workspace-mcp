"""
Gmail Tools for MCP Server
Provides email reading, sending, and search functionality
"""

import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GmailTools:
    """Gmail API tools for reading and sending emails"""

    def __init__(self, credentials):
        """Initialize Gmail service with credentials"""
        self.service = build('gmail', 'v1', credentials=credentials)

    def list_messages(
        self,
        max_results: int = 10,
        query: Optional[str] = None,
        label_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        List Gmail messages

        Args:
            max_results: Maximum number of messages to return
            query: Gmail search query (e.g., "from:example@gmail.com")
            label_ids: Filter by label IDs (e.g., ["INBOX", "UNREAD"])

        Returns:
            List of message summaries
        """
        try:
            params = {
                'userId': 'me',
                'maxResults': max_results
            }

            if query:
                params['q'] = query

            if label_ids:
                params['labelIds'] = label_ids

            results = self.service.users().messages().list(**params).execute()
            messages = results.get('messages', [])

            # Fetch details for each message
            detailed_messages = []
            for msg in messages:
                detail = self.get_message(msg['id'])
                if detail:
                    detailed_messages.append(detail)

            return detailed_messages

        except HttpError as error:
            return [{'error': f'Gmail API error: {error}'}]

    def get_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific Gmail message by ID

        Args:
            message_id: The message ID

        Returns:
            Message details including headers and body
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            # Extract headers
            headers = {}
            for header in message['payload'].get('headers', []):
                name = header['name'].lower()
                if name in ['from', 'to', 'subject', 'date']:
                    headers[name] = header['value']

            # Extract body
            body = self._get_message_body(message['payload'])

            return {
                'id': message['id'],
                'threadId': message['threadId'],
                'snippet': message.get('snippet', ''),
                'headers': headers,
                'body': body
            }

        except HttpError as error:
            return {'error': f'Failed to get message: {error}'}

    def _get_message_body(self, payload: Dict[str, Any]) -> str:
        """Extract message body from payload"""
        body = ""

        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
                        break
                elif 'parts' in part:
                    body = self._get_message_body(part)
                    if body:
                        break
        elif 'body' in payload and 'data' in payload['body']:
            body = base64.urlsafe_b64decode(
                payload['body']['data']
            ).decode('utf-8')

        return body

    def send_message(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send an email

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)

        Returns:
            Sent message details
        """
        try:
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject

            if cc:
                message['cc'] = cc
            if bcc:
                message['bcc'] = bcc

            raw_message = base64.urlsafe_b64encode(
                message.as_bytes()
            ).decode('utf-8')

            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()

            return {
                'success': True,
                'message_id': sent_message['id'],
                'thread_id': sent_message['threadId']
            }

        except HttpError as error:
            return {'success': False, 'error': f'Failed to send email: {error}'}

    def search_messages(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search Gmail messages with advanced query

        Args:
            query: Gmail search query
            max_results: Maximum number of results

        Returns:
            List of matching messages
        """
        return self.list_messages(max_results=max_results, query=query)

    def mark_as_read(self, message_id: str) -> Dict[str, Any]:
        """
        Mark a message as read

        Args:
            message_id: The message ID

        Returns:
            Operation result
        """
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()

            return {'success': True, 'message': 'Message marked as read'}

        except HttpError as error:
            return {'success': False, 'error': f'Failed to mark as read: {error}'}

    def mark_as_unread(self, message_id: str) -> Dict[str, Any]:
        """
        Mark a message as unread

        Args:
            message_id: The message ID

        Returns:
            Operation result
        """
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': ['UNREAD']}
            ).execute()

            return {'success': True, 'message': 'Message marked as unread'}

        except HttpError as error:
            return {'success': False, 'error': f'Failed to mark as unread: {error}'}

    def delete_message(self, message_id: str) -> Dict[str, Any]:
        """
        Delete a message (move to trash)

        Args:
            message_id: The message ID

        Returns:
            Operation result
        """
        try:
            self.service.users().messages().trash(
                userId='me',
                id=message_id
            ).execute()

            return {'success': True, 'message': 'Message moved to trash'}

        except HttpError as error:
            return {'success': False, 'error': f'Failed to delete message: {error}'}
