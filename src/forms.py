"""
Google Forms Tools for MCP Server
Provides form creation and response reading functionality
"""

from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class FormsTools:
    """Google Forms API tools for form management"""

    def __init__(self, credentials):
        """Initialize Forms service with credentials"""
        self.service = build('forms', 'v1', credentials=credentials)

    def create_form(
        self,
        title: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new form

        Args:
            title: Form title
            description: Optional form description

        Returns:
            Created form details
        """
        try:
            form = {
                'info': {
                    'title': title
                }
            }

            if description:
                form['info']['documentTitle'] = description

            result = self.service.forms().create(body=form).execute()

            return {
                'success': True,
                'form_id': result.get('formId', ''),
                'responder_uri': result.get('responderUri', ''),
                'title': result.get('info', {}).get('title', '')
            }

        except HttpError as error:
            return {'success': False, 'error': f'Failed to create form: {error}'}

    def get_form(self, form_id: str) -> Dict[str, Any]:
        """
        Get form details

        Args:
            form_id: The form ID

        Returns:
            Form metadata and questions
        """
        try:
            form = self.service.forms().get(formId=form_id).execute()

            questions = []
            for item in form.get('items', []):
                if 'questionItem' in item:
                    q = item['questionItem']['question']
                    questions.append({
                        'questionId': q.get('questionId', ''),
                        'title': item.get('title', ''),
                        'type': list(q.keys())[0] if q else 'unknown'
                    })

            return {
                'success': True,
                'form_id': form.get('formId', ''),
                'title': form.get('info', {}).get('title', ''),
                'description': form.get('info', {}).get('description', ''),
                'responder_uri': form.get('responderUri', ''),
                'questions': questions
            }

        except HttpError as error:
            return {'success': False, 'error': f'Failed to get form: {error}'}

    def add_question(
        self,
        form_id: str,
        question_title: str,
        question_type: str = 'SHORT_ANSWER',
        required: bool = False,
        choices: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Add a question to a form

        Args:
            form_id: The form ID
            question_title: Question text
            question_type: Type of question ('SHORT_ANSWER', 'PARAGRAPH', 'MULTIPLE_CHOICE', 'CHECKBOX', 'DROP_DOWN')
            required: Whether the question is required
            choices: List of choices for multiple choice questions

        Returns:
            Operation result
        """
        try:
            question_item = {
                'title': question_title,
                'questionItem': {
                    'question': {
                        'required': required
                    }
                }
            }

            # Add question type specific configuration
            if question_type == 'SHORT_ANSWER':
                question_item['questionItem']['question']['textQuestion'] = {
                    'paragraph': False
                }
            elif question_type == 'PARAGRAPH':
                question_item['questionItem']['question']['textQuestion'] = {
                    'paragraph': True
                }
            elif question_type in ['MULTIPLE_CHOICE', 'CHECKBOX', 'DROP_DOWN']:
                if not choices:
                    return {'success': False, 'error': 'Choices required for this question type'}

                options = [{'value': choice} for choice in choices]

                if question_type == 'MULTIPLE_CHOICE':
                    question_item['questionItem']['question']['choiceQuestion'] = {
                        'type': 'RADIO',
                        'options': options
                    }
                elif question_type == 'CHECKBOX':
                    question_item['questionItem']['question']['choiceQuestion'] = {
                        'type': 'CHECKBOX',
                        'options': options
                    }
                elif question_type == 'DROP_DOWN':
                    question_item['questionItem']['question']['choiceQuestion'] = {
                        'type': 'DROP_DOWN',
                        'options': options
                    }

            # Create the update request
            request = {
                'requests': [{
                    'createItem': {
                        'item': question_item,
                        'location': {'index': 0}
                    }
                }]
            }

            self.service.forms().batchUpdate(
                formId=form_id,
                body=request
            ).execute()

            return {'success': True, 'message': 'Question added successfully'}

        except HttpError as error:
            return {'success': False, 'error': f'Failed to add question: {error}'}

    def get_responses(self, form_id: str) -> Dict[str, Any]:
        """
        Get all responses for a form

        Args:
            form_id: The form ID

        Returns:
            List of form responses
        """
        try:
            responses = self.service.forms().responses().list(
                formId=form_id
            ).execute()

            response_list = []
            for response in responses.get('responses', []):
                answers = {}
                for question_id, answer in response.get('answers', {}).items():
                    text_answers = answer.get('textAnswers', {}).get('answers', [])
                    if text_answers:
                        answers[question_id] = [a.get('value', '') for a in text_answers]

                response_list.append({
                    'response_id': response.get('responseId', ''),
                    'create_time': response.get('createTime', ''),
                    'last_submitted_time': response.get('lastSubmittedTime', ''),
                    'answers': answers
                })

            return {
                'success': True,
                'form_id': form_id,
                'total_responses': len(response_list),
                'responses': response_list
            }

        except HttpError as error:
            return {'success': False, 'error': f'Failed to get responses: {error}'}

    def get_response(self, form_id: str, response_id: str) -> Dict[str, Any]:
        """
        Get a specific form response

        Args:
            form_id: The form ID
            response_id: The response ID

        Returns:
            Response details
        """
        try:
            response = self.service.forms().responses().get(
                formId=form_id,
                responseId=response_id
            ).execute()

            answers = {}
            for question_id, answer in response.get('answers', {}).items():
                text_answers = answer.get('textAnswers', {}).get('answers', [])
                if text_answers:
                    answers[question_id] = [a.get('value', '') for a in text_answers]

            return {
                'success': True,
                'response_id': response.get('responseId', ''),
                'create_time': response.get('createTime', ''),
                'last_submitted_time': response.get('lastSubmittedTime', ''),
                'answers': answers
            }

        except HttpError as error:
            return {'success': False, 'error': f'Failed to get response: {error}'}
