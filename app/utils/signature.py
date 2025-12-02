"""
Utility functions for signature field handling.
Converts base64 signature data to PNG files for storage.
"""
import base64
import re
from pathlib import Path
from typing import Tuple
import io
from PIL import Image


class SignatureValidationError(Exception):
    """Raised when signature validation fails"""
    pass


def validate_base64(data: str) -> bool:
    """
    Check if string is valid base64.

    Args:
        data: String to validate

    Returns:
        True if valid base64, False otherwise
    """
    try:
        # Remove data URI prefix if present
        if ',' in data:
            data = data.split(',')[1]

        # Try to decode
        base64.b64decode(data, validate=True)
        return True
    except Exception:
        return False


def remove_data_uri_prefix(base64_string: str) -> str:
    """
    Remove data URI prefix from base64 string if present.

    Examples:
        data:image/png;base64,iVBORw0... -> iVBORw0...
        iVBORw0... -> iVBORw0...

    Args:
        base64_string: Base64 string with or without data URI

    Returns:
        Clean base64 string
    """
    if ',' in base64_string:
        return base64_string.split(',', 1)[1]
    return base64_string


def base64_to_png(base64_string: str) -> bytes:
    """
    Convert base64 string to PNG bytes.

    Args:
        base64_string: Base64 encoded image (with or without data URI prefix)

    Returns:
        PNG image as bytes

    Raises:
        SignatureValidationError: If conversion fails or invalid format
    """
    try:
        # Remove data URI prefix if present
        clean_base64 = remove_data_uri_prefix(base64_string)

        # Decode base64
        image_bytes = base64.b64decode(clean_base64)

        # Verify it's a valid image using PIL
        try:
            img = Image.open(io.BytesIO(image_bytes))

            # Convert to PNG if it isn't already
            if img.format != 'PNG':
                png_buffer = io.BytesIO()
                img.save(png_buffer, format='PNG')
                image_bytes = png_buffer.getvalue()

            return image_bytes

        except Exception as e:
            raise SignatureValidationError(f"Invalid image data: {str(e)}")

    except base64.binascii.Error:
        raise SignatureValidationError("Invalid base64 encoding")
    except Exception as e:
        raise SignatureValidationError(f"Failed to process signature: {str(e)}")


def validate_signature_size(base64_string: str, max_size_bytes: int = 5242880) -> Tuple[bool, int]:
    """
    Validate signature size is within limits.

    Args:
        base64_string: Base64 encoded signature
        max_size_bytes: Maximum allowed size in bytes (default 5MB)

    Returns:
        Tuple of (is_valid, actual_size_bytes)

    Raises:
        SignatureValidationError: If size exceeds limit
    """
    try:
        # Remove data URI prefix
        clean_base64 = remove_data_uri_prefix(base64_string)

        # Calculate decoded size
        # Base64 encodes 3 bytes into 4 characters
        # So decoded size ≈ (encoded_length * 3) / 4
        padding = clean_base64.count('=')
        size_bytes = ((len(clean_base64) * 3) // 4) - padding

        if size_bytes > max_size_bytes:
            max_mb = max_size_bytes / (1024 * 1024)
            actual_mb = size_bytes / (1024 * 1024)
            raise SignatureValidationError(
                f"Signature size ({actual_mb:.2f}MB) exceeds maximum allowed size ({max_mb:.2f}MB)"
            )

        return True, size_bytes

    except SignatureValidationError:
        raise
    except Exception as e:
        raise SignatureValidationError(f"Failed to validate signature size: {str(e)}")


def save_signature_file(png_bytes: bytes, filename: str, upload_dir: str) -> str:
    """
    Save PNG bytes to file.

    Args:
        png_bytes: PNG image as bytes
        filename: Name of file to save (should include .png extension)
        upload_dir: Directory to save file in

    Returns:
        Full file path where signature was saved

    Raises:
        SignatureValidationError: If save fails
    """
    try:
        # Ensure upload directory exists
        upload_path = Path(upload_dir)
        upload_path.mkdir(parents=True, exist_ok=True)

        # Full file path
        file_path = upload_path / filename

        # Write file
        with open(file_path, 'wb') as f:
            f.write(png_bytes)

        return str(file_path)

    except Exception as e:
        raise SignatureValidationError(f"Failed to save signature file: {str(e)}")


def generate_signature_filename(user_id: int, field_id: int, tenant_id: int) -> str:
    """
    Generate unique filename for signature.

    Format: signature_{tenant_id}_{user_id}_{field_id}_{timestamp}.png

    Args:
        user_id: User ID
        field_id: Field ID
        tenant_id: Tenant ID

    Returns:
        Generated filename
    """
    import time
    timestamp = int(time.time() * 1000)  # Milliseconds
    return f"signature_{tenant_id}_{user_id}_{field_id}_{timestamp}.png"
