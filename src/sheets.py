"""
Google Sheets Tools for MCP Server
Provides spreadsheet reading, writing, and manipulation functionality
"""

from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class SheetsTools:
    """Google Sheets API tools for spreadsheet operations"""

    def __init__(self, credentials):
        """Initialize Sheets service with credentials"""
        self.service = build('sheets', 'v4', credentials=credentials)

    def create_spreadsheet(
        self,
        title: str,
        sheet_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new spreadsheet

        Args:
            title: Spreadsheet title
            sheet_names: Optional list of sheet names to create

        Returns:
            Created spreadsheet details
        """
        try:
            body = {'properties': {'title': title}}

            if sheet_names:
                body['sheets'] = [
                    {'properties': {'title': name}} for name in sheet_names
                ]

            spreadsheet = self.service.spreadsheets().create(
                body=body
            ).execute()

            return {
                'success': True,
                'spreadsheet_id': spreadsheet['spreadsheetId'],
                'spreadsheet_url': spreadsheet['spreadsheetUrl'],
                'title': spreadsheet['properties']['title']
            }

        except HttpError as error:
            return {'success': False, 'error': f'Failed to create spreadsheet: {error}'}

    def get_values(
        self,
        spreadsheet_id: str,
        range_name: str
    ) -> Dict[str, Any]:
        """
        Read values from a spreadsheet range

        Args:
            spreadsheet_id: The spreadsheet ID
            range_name: A1 notation range (e.g., 'Sheet1!A1:D10')

        Returns:
            Values from the specified range
        """
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()

            return {
                'success': True,
                'range': result.get('range', ''),
                'values': result.get('values', [])
            }

        except HttpError as error:
            return {'success': False, 'error': f'Failed to get values: {error}'}

    def update_values(
        self,
        spreadsheet_id: str,
        range_name: str,
        values: List[List[Any]]
    ) -> Dict[str, Any]:
        """
        Update values in a spreadsheet range

        Args:
            spreadsheet_id: The spreadsheet ID
            range_name: A1 notation range
            values: 2D array of values to write

        Returns:
            Update operation result
        """
        try:
            body = {'values': values}

            result = self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()

            return {
                'success': True,
                'updated_cells': result.get('updatedCells', 0),
                'updated_range': result.get('updatedRange', '')
            }

        except HttpError as error:
            return {'success': False, 'error': f'Failed to update values: {error}'}

    def append_values(
        self,
        spreadsheet_id: str,
        range_name: str,
        values: List[List[Any]]
    ) -> Dict[str, Any]:
        """
        Append values to a spreadsheet

        Args:
            spreadsheet_id: The spreadsheet ID
            range_name: A1 notation range
            values: 2D array of values to append

        Returns:
            Append operation result
        """
        try:
            body = {'values': values}

            result = self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()

            return {
                'success': True,
                'updated_cells': result.get('updates', {}).get('updatedCells', 0),
                'updated_range': result.get('updates', {}).get('updatedRange', '')
            }

        except HttpError as error:
            return {'success': False, 'error': f'Failed to append values: {error}'}

    def clear_values(
        self,
        spreadsheet_id: str,
        range_name: str
    ) -> Dict[str, Any]:
        """
        Clear values from a spreadsheet range

        Args:
            spreadsheet_id: The spreadsheet ID
            range_name: A1 notation range

        Returns:
            Clear operation result
        """
        try:
            result = self.service.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                body={}
            ).execute()

            return {
                'success': True,
                'cleared_range': result.get('clearedRange', '')
            }

        except HttpError as error:
            return {'success': False, 'error': f'Failed to clear values: {error}'}

    def add_sheet(
        self,
        spreadsheet_id: str,
        sheet_name: str
    ) -> Dict[str, Any]:
        """
        Add a new sheet to a spreadsheet

        Args:
            spreadsheet_id: The spreadsheet ID
            sheet_name: Name for the new sheet

        Returns:
            Operation result
        """
        try:
            body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': sheet_name
                        }
                    }
                }]
            }

            result = self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()

            sheet_id = result['replies'][0]['addSheet']['properties']['sheetId']

            return {
                'success': True,
                'sheet_id': sheet_id,
                'sheet_name': sheet_name
            }

        except HttpError as error:
            return {'success': False, 'error': f'Failed to add sheet: {error}'}

    def format_cells(
        self,
        spreadsheet_id: str,
        sheet_id: int,
        start_row: int,
        start_col: int,
        end_row: int,
        end_col: int,
        bold: Optional[bool] = None,
        background_color: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Format cells in a spreadsheet

        Args:
            spreadsheet_id: The spreadsheet ID
            sheet_id: The sheet ID (not name)
            start_row: Starting row (0-indexed)
            start_col: Starting column (0-indexed)
            end_row: Ending row (0-indexed)
            end_col: Ending column (0-indexed)
            bold: Make text bold
            background_color: RGB color dict (e.g., {'red': 1.0, 'green': 0.0, 'blue': 0.0})

        Returns:
            Format operation result
        """
        try:
            cell_format = {}

            if bold is not None:
                cell_format['textFormat'] = {'bold': bold}

            if background_color:
                cell_format['backgroundColor'] = background_color

            body = {
                'requests': [{
                    'repeatCell': {
                        'range': {
                            'sheetId': sheet_id,
                            'startRowIndex': start_row,
                            'endRowIndex': end_row,
                            'startColumnIndex': start_col,
                            'endColumnIndex': end_col
                        },
                        'cell': {
                            'userEnteredFormat': cell_format
                        },
                        'fields': 'userEnteredFormat(' + ','.join(cell_format.keys()) + ')'
                    }
                }]
            }

            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()

            return {'success': True, 'message': 'Cells formatted successfully'}

        except HttpError as error:
            return {'success': False, 'error': f'Failed to format cells: {error}'}

    def get_spreadsheet_info(self, spreadsheet_id: str) -> Dict[str, Any]:
        """
        Get spreadsheet metadata

        Args:
            spreadsheet_id: The spreadsheet ID

        Returns:
            Spreadsheet information
        """
        try:
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()

            sheets = [{
                'title': sheet['properties']['title'],
                'sheetId': sheet['properties']['sheetId'],
                'index': sheet['properties']['index']
            } for sheet in spreadsheet.get('sheets', [])]

            return {
                'success': True,
                'title': spreadsheet['properties']['title'],
                'spreadsheet_id': spreadsheet['spreadsheetId'],
                'spreadsheet_url': spreadsheet['spreadsheetUrl'],
                'sheets': sheets
            }

        except HttpError as error:
            return {'success': False, 'error': f'Failed to get spreadsheet info: {error}'}
