"""
Google Chat Tools for MCP Server
Provides chat messaging and space management functionality
"""

from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class ChatTools:
    """Google Chat API tools for messaging and space management"""

    def __init__(self, credentials):
        """Initialize Chat service with credentials"""
        self.service = build('chat', 'v1', credentials=credentials)

    def list_spaces(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        List all Chat spaces the user is a member of

        Args:
            max_results: Maximum number of spaces to return

        Returns:
            List of spaces
        """
        try:
            results = self.service.spaces().list(
                pageSize=max_results
            ).execute()

            spaces = results.get('spaces', [])

            return [{
                'name': space.get('name', ''),
                'displayName': space.get('displayName', ''),
                'type': space.get('type', ''),
                'spaceType': space.get('spaceType', '')
            } for space in spaces]

        except HttpError as error:
            return [{'error': f'Failed to list spaces: {error}'}]

    def send_message(
        self,
        space: str,
        text: str,
        thread_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a message to a Chat space

        Args:
            space: Space name (e.g., 'spaces/SPACE_ID')
            text: Message text
            thread_key: Optional thread key for threading messages

        Returns:
            Sent message details
        """
        try:
            body = {'text': text}

            if thread_key:
                body['thread'] = {'threadKey': thread_key}

            message = self.service.spaces().messages().create(
                parent=space,
                body=body
            ).execute()

            return {
                'success': True,
                'message_name': message.get('name', ''),
                'create_time': message.get('createTime', ''),
                'text': message.get('text', '')
            }

        except HttpError as error:
            return {'success': False, 'error': f'Failed to send message: {error}'}

    def get_message(self, message_name: str) -> Dict[str, Any]:
        """
        Get a specific Chat message

        Args:
            message_name: Full message name (e.g., 'spaces/SPACE_ID/messages/MESSAGE_ID')

        Returns:
            Message details
        """
        try:
            message = self.service.spaces().messages().get(
                name=message_name
            ).execute()

            return {
                'name': message.get('name', ''),
                'text': message.get('text', ''),
                'sender': message.get('sender', {}).get('displayName', ''),
                'createTime': message.get('createTime', ''),
                'thread': message.get('thread', {})
            }

        except HttpError as error:
            return {'error': f'Failed to get message: {error}'}

    def list_messages(
        self,
        space: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        List messages in a Chat space

        Args:
            space: Space name (e.g., 'spaces/SPACE_ID')
            max_results: Maximum number of messages to return

        Returns:
            List of messages
        """
        try:
            results = self.service.spaces().messages().list(
                parent=space,
                pageSize=max_results
            ).execute()

            messages = results.get('messages', [])

            return [{
                'name': msg.get('name', ''),
                'text': msg.get('text', ''),
                'sender': msg.get('sender', {}).get('displayName', ''),
                'createTime': msg.get('createTime', '')
            } for msg in messages]

        except HttpError as error:
            return [{'error': f'Failed to list messages: {error}'}]

    def delete_message(self, message_name: str) -> Dict[str, Any]:
        """
        Delete a Chat message

        Args:
            message_name: Full message name

        Returns:
            Operation result
        """
        try:
            self.service.spaces().messages().delete(
                name=message_name
            ).execute()

            return {'success': True, 'message': 'Message deleted successfully'}

        except HttpError as error:
            return {'success': False, 'error': f'Failed to delete message: {error}'}

    def create_space(self, display_name: str) -> Dict[str, Any]:
        """
        Create a new Chat space

        Args:
            display_name: Display name for the space

        Returns:
            Created space details
        """
        try:
            space = self.service.spaces().create(
                body={
                    'displayName': display_name,
                    'spaceType': 'SPACE'
                }
            ).execute()

            return {
                'success': True,
                'space_name': space.get('name', ''),
                'display_name': space.get('displayName', '')
            }

        except HttpError as error:
            return {'success': False, 'error': f'Failed to create space: {error}'}
