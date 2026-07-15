"""
Phone verification step component — the gate to the rest of the flow.

Phone verification is mandatory. On verify:
  - New phone → advance to the user-info step (blank form).
  - Existing phone (the users schema requires a topic_id, so an existing user
    always holds a topic) → a saved-data card is shown with a
    "المتابعة بالبيانات المسجلة" button; on resume, the name, teammate and
    chosen topic are carried into session, then the flow advances.

The session is aligned with the MongoDB `users` schema
(required: name, phone_number, teammate_name, topic_id):
  - name           (was first_name)  — required
  - teammate_name  (was last_name)   — optional
  - selected_option                  — topic_name of the current selection
"""

import streamlit as st
from ..utils.validators import PhoneValidator
from ..utils.session import SessionManager
from ..database import db_manager


class PhoneStep:
    """Handles the phone number verification step."""

    def __init__(self):
        """Initialize with database manager."""
        self.db = db_manager

    def render(self) -> bool:
        """Render the phone verification step.

        Returns:
            True when phone is verified and the run should proceed.
        """
        st.markdown("""
        <div class="phone-verification-container">
            <div class="phone-header">
                <h2>التحقق من رقم هاتفك انه متسجل لدينا</h2>
            </div>
            <div class="phone-instructions">
                <p>الرجاء إدخال رقم هاتف مصري
                   (يبدأ بـ 01 ويحتوي على 11 رقمًا)</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        phone = st.text_input(
            "",
            key="phone_input",
            placeholder="أدخل رقم هاتفك (مثال: 01234567890)",
            max_chars=11,
            label_visibility="collapsed",
        )

        if st.button(
            "Enter",
            use_container_width=True,
            type="primary",
            key="verify_phone",
        ):
            return self._handle_verification(phone)

        return False

    def _handle_verification(self, phone: str) -> bool:
        """Validate the phone, look the user up, and advance accordingly."""
        error = PhoneValidator.get_validation_error(phone)
        if error:
            st.error(error)
            return False

        cleaned = PhoneValidator.validate_egyptian_phone(phone)
        if not cleaned:
            st.error(
                "الرجاء إدخال رقم هاتف مصري صحيح "
                "(يبدأ بـ 01 ويحتوي على 11 رقمًا)"
            )
            return False

        existing_user = self.db.get_user_by_phone(cleaned)

        if existing_user:
            # The schema requires topic_id, so an existing user always has a
            # topic. Rehydrate the topic name from the stored topic_id.
            topic_name = ""
            topic_id = existing_user.get("topic_id")
            if topic_id:
                topic_doc = self.db.get_topic_by_id(topic_id)
                if topic_doc:
                    topic_name = topic_doc.get("topic_name", "")

            # Show existing user data for confirmation
            self._show_existing_data_card(existing_user, topic_name)

            # Mark that we just loaded an existing user so the user info
            # step will be shown for review/edit
            SessionManager.set('just_loaded_existing_user', True)

            # Set session data with existing user information
            SessionManager.update({
                "phone_verified": True,
                "phone_number": cleaned,
                "name": existing_user.get("name") or "",
                "teammate_name": existing_user.get("teammate_name") or "",
                "selected_option": topic_name or None,
            })
            return True

                # New user: advance to the user-info step on a blank form.
        SessionManager.update({
            "phone_verified": True,
            "phone_number": cleaned,
            "name": "",
            "teammate_name": "",
            "selected_option": None,
        })
        return True

    def _show_existing_data_card(self, user: dict, ticket_name: str) -> None:
        """Render the saved-data card for a returning user."""
        st.markdown(
            """
            <div class="existing-data-card">
                <h4 style="margin-top: 0; color: #2c3e50;">
                    البيانات المسجلة سابقاً
                </h4>
                <div class="data-item">
                    <div class="data-label">الاسم:</div>
                    <div class="data-value">{}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">اسم الزميل:</div>
                    <div class="data-value">{}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">الموضوع المختار:</div>
                    <div class="data-value">{}</div>
                </div>
            </div>
            """.format(
                user.get("name") or "",
                user.get("teammate_name") or "",
                ticket_name or "",
            ),
            unsafe_allow_html=True,
        )