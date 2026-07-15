"""
State management for Streamlit.
"""

import streamlit as st
from typing import Dict, Any, Optional


class SessionManager:
    """Manages Streamlit session state for the poll application."""

    # Default form state structure (aligned with the MongoDB `users` schema,
    # which requires: name, phone_number, teammate_name, topic_id).
    DEFAULT_FORM_STATE = {
        'phone_verified': False,
        'phone_number': '',
        'name': '',              # required (was first_name)
        'teammate_name': '',     # optional (was last_name)
        'selected_option': None,  # token_name of the current selection, or None
        'submitted': False,
        'temp_counts': {},       # optimistic per-token count deltas,
        'just_loaded_existing_user': False,  # flag to indicate we just loaded an existing user
    }

    @classmethod
    def initialize(cls) -> Dict[str, Any]:
        """
        Initialize session state with default values.

        Returns:
            The form state dictionary
        """
        if 'form' not in st.session_state:
            st.session_state.form = cls.DEFAULT_FORM_STATE.copy()
        return st.session_state.form

    @classmethod
    def get(cls, key: str, default: Dict[str, Optional[str]]) -> Any:
        """Get a value from form state."""
        cls.initialize()
        return st.session_state.form.get(key, default)

    @classmethod
    def set(cls, key: str, value: Any) -> None:
        """Set a value in form state."""
        cls.initialize()
        st.session_state.form[key] = value

    @classmethod
    def update(cls, updates: Dict[str, Optional[str]]) -> None:
        """Update multiple values in form state."""
        cls.initialize()
        st.session_state.form.update(updates)

    @classmethod
    def reset(cls) -> None:
        """Reset form state to defaults."""
        st.session_state.form = cls.DEFAULT_FORM_STATE.copy()

    @classmethod
    def is_phone_verified(cls) -> bool:
        """Check if phone is verified."""
        return cls.get('phone_verified', False)

    @classmethod
    def is_submitted(cls) -> bool:
        """Check if form is submitted."""
        return cls.get('submitted', False)