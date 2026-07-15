"""
Validation utilities for user input.
"""

import re
from typing import Optional


class PhoneValidator:
    """Handles phone number validation logic."""

    EGYPTIAN_PHONE_PATTERN = r'^01\d{9}$'
    MIN_LENGTH = 11
    MAX_LENGTH = 11
    PREFIX = '01'

    @classmethod
    def validate_egyptian_phone(cls, phone: str) -> Optional[str]:
        """
        Validate and normalize Egyptian phone number.
        
        Args:
            phone: Raw phone number input
            
        Returns:
            Cleaned phone number if valid, None otherwise
        """
        # Remove non-digit characters
        cleaned = re.sub(r'\D', '', phone)
        
        # Validate length and prefix
        if (
            len(cleaned) == cls.MIN_LENGTH 
            and cleaned.startswith(cls.PREFIX)
        ):
            return cleaned
        
        return None

    @classmethod
    def get_validation_error(cls, phone: str) -> Optional[str]:
        """
        Get specific validation error message.
        
        Args:
            phone: Raw phone number input
            
        Returns:
            Error message if invalid, None if valid
        """
        cleaned = re.sub(r'\D', '', phone)
        
        if not cleaned:
            return "يرجى إدخال رقم الهاتف"
        
        if len(cleaned) < cls.MIN_LENGTH:
            return f"رقم الهاتف قصير، يجب أن يكون {cls.MIN_LENGTH} رقم"
        
        if len(cleaned) > cls.MAX_LENGTH:
            return f"رقم الهاتف طويل، يجب أن يكون {cls.MAX_LENGTH} رقم"
        
        if not cleaned.startswith(cls.PREFIX):
            return "رقم الهاتف يجب أن يبدأ بـ 01"
        
        return None