import json
import os
import re
from datetime import datetime

def sanitize_filename(filename):
    """
    Sanitizes a string to be used as a valid filename.
    """
    # Remove invalid characters
    sanitized = re.sub(r'[\\/*?:"<>|]', "", filename)
    # Replace spaces with underscores (optional, you can keep spaces)
    sanitized = sanitized.replace(' ', '_')
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')
    # Truncate to a reasonable length
    return sanitized[:100] if sanitized else 'Untitled'

def extract_conversation_title(conversation):
    """
    Attempts to extract a title from the conversation in various ways.
    """
    # Try common title fields
    title_fields = ['name', 'title', 'conversation_title', 'subject']
    for field in title_fields:
        if field in conversation and conversation[field]:
            return conversation[field]
    
    # Try to extract from first message if no title
    messages = extract_messages(conversation)
    if messages:
        first_message = messages[0].get('text', messages[0].get('content', ''))[:50]
        return f"Conversation_{first_message}" if first_message else "Untitled_Conversation"
    
    return "Untitled_Conversation"

def extract_messages(conversation):
    """
    Extracts messages from various possible structures.
    """
    # Try different possible message field names
    message_fields = ['chat_messages', 'messages', 'conversation', 'history']
    for field in message_fields:
        if field in conversation and isinstance(conversation[field], list):
            return conversation[field]
    
    # If the conversation itself is a list, it might be the messages
    if isinstance(conversation, list):
        return conversation
    
    return []

def format_message(message):
    """
    Formats a single message for markdown output.
    """
    # Extract sender (try different field names)
    sender_fields = ['sender', 'role', 'author', 'from']
    sender = 'Unknown'
    for field in sender_fields:
        if field in message:
            sender = str(message[field]).capitalize()
            break
    
    # Extract text content (try different field names)
    text_fields = ['text', 'content', 'message', 'body']
    text = ''
    for field in text_fields:
        if field in message:
            text = message[field]
            # Handle case where content might be nested
            if isinstance(text, dict) and 'text' in text:
                text = text['text']
            elif isinstance(text, list):
                # Handle case where content is a list of parts
                text_parts = []
                for part in text:
                    if isinstance(part, dict) and 'text' in part:
                        text_parts.append(part['text'])
                    elif isinstance(part, str):
                        text_parts.append(part)
                text = '\n'.join(text_parts)
            break
    
    # Extract timestamp if available
    timestamp_fields = ['timestamp', 'created_at', 'time', 'date']
    timestamp = None
    for field in timestamp_fields:
        if field in message:
            timestamp = message[field]
            break
    
    # Format the message
    formatted = f"**{sender}:**"
    if timestamp:
        try:
            # Try to parse and format timestamp
            if isinstance(timestamp, (int, float)):
                dt = datetime.fromtimestamp(timestamp)
                formatted += f" *({dt.strftime('%Y-%m-%d %H:%M:%S')})*"
            else:
                formatted += f" *({timestamp})*"
        except:
            pass
    
    formatted += f"\n{text}\n"
    return formatted

def convert_conversations_to_md(json_file_path, output_dir='markdown_transcripts'):
    """
    Reads a JSON file of conversations and converts each conversation
    into a separate Markdown file.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{json_file_path}' was not found.")
        return
    except json.JSONDecodeError as e:
        print(f"Error: The file '{json_file_path}' is not a valid JSON file.")
        print(f"JSON Error: {e}")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    # Handle different possible structures
    conversations = []
    if isinstance(data, list):
        conversations = data
    elif isinstance(data, dict):
        # Check if it's a wrapper object containing conversations
        for key in ['conversations', 'chats', 'data', 'items']:
            if key in data and isinstance(data[key], list):
                conversations = data[key]
                break
        # If still no conversations found, treat the dict as a single conversation
        if not conversations:
            conversations = [data]
    
    if not conversations:
        print("No conversations found in the JSON file.")
        return
    
    print(f"Found {len(conversations)} conversations to convert.")
    
    # Process each conversation
    for i, conversation in enumerate(conversations):
        # Generate filename
        title = extract_conversation_title(conversation)
        if title == "Untitled_Conversation" and len(conversations) > 1:
            title = f"Conversation_{i+1}"
        
        sanitized_title = sanitize_filename(title)
        md_filename = os.path.join(output_dir, f"{sanitized_title}.md")
        
        # Handle duplicate filenames
        counter = 1
        original_filename = md_filename
        while os.path.exists(md_filename):
            base, ext = os.path.splitext(original_filename)
            md_filename = f"{base}_{counter}{ext}"
            counter += 1
        
        try:
            with open(md_filename, 'w', encoding='utf-8') as md_file:
                # Write header
                md_file.write(f"# {title}\n\n")
                
                # Write metadata if available
                if 'created_at' in conversation or 'updated_at' in conversation:
                    md_file.write("## Metadata\n")
                    if 'created_at' in conversation:
                        md_file.write(f"- Created: {conversation['created_at']}\n")
                    if 'updated_at' in conversation:
                        md_file.write(f"- Updated: {conversation['updated_at']}\n")
                    md_file.write("\n---\n\n")
                
                # Extract and write messages
                messages = extract_messages(conversation)
                if messages:
                    for message in messages:
                        if isinstance(message, dict):
                            formatted_message = format_message(message)
                            md_file.write(formatted_message + "\n")
                else:
                    md_file.write("*No messages found in this conversation.*\n")
            
            print(f"Successfully created: {md_filename}")
        
        except Exception as e:
            print(f"Error processing conversation {i+1}: {e}")
            continue
    
    print(f"\nConversion complete! Check the '{output_dir}' directory for your markdown files.")

def analyze_json_structure(json_file_path):
    """
    Analyzes and prints the structure of the JSON file to help understand the format.
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("=== JSON Structure Analysis ===")
        print(f"Root type: {type(data).__name__}")
        
        if isinstance(data, list):
            print(f"Number of items: {len(data)}")
            if data:
                print("\nFirst item structure:")
                print_structure(data[0], indent=2)
        elif isinstance(data, dict):
            print(f"Root keys: {list(data.keys())}")
            print("\nStructure:")
            print_structure(data, indent=2)
        
    except Exception as e:
        print(f"Error analyzing file: {e}")

def print_structure(obj, indent=0, max_depth=3):
    """
    Recursively prints the structure of an object.
    """
    if indent > max_depth * 2:
        return
    
    prefix = " " * indent
    
    if isinstance(obj, dict):
        for key, value in list(obj.items())[:5]:  # Limit to first 5 keys
            if isinstance(value, (dict, list)):
                print(f"{prefix}{key}: {type(value).__name__}")
                print_structure(value, indent + 2)
            else:
                print(f"{prefix}{key}: {type(value).__name__}")
    elif isinstance(obj, list) and obj:
        print(f"{prefix}[0]: {type(obj[0]).__name__}")
        if isinstance(obj[0], (dict, list)):
            print_structure(obj[0], indent + 2)

if __name__ == '__main__':
    json_file = 'conversations.json'  # Change this to your actual filename
    
    # First, analyze the structure
    print("Analyzing JSON structure...\n")
    analyze_json_structure(json_file)
    
    # Then convert
    print("\n\nStarting conversion...\n")
    convert_conversations_to_md(json_file)
