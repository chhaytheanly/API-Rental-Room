import base64
from typing import Optional
from fastapi import UploadFile

def file_to_base64(file: UploadFile) -> str:
    """
    Convert an uploaded file to a Base64 encoded string with data URI prefix.
    
    Args:
        file: FastAPI UploadFile object
        
    Returns:
        Base64 encoded string with data URI (e.g., "data:image/png;base64,...")
    """
    # Read file content
    file_content = file.file.read()
    
    # Encode to base64
    encoded = base64.b64encode(file_content).decode('utf-8')
    
    # Reset file pointer for potential reuse
    file.file.seek(0)
    
    # Return with data URI prefix
    return f"data:{file.content_type};base64,{encoded}"


def base64_to_bytes(base64_string: str) -> bytes:
    """
    Convert a Base64 string (with or without data URI prefix) to bytes.
    
    Args:
        base64_string: Base64 encoded string
        
    Returns:
        Decoded bytes
    """
    # Remove data URI prefix if present
    if base64_string.startswith('data:'):
        base64_string = base64_string.split(',', 1)[1]
    
    return base64.b64decode(base64_string)


def validate_image_base64(base64_string: str) -> bool:
    """
    Validate if a Base64 string is a valid image.
    
    Args:
        base64_string: Base64 encoded string
        
    Returns:
        True if valid image, False otherwise
    """
    try:
        # Check if it has data URI prefix
        if base64_string.startswith('data:image/'):
            return True
        
        # Try to decode
        base64_to_bytes(base64_string)
        return True
    except Exception:
        return False
