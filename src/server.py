#!/usr/bin/env python3
"""
Google Workspace MCP Server
Comprehensive Model Context Protocol server for Google Workspace APIs

Supports: Gmail, Google Chat, Google Sheets, Google Drive, Google Forms,
          Google Calendar, Google Docs
"""

import sys
import json
import logging
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent

from auth import GoogleAuthenticator
from gmail import GmailTools
from chat import ChatTools
from sheets import SheetsTools
from drive import DriveTools
from forms import FormsTools
from calendar import CalendarTools
from docs import DocsTools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
app = Server("google-workspace-mcp")

# Global service instances
auth = None
gmail = None
chat = None
sheets = None
drive = None
forms = None
calendar = None
docs = None


def initialize_services():
    """Initialize all Google Workspace services"""
    global auth, gmail, chat, sheets, drive, forms, calendar, docs

    try:
        # Authenticate
        auth = GoogleAuthenticator()
        credentials = auth.get_credentials()

        if not credentials:
            logger.error("Failed to obtain credentials")
            return False

        # Initialize all services
        gmail = GmailTools(credentials)
        chat = ChatTools(credentials)
        sheets = SheetsTools(credentials)
        drive = DriveTools(credentials)
        forms = FormsTools(credentials)
        calendar = CalendarTools(credentials)
        docs = DocsTools(credentials)

        logger.info("All Google Workspace services initialized successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        return False


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools"""
    return [
        # Gmail Tools
        Tool(
            name="gmail_list_messages",
            description="List Gmail messages with optional filters",
            inputSchema={
                "type": "object",
                "properties": {
                    "max_results": {"type": "number", "description": "Maximum results (default: 10)"},
                    "query": {"type": "string", "description": "Gmail search query (e.g., 'from:example@gmail.com')"},
                    "label_ids": {"type": "array", "items": {"type": "string"}, "description": "Filter by labels"}
                }
            }
        ),
        Tool(
            name="gmail_get_message",
            description="Get a specific Gmail message by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {"type": "string", "description": "Message ID"}
                },
                "required": ["message_id"]
            }
        ),
        Tool(
            name="gmail_send_message",
            description="Send an email",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body"},
                    "cc": {"type": "string", "description": "CC recipients"},
                    "bcc": {"type": "string", "description": "BCC recipients"}
                },
                "required": ["to", "subject", "body"]
            }
        ),
        Tool(
            name="gmail_search_messages",
            description="Search Gmail messages",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "max_results": {"type": "number", "description": "Maximum results"}
                },
                "required": ["query"]
            }
        ),

        # Google Chat Tools
        Tool(
            name="chat_list_spaces",
            description="List all Chat spaces",
            inputSchema={
                "type": "object",
                "properties": {
                    "max_results": {"type": "number", "description": "Maximum results"}
                }
            }
        ),
        Tool(
            name="chat_send_message",
            description="Send a message to a Chat space",
            inputSchema={
                "type": "object",
                "properties": {
                    "space": {"type": "string", "description": "Space name (e.g., 'spaces/SPACE_ID')"},
                    "text": {"type": "string", "description": "Message text"},
                    "thread_key": {"type": "string", "description": "Thread key for threading"}
                },
                "required": ["space", "text"]
            }
        ),
        Tool(
            name="chat_list_messages",
            description="List messages in a Chat space",
            inputSchema={
                "type": "object",
                "properties": {
                    "space": {"type": "string", "description": "Space name"},
                    "max_results": {"type": "number", "description": "Maximum results"}
                },
                "required": ["space"]
            }
        ),

        # Google Sheets Tools
        Tool(
            name="sheets_create_spreadsheet",
            description="Create a new spreadsheet",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Spreadsheet title"},
                    "sheet_names": {"type": "array", "items": {"type": "string"}, "description": "Sheet names"}
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="sheets_get_values",
            description="Read values from a spreadsheet",
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {"type": "string", "description": "Spreadsheet ID"},
                    "range_name": {"type": "string", "description": "A1 notation range"}
                },
                "required": ["spreadsheet_id", "range_name"]
            }
        ),
        Tool(
            name="sheets_update_values",
            description="Update values in a spreadsheet",
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {"type": "string", "description": "Spreadsheet ID"},
                    "range_name": {"type": "string", "description": "A1 notation range"},
                    "values": {"type": "array", "description": "2D array of values"}
                },
                "required": ["spreadsheet_id", "range_name", "values"]
            }
        ),
        Tool(
            name="sheets_append_values",
            description="Append values to a spreadsheet",
            inputSchema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {"type": "string", "description": "Spreadsheet ID"},
                    "range_name": {"type": "string", "description": "A1 notation range"},
                    "values": {"type": "array", "description": "2D array of values"}
                },
                "required": ["spreadsheet_id", "range_name", "values"]
            }
        ),

        # Google Drive Tools
        Tool(
            name="drive_list_files",
            description="List files in Google Drive",
            inputSchema={
                "type": "object",
                "properties": {
                    "max_results": {"type": "number", "description": "Maximum results"},
                    "query": {"type": "string", "description": "Drive query string"}
                }
            }
        ),
        Tool(
            name="drive_create_folder",
            description="Create a new folder",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder_name": {"type": "string", "description": "Folder name"},
                    "parent_folder_id": {"type": "string", "description": "Parent folder ID"}
                },
                "required": ["folder_name"]
            }
        ),
        Tool(
            name="drive_delete_file",
            description="Delete a file or folder",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "File/folder ID"}
                },
                "required": ["file_id"]
            }
        ),
        Tool(
            name="drive_share_file",
            description="Share a file with a user",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "File ID"},
                    "email": {"type": "string", "description": "Email address"},
                    "role": {"type": "string", "description": "Permission role (reader/writer/commenter)"}
                },
                "required": ["file_id", "email"]
            }
        ),

        # Google Forms Tools
        Tool(
            name="forms_create_form",
            description="Create a new form",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Form title"},
                    "description": {"type": "string", "description": "Form description"}
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="forms_add_question",
            description="Add a question to a form",
            inputSchema={
                "type": "object",
                "properties": {
                    "form_id": {"type": "string", "description": "Form ID"},
                    "question_title": {"type": "string", "description": "Question text"},
                    "question_type": {"type": "string", "description": "Question type"},
                    "required": {"type": "boolean", "description": "Is required"},
                    "choices": {"type": "array", "items": {"type": "string"}, "description": "Choice options"}
                },
                "required": ["form_id", "question_title"]
            }
        ),
        Tool(
            name="forms_get_responses",
            description="Get all form responses",
            inputSchema={
                "type": "object",
                "properties": {
                    "form_id": {"type": "string", "description": "Form ID"}
                },
                "required": ["form_id"]
            }
        ),

        # Google Calendar Tools
        Tool(
            name="calendar_list_events",
            description="List calendar events",
            inputSchema={
                "type": "object",
                "properties": {
                    "max_results": {"type": "number", "description": "Maximum results"},
                    "time_min": {"type": "string", "description": "Start time (RFC3339)"},
                    "time_max": {"type": "string", "description": "End time (RFC3339)"}
                }
            }
        ),
        Tool(
            name="calendar_create_event",
            description="Create a calendar event",
            inputSchema={
                "type": "object",
                "properties": {
                    "summary": {"type": "string", "description": "Event title"},
                    "start_time": {"type": "string", "description": "Start time (RFC3339)"},
                    "end_time": {"type": "string", "description": "End time (RFC3339)"},
                    "description": {"type": "string", "description": "Event description"},
                    "location": {"type": "string", "description": "Event location"},
                    "attendees": {"type": "array", "items": {"type": "string"}, "description": "Attendee emails"}
                },
                "required": ["summary", "start_time", "end_time"]
            }
        ),
        Tool(
            name="calendar_delete_event",
            description="Delete a calendar event",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_id": {"type": "string", "description": "Event ID"}
                },
                "required": ["event_id"]
            }
        ),

        # Google Docs Tools
        Tool(
            name="docs_create_document",
            description="Create a new Google Doc",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Document title"}
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="docs_get_document",
            description="Get document content",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "Document ID"}
                },
                "required": ["document_id"]
            }
        ),
        Tool(
            name="docs_insert_text",
            description="Insert text into a document",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "Document ID"},
                    "text": {"type": "string", "description": "Text to insert"},
                    "index": {"type": "number", "description": "Position to insert"}
                },
                "required": ["document_id", "text"]
            }
        ),
        Tool(
            name="docs_append_text",
            description="Append text to a document",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "Document ID"},
                    "text": {"type": "string", "description": "Text to append"}
                },
                "required": ["document_id", "text"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    try:
        result = None

        # Gmail tools
        if name == "gmail_list_messages":
            result = gmail.list_messages(**arguments)
        elif name == "gmail_get_message":
            result = gmail.get_message(**arguments)
        elif name == "gmail_send_message":
            result = gmail.send_message(**arguments)
        elif name == "gmail_search_messages":
            result = gmail.search_messages(**arguments)

        # Chat tools
        elif name == "chat_list_spaces":
            result = chat.list_spaces(**arguments)
        elif name == "chat_send_message":
            result = chat.send_message(**arguments)
        elif name == "chat_list_messages":
            result = chat.list_messages(**arguments)

        # Sheets tools
        elif name == "sheets_create_spreadsheet":
            result = sheets.create_spreadsheet(**arguments)
        elif name == "sheets_get_values":
            result = sheets.get_values(**arguments)
        elif name == "sheets_update_values":
            result = sheets.update_values(**arguments)
        elif name == "sheets_append_values":
            result = sheets.append_values(**arguments)

        # Drive tools
        elif name == "drive_list_files":
            result = drive.list_files(**arguments)
        elif name == "drive_create_folder":
            result = drive.create_folder(**arguments)
        elif name == "drive_delete_file":
            result = drive.delete_file(**arguments)
        elif name == "drive_share_file":
            result = drive.share_file(**arguments)

        # Forms tools
        elif name == "forms_create_form":
            result = forms.create_form(**arguments)
        elif name == "forms_add_question":
            result = forms.add_question(**arguments)
        elif name == "forms_get_responses":
            result = forms.get_responses(**arguments)

        # Calendar tools
        elif name == "calendar_list_events":
            result = calendar.list_events(**arguments)
        elif name == "calendar_create_event":
            result = calendar.create_event(**arguments)
        elif name == "calendar_delete_event":
            result = calendar.delete_event(**arguments)

        # Docs tools
        elif name == "docs_create_document":
            result = docs.create_document(**arguments)
        elif name == "docs_get_document":
            result = docs.get_document(**arguments)
        elif name == "docs_insert_text":
            result = docs.insert_text(**arguments)
        elif name == "docs_append_text":
            result = docs.append_text(**arguments)

        else:
            result = {"error": f"Unknown tool: {name}"}

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        logger.error(f"Tool call error: {e}")
        return [TextContent(type="text", text=json.dumps({"error": str(e)}, indent=2))]


async def main():
    """Main entry point"""
    # Initialize services
    if not initialize_services():
        logger.error("Failed to initialize services. Exiting.")
        sys.exit(1)

    # Run the server
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
