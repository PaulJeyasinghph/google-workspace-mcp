"""
Google Docs Tools for MCP Server
Provides document creation and editing functionality
"""

from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class DocsTools:
    """Google Docs API tools for document operations"""

    def __init__(self, credentials):
        """Initialize Docs service with credentials"""
        self.service = build('docs', 'v1', credentials=credentials)

    def create_document(self, title: str) -> Dict[str, Any]:
        """
        Create a new Google Doc

        Args:
            title: Document title

        Returns:
            Created document details
        """
        try:
            doc = self.service.documents().create(
                body={'title': title}
            ).execute()

            return {
                'success': True,
                'document_id': doc.get('documentId', ''),
                'title': doc.get('title', ''),
                'document_url': f"https://docs.google.com/document/d/{doc.get('documentId', '')}/edit"
            }

        except HttpError as error:
            return {'success': False, 'error': f'Failed to create document: {error}'}

    def get_document(self, document_id: str) -> Dict[str, Any]:
        """
        Get document content

        Args:
            document_id: The document ID

        Returns:
            Document content and metadata
        """
        try:
            doc = self.service.documents().get(documentId=document_id).execute()

            # Extract text content
            content = []
            for element in doc.get('body', {}).get('content', []):
                if 'paragraph' in element:
                    for elem in element['paragraph'].get('elements', []):
                        if 'textRun' in elem:
                            content.append(elem['textRun'].get('content', ''))

            full_text = ''.join(content)

            return {
                'success': True,
                'document_id': doc.get('documentId', ''),
                'title': doc.get('title', ''),
                'content': full_text,
                'document_url': f"https://docs.google.com/document/d/{doc.get('documentId', '')}/edit"
            }

        except HttpError as error:
            return {'success': False, 'error': f'Failed to get document: {error}'}

    def insert_text(
        self,
        document_id: str,
        text: str,
        index: int = 1
    ) -> Dict[str, Any]:
        """
        Insert text into a document

        Args:
            document_id: The document ID
            text: Text to insert
            index: Position to insert (default: 1, beginning of document)

        Returns:
            Operation result
        """
        try:
            requests = [{
                'insertText': {
                    'location': {'index': index},
                    'text': text
                }
            }]

            self.service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()

            return {'success': True, 'message': 'Text inserted successfully'}

        except HttpError as error:
            return {'success': False, 'error': f'Failed to insert text: {error}'}

    def append_text(self, document_id: str, text: str) -> Dict[str, Any]:
        """
        Append text to the end of a document

        Args:
            document_id: The document ID
            text: Text to append

        Returns:
            Operation result
        """
        try:
            # Get document to find end index
            doc = self.service.documents().get(documentId=document_id).execute()

            # Find the end index
            end_index = doc.get('body', {}).get('content', [{}])[-1].get('endIndex', 1)

            # Insert text at end
            requests = [{
                'insertText': {
                    'location': {'index': end_index - 1},
                    'text': text
                }
            }]

            self.service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()

            return {'success': True, 'message': 'Text appended successfully'}

        except HttpError as error:
            return {'success': False, 'error': f'Failed to append text: {error}'}

    def replace_text(
        self,
        document_id: str,
        old_text: str,
        new_text: str,
        match_case: bool = True
    ) -> Dict[str, Any]:
        """
        Replace all occurrences of text in a document

        Args:
            document_id: The document ID
            old_text: Text to find
            new_text: Replacement text
            match_case: Whether to match case

        Returns:
            Operation result
        """
        try:
            requests = [{
                'replaceAllText': {
                    'containsText': {
                        'text': old_text,
                        'matchCase': match_case
                    },
                    'replaceText': new_text
                }
            }]

            result = self.service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()

            occurrences = result.get('replies', [{}])[0].get('replaceAllText', {}).get('occurrencesChanged', 0)

            return {
                'success': True,
                'message': f'Replaced {occurrences} occurrence(s)',
                'occurrences_changed': occurrences
            }

        except HttpError as error:
            return {'success': False, 'error': f'Failed to replace text: {error}'}

    def delete_content_range(
        self,
        document_id: str,
        start_index: int,
        end_index: int
    ) -> Dict[str, Any]:
        """
        Delete content in a specific range

        Args:
            document_id: The document ID
            start_index: Start position
            end_index: End position

        Returns:
            Operation result
        """
        try:
            requests = [{
                'deleteContentRange': {
                    'range': {
                        'startIndex': start_index,
                        'endIndex': end_index
                    }
                }
            }]

            self.service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()

            return {'success': True, 'message': 'Content deleted successfully'}

        except HttpError as error:
            return {'success': False, 'error': f'Failed to delete content: {error}'}

    def format_text(
        self,
        document_id: str,
        start_index: int,
        end_index: int,
        bold: Optional[bool] = None,
        italic: Optional[bool] = None,
        underline: Optional[bool] = None,
        font_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Format text in a document

        Args:
            document_id: The document ID
            start_index: Start position
            end_index: End position
            bold: Make text bold
            italic: Make text italic
            underline: Underline text
            font_size: Font size in points

        Returns:
            Operation result
        """
        try:
            text_style = {}

            if bold is not None:
                text_style['bold'] = bold
            if italic is not None:
                text_style['italic'] = italic
            if underline is not None:
                text_style['underline'] = underline
            if font_size is not None:
                text_style['fontSize'] = {'magnitude': font_size, 'unit': 'PT'}

            requests = [{
                'updateTextStyle': {
                    'range': {
                        'startIndex': start_index,
                        'endIndex': end_index
                    },
                    'textStyle': text_style,
                    'fields': ','.join(text_style.keys())
                }
            }]

            self.service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()

            return {'success': True, 'message': 'Text formatted successfully'}

        except HttpError as error:
            return {'success': False, 'error': f'Failed to format text: {error}'}

    def create_paragraph_bullets(
        self,
        document_id: str,
        start_index: int,
        end_index: int
    ) -> Dict[str, Any]:
        """
        Create bulleted list from paragraphs

        Args:
            document_id: The document ID
            start_index: Start position
            end_index: End position

        Returns:
            Operation result
        """
        try:
            requests = [{
                'createParagraphBullets': {
                    'range': {
                        'startIndex': start_index,
                        'endIndex': end_index
                    },
                    'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE'
                }
            }]

            self.service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()

            return {'success': True, 'message': 'Bullets created successfully'}

        except HttpError as error:
            return {'success': False, 'error': f'Failed to create bullets: {error}'}
