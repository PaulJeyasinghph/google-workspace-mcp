"""
Google Drive Tools for MCP Server
Provides file and folder management functionality
"""

from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import io


class DriveTools:
    """Google Drive API tools for file and folder operations"""

    def __init__(self, credentials):
        """Initialize Drive service with credentials"""
        self.service = build('drive', 'v3', credentials=credentials)

    def list_files(
        self,
        max_results: int = 10,
        query: Optional[str] = None,
        order_by: str = 'modifiedTime desc'
    ) -> List[Dict[str, Any]]:
        """
        List files in Google Drive

        Args:
            max_results: Maximum number of files to return
            query: Drive query string (e.g., "mimeType='application/pdf'")
            order_by: Sort order (e.g., 'modifiedTime desc', 'name')

        Returns:
            List of files
        """
        try:
            params = {
                'pageSize': max_results,
                'fields': 'files(id, name, mimeType, createdTime, modifiedTime, size, webViewLink)',
                'orderBy': order_by
            }

            if query:
                params['q'] = query

            results = self.service.files().list(**params).execute()
            files = results.get('files', [])

            return [{
                'id': f.get('id', ''),
                'name': f.get('name', ''),
                'mimeType': f.get('mimeType', ''),
                'createdTime': f.get('createdTime', ''),
                'modifiedTime': f.get('modifiedTime', ''),
                'size': f.get('size', '0'),
                'webViewLink': f.get('webViewLink', '')
            } for f in files]

        except HttpError as error:
            return [{'error': f'Failed to list files: {error}'}]

    def get_file(self, file_id: str) -> Dict[str, Any]:
        """
        Get file metadata

        Args:
            file_id: The file ID

        Returns:
            File metadata
        """
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='id, name, mimeType, createdTime, modifiedTime, size, webViewLink, parents'
            ).execute()

            return {
                'success': True,
                'id': file.get('id', ''),
                'name': file.get('name', ''),
                'mimeType': file.get('mimeType', ''),
                'createdTime': file.get('createdTime', ''),
                'modifiedTime': file.get('modifiedTime', ''),
                'size': file.get('size', '0'),
                'webViewLink': file.get('webViewLink', ''),
                'parents': file.get('parents', [])
            }

        except HttpError as error:
            return {'success': False, 'error': f'Failed to get file: {error}'}

    def create_folder(
        self,
        folder_name: str,
        parent_folder_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new folder

        Args:
            folder_name: Name for the new folder
            parent_folder_id: Optional parent folder ID

        Returns:
            Created folder details
        """
        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }

            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]

            folder = self.service.files().create(
                body=file_metadata,
                fields='id, name, webViewLink'
            ).execute()

            return {
                'success': True,
                'folder_id': folder.get('id', ''),
                'folder_name': folder.get('name', ''),
                'webViewLink': folder.get('webViewLink', '')
            }

        except HttpError as error:
            return {'success': False, 'error': f'Failed to create folder: {error}'}

    def delete_file(self, file_id: str) -> Dict[str, Any]:
        """
        Delete a file or folder

        Args:
            file_id: The file/folder ID

        Returns:
            Operation result
        """
        try:
            self.service.files().delete(fileId=file_id).execute()

            return {'success': True, 'message': 'File deleted successfully'}

        except HttpError as error:
            return {'success': False, 'error': f'Failed to delete file: {error}'}

    def copy_file(
        self,
        file_id: str,
        new_name: Optional[str] = None,
        parent_folder_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Copy a file

        Args:
            file_id: The source file ID
            new_name: Optional new name for the copy
            parent_folder_id: Optional destination folder ID

        Returns:
            Copied file details
        """
        try:
            body = {}

            if new_name:
                body['name'] = new_name

            if parent_folder_id:
                body['parents'] = [parent_folder_id]

            copied_file = self.service.files().copy(
                fileId=file_id,
                body=body,
                fields='id, name, webViewLink'
            ).execute()

            return {
                'success': True,
                'file_id': copied_file.get('id', ''),
                'name': copied_file.get('name', ''),
                'webViewLink': copied_file.get('webViewLink', '')
            }

        except HttpError as error:
            return {'success': False, 'error': f'Failed to copy file: {error}'}

    def move_file(
        self,
        file_id: str,
        new_parent_id: str
    ) -> Dict[str, Any]:
        """
        Move a file to a different folder

        Args:
            file_id: The file ID
            new_parent_id: The destination folder ID

        Returns:
            Operation result
        """
        try:
            # Retrieve the existing parents to remove
            file = self.service.files().get(
                fileId=file_id,
                fields='parents'
            ).execute()

            previous_parents = ','.join(file.get('parents', []))

            # Move the file
            updated_file = self.service.files().update(
                fileId=file_id,
                addParents=new_parent_id,
                removeParents=previous_parents,
                fields='id, name, parents'
            ).execute()

            return {
                'success': True,
                'file_id': updated_file.get('id', ''),
                'name': updated_file.get('name', ''),
                'parents': updated_file.get('parents', [])
            }

        except HttpError as error:
            return {'success': False, 'error': f'Failed to move file: {error}'}

    def share_file(
        self,
        file_id: str,
        email: str,
        role: str = 'reader'
    ) -> Dict[str, Any]:
        """
        Share a file with a user

        Args:
            file_id: The file ID
            email: Email address to share with
            role: Permission role ('reader', 'writer', 'commenter')

        Returns:
            Operation result
        """
        try:
            permission = {
                'type': 'user',
                'role': role,
                'emailAddress': email
            }

            self.service.permissions().create(
                fileId=file_id,
                body=permission,
                fields='id'
            ).execute()

            return {
                'success': True,
                'message': f'File shared with {email} as {role}'
            }

        except HttpError as error:
            return {'success': False, 'error': f'Failed to share file: {error}'}

    def search_files(
        self,
        query: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for files by name or content

        Args:
            query: Search query (file name)
            max_results: Maximum number of results

        Returns:
            List of matching files
        """
        search_query = f"name contains '{query}'"
        return self.list_files(max_results=max_results, query=search_query)

    def get_folder_contents(
        self,
        folder_id: str,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List all files in a specific folder

        Args:
            folder_id: The folder ID
            max_results: Maximum number of files to return

        Returns:
            List of files in the folder
        """
        query = f"'{folder_id}' in parents and trashed=false"
        return self.list_files(max_results=max_results, query=query)
