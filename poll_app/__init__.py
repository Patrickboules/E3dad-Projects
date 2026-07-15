"""
Poll Application Package
A modular Streamlit poll application.
"""

from .poll import run_poll, PollApp, create_poll_app

__version__ = "1.0.0"
__all__ = ['run_poll', 'PollApp', 'create_poll_app']