"""
Topic selection step component — step 3 of the flow.

A single page listing every topic as a card with a live (count/3) meter and a
progress bar. Selection is auto-saved to MongoDB on every change, touching BOTH
the users document (which topic this phone holds) and the topics document
(that topic's global count). One topic per user; up to three users per topic.
A topic at 3/3 is dimmed for everyone except the user currently holding it
(so they can still deselect and free the slot).
"""

import streamlit as st
from streamlit.components.v1 import html

from ..utils.session import SessionManager
from ..utils.cache import CacheManager
from ..database import db_manager
from .styles import option_click_js


MAX_LIMIT = 3  # participants per topic (per-topic cap)
REFRESH_INTERVAL = "3s"  # how often the topic list polls the DB for other users' changes


class TopicStep:
    """Handles the topic selection step."""

    def __init__(self):
        self.db = db_manager

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #
    def render(self) -> bool:
        """Render the topic selection step.

        Returns:
            True when the run should advance (to the results step).
        """
        st.markdown(
            '<h2 class="header">الرجاء اختيار موضوع واحد من المواضيع التالية:</h2>',
            unsafe_allow_html=True,
        )

        # Everything inside is a fragment: it reruns on its own timer, so
        # other users' selections/deselections show up here without a full
        # page reload and without disturbing this user's own inputs.
        self._render_topic_list()

        st.markdown("---")

        # Advance to results
        return self._render_continue()

    # ------------------------------------------------------------------ #
    # Auto-refreshing topic list
    # ------------------------------------------------------------------ #
    @st.fragment(run_every=REFRESH_INTERVAL)
    def _render_topic_list(self) -> None:
        """Render every topic card; reruns every REFRESH_INTERVAL on its own."""
        year = SessionManager.get("year", None)
        topics_data = CacheManager.get_topics_data(year)

        if not topics_data:
            st.warning("لا توجد مواضيع متاحة حالياً — تأكد من تهيئة قاعدة البيانات.")
            return

        counts = self._combined_counts(topics_data)

        for num, (name, info) in enumerate(topics_data.items(), start=1):
            self._render_topic_card(num, name, info, counts)

        # Custom topic input section
        self._render_custom_topic_input()

        # Inject the card-click → button + light-mode-pinning JavaScript
        html(option_click_js(), height=0)

    # ------------------------------------------------------------------ #
    # Counts
    # ------------------------------------------------------------------ #
    def _combined_counts(self, topics_data: dict) -> dict:
        """Merge the DB topic counts with optimistic `temp_counts` deltas."""
        counts = {
            name: info.get("count", 0)
            for name, info in topics_data.items()
        }
        temp = SessionManager.get("temp_counts", {})
        for name, delta in temp.items():
            counts[name] = counts.get(name, 0) + delta
        return counts

    def _bump_temp(self, name: str, delta: int) -> None:
        """Apply a delta to a topic's optimistic temp count."""
        temp = SessionManager.get("temp_counts", {})
        temp[name] = temp.get(name, 0) + delta
        SessionManager.set("temp_counts", temp)

    # ------------------------------------------------------------------ #
    # Custom topic handling
    # ------------------------------------------------------------------ #
    def _render_custom_topic_input(self) -> None:
        """Render the custom topic input field and selection controls."""
        # Check if we need to clear the custom topic input
        if st.session_state.get('clear_custom_topic_input_flag', False):
            st.session_state.custom_topic_input = ""
            st.session_state.clear_custom_topic_input_flag = False

        custom_topic = SessionManager.get("custom_topic", "")
        selected_option = SessionManager.get("selected_option", None)

        st.markdown("---")
        st.markdown("** أو اكتب موضوعاً خاصاً بك:**")

        input_col, button_col1, button_col2 = st.columns([4, 1, 1])

        with input_col:
            custom_input = st.text_input(
                "اكتب موضوعك الخاص هنا",
                value=custom_topic or "",
                placeholder="مثال: موضوع مخصص للحدث",
                label_visibility="collapsed",
                key="custom_topic_input"
            )

        with button_col1:
            if st.button(
                "اختر",
                key="select_custom_topic",
                disabled=not custom_input.strip(),
                type="secondary",
                use_container_width=True,
            ):
                self._select_custom_topic(custom_input.strip())

        with button_col2:
            if custom_topic:
                if st.button(
                    "إلغاء الاختيار",
                    key="clear_custom_topic",
                    type="secondary",
                    use_container_width=True,
                ):
                    self._clear_custom_topic()

        # Inject the card-click → button + light-mode-pinning JavaScript
        html(option_click_js(), height=0)

    def _select_custom_topic(self, topic_string: str) -> bool:
        """Handle selection of a custom topic."""
        # Release any predefined topic if currently selected
        current_predefined = SessionManager.get("selected_option", None)
        if current_predefined:
            self.db.update_topic_count(current_predefined, -1)
            self._bump_temp(current_predefined, -1)

        # Set custom topic in session
        SessionManager.update({
            "selected_option": None,  # Clear predefined topic selection
            "custom_topic": topic_string,
        })

        # Persist to database
        if not self._persist_user(custom_topic=topic_string):
            phone_number = SessionManager.get("phone_number", "")
            if not phone_number:
                st.error("جلسة غير صالحة. يرجى إعادة البدء.")
            else:
                st.error("فشل حفظ выборك. يرجى المحاولة مرة أخرى.")
            # Rollback: restore predefined topic if we had one
            if current_predefined:
                self.db.update_topic_count(current_predefined, +1)
                self._bump_temp(current_predefined, +1)
                SessionManager.update({
                    "selected_option": current_predefined,
                    "custom_topic": None,
                })
            return False

        # Clear temp counts for the predefined topic we released (if any)
        if current_predefined:
            temp = SessionManager.get("temp_counts", {})
            if current_predefined in temp:
                del temp[current_predefined]
            SessionManager.set("temp_counts", temp)

        # Clear widget session state for custom topic input to ensure text input updates correctly on rerun
        st.session_state.clear_custom_topic_input_flag = True

        CacheManager.clear_topics_cache()
        st.rerun()
        return True

    def _clear_custom_topic(self) -> bool:
        """Clear the currently selected custom topic."""
        st.session_state.clear_custom_topic_input_flag = True

        custom_topic = SessionManager.get("custom_topic", "")
        if not custom_topic:
            return True

        # Persist the clearance to database
        if not self._persist_user(custom_topic=""):
            # Rollback: restore the custom topic
            SessionManager.update({
                "custom_topic": custom_topic,
            })
            st.error("فشل حذف الاختيار. يرجى المحاولة مرة أخرى.")
            return False

        # Clear custom topic from session
        SessionManager.update({
            "custom_topic": None,
        })

        # Clear widget session state for custom topic input to ensure text input clears

        CacheManager.clear_topics_cache()
        st.rerun()
        return True

    # ------------------------------------------------------------------ #
    # Predefined topic cards
    # ------------------------------------------------------------------ #
    def _render_topic_card(self, num: int, name: str, info: dict, counts: dict) -> None:
        """Render a single topic card with its meter and Select/Deselect."""
        # Get topic ID for stable button keys; fallback to topic name if _id is missing
        topic_id = info.get("_id")
        if topic_id is None:
            topic_id = name
        topic_id = str(topic_id)

        count = counts.get(name, 0)
        progress = (count / MAX_LIMIT) * 100
        is_current = SessionManager.get("selected_option", None) == name
        is_full = count >= MAX_LIMIT

        # A full topic is dimmed for everyone except its current holder.
        disabled = is_full and not is_current

        container = st.container()
        container.markdown(
            f"""
            <div class="option-container {'selected' if is_current else ''}
                 {'disabled' if disabled and not is_current else ''}"
                 id="option_{num}"
                 onclick="handleClick('{topic_id}')">
                <div class="option-header">
                    <div class="option-number">{num}.</div>
                    <div class="count-display">({count}/{MAX_LIMIT})</div>
                </div>
                <div class="option-text">{name}</div>
                <div class="progress-container">
                    <div class="progress-bar {'complete' if is_full else ''}"
                         style="width:{progress}%"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = container.columns([1, 1])

        if col1.button(
            "اختر",
            key=f"select_{topic_id}",
            disabled=disabled,
        ):
            self._select_topic(name)

        if is_current:
            if col2.button("إلغاء الاختيار", key=f"deselect_{topic_id}"):
                self._deselect_topic(name)
        else:
            col2.empty()

    def _select_topic(self, name: str) -> bool:
        """Switch to a predefined topic (swapping/deselecting the previous)."""
        current = SessionManager.get("selected_option", None)

        # Release a previously-held predefined topic, if any.
        if current:
            self.db.update_topic_count(current, -1)
            self._bump_temp(current, -1)

        # Pick up the new topic.
        self.db.update_topic_count(name, +1)
        self._bump_temp(name, +1)
        SessionManager.update({
            "selected_option": name,
        })

        # Persist the user's selection
        if not self._persist_user(selected_topic=name):
            phone_number = SessionManager.get("phone_number", "")
            if not phone_number:
                st.error("جلسة غير صالحة. يرجى إعادة البدء.")
            else:
                st.error("فشل حفظ выборك. يرجى المحاولة مرة أخرى.")
            # Rollback the topic count changes and session state
            self.db.update_topic_count(name, -1)
            self._bump_temp(name, -1)
            if current:
                self.db.update_topic_count(current, +1)
                self._bump_temp(current, +1)
            SessionManager.update({
                "selected_option": current,
            })
            return False

        # Clear widget session state for custom topic input to ensure text input reflects form state
        st.session_state.clear_custom_topic_input_flag = True

        # Clear temp counts for updated topics since we'll get fresh data from DB on rerun
        temp = SessionManager.get("temp_counts", {})
        if current and current in temp:
            del temp[current]
        if name in temp:
            del temp[name]
        SessionManager.set("temp_counts", temp)

        CacheManager.clear_topics_cache()
        st.rerun()
        return True

    def _deselect_topic(self, name: str) -> bool:
        """Release the currently-held predefined topic."""
        self.db.update_topic_count(name, -1)
        self._bump_temp(name, -1)
        SessionManager.update({
            "selected_option": None,
        })

        # Persist the user's deselection (setting topic to none)
        if not self._persist_user():
            # Rollback: restore the topic count and session state
            self.db.update_topic_count(name, +1)
            self._bump_temp(name, +1)
            SessionManager.update({
                "selected_option": name,
            })
            st.error("Failed to save your deselection. Please try again.")
            return False

        # Clear widget session state for custom topic input to ensure text input reflects form state
        st.session_state.clear_custom_topic_input_flag = True

        # Clear temp count for updated topic since we'll get fresh data from DB on rerun
        temp = SessionManager.get("temp_counts", {})
        if name in temp:
            del temp[name]
        SessionManager.set("temp_counts", temp)

        CacheManager.clear_topics_cache()
        st.rerun()
        return True

    # ------------------------------------------------------------------ #
    # Persistence + navigation
    # ------------------------------------------------------------------ #
    def _persist_user(
        self,
        selected_topic: str = "",
        custom_topic: str = None,
    ) -> bool:
        """Update the user's topic selection in the database using phone number.
        Preserves existing name and teammate_name fields.
        For predefined topic selection: sets topic_id and unsets custom_topic.
        For custom topic selection: sets custom_topic and unsets topic_id.
        For deselection: unsets both topic_id and custom_topic.
        """
        # Get the phone number from session
        phone_number = SessionManager.get("phone_number", "")
        if not phone_number:
            return False

        # Get name and teammate_name from session to preserve them
        name = SessionManager.get("name", "")
        teammate_name = SessionManager.get("teammate_name", "")

        try:
            # Check if we have a non-empty custom topic
            has_custom_topic = custom_topic is not None and custom_topic.strip() != ""

            if has_custom_topic:
                # Custom topic selected: set custom_topic and unset topic_id
                result = self.db.db["users"].update_one(
                    {"phone_number": phone_number},
                    {"$set": {
                        "phone_number": phone_number,
                        "name": name,
                        "teammate_name": teammate_name,
                        "custom_topic": custom_topic.strip()
                    }, "$unset": {"topic_id": ""}}
                )
                return result.matched_count > 0 or result.upserted_id is not None
            elif selected_topic:
                # Predefined topic selected: set topic_id and unset custom_topic
                # Find the topic ID corresponding to the selected topic name
                topic_id = None
                topics = self.db.get_all_topics()
                for topic in topics:
                    if topic.get("topic_name") == selected_topic:
                        topic_id = topic.get("_id")
                        break
                # Update phone_number, topic_id, and preserve name and teammate_name
                user_data = {
                    "phone_number": phone_number,
                    "name": name,
                    "teammate_name": teammate_name,
                    "topic_id": topic_id,
                }
                return self.db.save_or_update_user(user_data)
            else:
                # Deselection: unset both topic_id and custom_topic while keeping other fields
                result = self.db.db["users"].update_one(
                    {"phone_number": phone_number},
                    {"$set": {
                        "phone_number": phone_number,
                        "name": name,
                        "teammate_name": teammate_name
                    }, "$unset": {"topic_id": "", "custom_topic": ""}}
                )
                return result.matched_count > 0 or result.upserted_id is not None
        except Exception as e:
            print(f"Error persisting user for {phone_number}: {e}")
            return False

    def _has_selection(self) -> bool:
        """Whether the user currently has a selected topic (predefined or custom)."""
        selected_option = SessionManager.get("selected_option", None)
        custom_topic = SessionManager.get("custom_topic", None)
        return selected_option is not None or bool(custom_topic)

    def _render_continue(self) -> bool:
        """Render the continue-to-results button."""
        if not self._has_selection():
            st.markdown(
                '<div class="error-message">الرجاء اختيار موضوع واحد</div>',
                unsafe_allow_html=True,
            )

        if st.button(
            "✅ متابعة",
            type="primary",
            use_container_width=True,
            key="submit_btn",
            disabled=not self._has_selection(),
        ):
            # Every selection was already auto-saved and verified; this just confirms.
            SessionManager.set("submitted", True)
            return True
        return False