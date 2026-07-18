"""
Results display component — the confirmation shown after submission.

Renders a recap card (name, chosen topic, phone) over `st.balloons()`, an
optional per-topic statistics list, and a reset button that drops the user
back to the phone gate.
"""

import streamlit as st
from ..utils.session import SessionManager

class ResultsView:
    """Handles the results/thank you view."""

    def render(self) -> bool:
        """
        Render the results view.

        Returns:
            True when the user wants to start over (vote again).
        """
        st.balloons()
        st.markdown("### 🎉 شكراً لمشاركتك!")
        st.markdown("---")

        self._show_recap_card()

        if st.button(
            "🔄 تصويت جديد",
            type="primary",
            use_container_width=True,
            key="vote_again_button",
        ):
            SessionManager.reset()
            return True
        return False

    def _show_recap_card(self) -> None:
        """Display the recap card from session (mirrors what was saved)."""
        name = SessionManager.get("name", "")
        teammate_name = SessionManager.get("teammate_name", "")
        phone = SessionManager.get("phone_number", "")

        # Check for custom topic first (mutually exclusive with selected_option)
        custom_topic = SessionManager.get("custom_topic", None)
        if custom_topic:
            topic = custom_topic
        else:
            # 'selected_option' always exists in session state (defaults to None
            # per project.md's DEFAULT_FORM_STATE), so dict.get()'s default arg
            # never fires here — None must be coalesced explicitly.
            topic = SessionManager.get("selected_option", None) or "غير محدد"

        teammate_row = (
            f'<p><strong>اسم الزميل:</strong> {teammate_name}</p>'
            if teammate_name.strip()
            else "</>"
        )

        st.markdown(
            f"""
            <div class="results-card">
                <h3>تفاصيل التسجيل</h3>
                <div class="results-card-content">
                    <p><strong>الاسم:</strong> {name}</p>
                    {teammate_row}
                    <p><strong>الموضوع المختار:</strong> {topic}</p>
                    <p><strong>رقم الهاتف:</strong> {phone}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )