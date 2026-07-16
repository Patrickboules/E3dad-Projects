"""
Main Poll Application - Modular Orchestrator
Handles the flow between different poll steps.
"""

import streamlit as st
from .database import db_manager
from .utils import SessionManager, CacheManager
from .components import PhoneStep, TopicStep, UserInfoStep, ResultsView


class PollApp:
    """
    Main poll application orchestrator.
    Manages the flow between different steps.
    """

    # Step identifiers
    STEP_PHONE = "phone"
    STEP_TOPIC = "topic"
    STEP_USER_INFO = "user_info"
    STEP_RESULTS = "results"

    def __init__(self):
        """Initialize the poll application."""
        self._initialize_components()
        self._initialize_session()

    def _initialize_components(self) -> None:
        """Initialize all step components."""
        self.phone_step = PhoneStep()
        self.topic_step = TopicStep()
        self.user_info_step = UserInfoStep()
        self.results_view = ResultsView()

    def _initialize_session(self) -> None:
        """Initialize session state."""
        SessionManager.initialize()

    def run(self) -> None:
        """Run the poll application."""
        try:
            self._render_header()
            self._run_step_flow()
            self._render_footer()
        except Exception as e:
            st.error(f"حدث خطأ غير متوقع: {str(e)}")
            if st.button("إعادة المحاولة"):
                SessionManager.reset()
                st.rerun()

    def _render_header(self) -> None:
        """Render application header."""
        st.title("📊 مشاريع اعداد 2026")
        st.markdown("---")

    def _render_footer(self) -> None:
        """Render application footer."""
        st.markdown("---")
        st.caption("© 2026 E3dad Projects - جميع الحقوق محفوظة")

    def _run_step_flow(self) -> None:
        """Execute the step-by-step flow.

        Flow: Phone verification → User info → Topic selection → Results.
        """
        # If already submitted, show results
        if SessionManager.is_submitted():
            if self.results_view.render():
                st.rerun()
            return

        # Step 1: Phone Verification
        if not SessionManager.is_phone_verified():
            if self.phone_step.render():
                st.rerun()
            return

        # Step 2: User Info (name is required before topic selection)
        # Show user info step if name is not set OR if we just loaded an existing user (to allow review/edit)
        if not SessionManager.get('name', '') or SessionManager.get('just_loaded_existing_user', False):
            if self.user_info_step.render():
                # Reset the flag after successful user info submission
                SessionManager.set('just_loaded_existing_user', False)
                st.rerun()
            return

        # Step 3: Topic Selection
        if self.topic_step.render():
            st.rerun()


def run_poll():
    """Entry point for the poll application."""
    app = PollApp()
    app.run()


# Convenience function for simple imports
def create_poll_app():
    """Factory function to create and return the poll app."""
    return PollApp()