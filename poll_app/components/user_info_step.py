"""
User information step component — step 2 of the flow.

Collects the participant's names BEFORE they pick a topic. The name is
required; the teammate name is optional. The user information is saved to
the database immediately after collection (before topic selection).
"""

import streamlit as st
from ..utils.session import SessionManager
from ..database import db_manager


class UserInfoStep:
    """Handles the user information collection step."""

    def render(self) -> bool:
        """
        Render the user information step.

        Returns:
            True when the (required) name is present and the run should
            proceed to the topic step.
        """
        st.markdown("### 👤 أدخل أسماء المخدومين")
        st.markdown(
            "1. إذا كنت بمفردك، يرجى ملء حقل الاسم فقط. "
            "2. إذا كان لديك زميل في الفريق، يرجى ملء اسمه أيضًا."
        )
        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                '<span class="required-field">الاسم</span>',
                unsafe_allow_html=True,
            )
            name = st.text_input(
                "الاسم",
                value=SessionManager.get("name", ""),
                key="name_input",
                label_visibility="collapsed",
            )

        with col2:
            st.markdown("اسم الزميل")
            teammate_name = st.text_input(
                "اسم الزميل",
                value=SessionManager.get("teammate_name", ""),
                key="teammate_name_input",
                label_visibility="collapsed",
                )
        st.markdown('<span class="required-field">الفئة</span>', unsafe_allow_html=True)
        # Inject custom CSS for the radio button group with larger font and better positioning
        st.markdown('''
            <style>
            .year-radio-container {
                background-color: #f0f2f6;
                padding: 20px;
                border-radius: 12px;
                margin: 15px 0;
                font-size: 22px;
                display: flex;
                justify-content: center;
                gap: 12px;
            }
            /* Style the radio button labels */
            .year-radio-container label {
                font-size: 22px !important;
                margin: 0 !important;
                padding: 8px 12px !important;
                border-radius: 8px !important;
                transition: background-color 0.2s;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .year-radio-container label:hover {
                background-color: #e0e0e0 !important;
            }
            /* Style the radio buttons themselves */
            .year-radio-container input[type="radio"] {
                width: 18px !important;
                height: 18px !important;
                cursor: pointer;
            }
            </style>
        ''', unsafe_allow_html=True)
        year_labels = {"year1": "سنة أولى", "year2": "سنة ثانية"}
        current_year = SessionManager.get("year", None)
        year_display = st.radio(
            "الفئة",
            options=list(year_labels.values()),
            index=list(year_labels.keys()).index(current_year) if current_year in year_labels else None,
            key="year_input",
            label_visibility="collapsed",
            horizontal=True,
        )
        year = next((k for k, v in year_labels.items() if v == year_display), None)
        name_ok = bool(name and name.strip())

        if not name_ok:
            st.markdown(
                '<div class="error-message">الرجاء إدخال الاسم</div>',
                unsafe_allow_html=True,
            )

        if st.button(
            "متابعة",
            type="primary",
            use_container_width=True,
            key="continue_to_topic",
            disabled=not name_ok,
        ):
            return self._handle_continue(name, teammate_name, year)

        return False

    def _handle_continue(self, name: str, teammate_name: str,year) -> bool:
        """Save the user information to session and database, then advance."""
        # Save to session
        SessionManager.update({
            "name": name.strip(),
            "teammate_name": teammate_name.strip(),
            "year": year
        })

        # Save to database
        phone_number = SessionManager.get("phone_number", "")
        if phone_number:  # Only save if we have a phone number (should be verified at this point)
            user_data = {
                "phone_number": phone_number,
                "name": name.strip(),
                "teammate_name": teammate_name.strip(),
                # topic_id will be set later when a topic is selected
            }
            if not db_manager.save_or_update_user(user_data):
                st.error("فشل حفظ البيانات. يرجى المحاولة مرة أخرى.")
                return False
        # Reset the flag indicating we just loaded an existing user
        SessionManager.set('just_loaded_existing_user', False)

        return True
