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
        topics_data = CacheManager.get_topics_data()

        if not topics_data:
            st.warning("لا توجد مواضيع متاحة حالياً — تأكد من تهيئة قاعدة البيانات.")
            return

        counts = self._combined_counts(topics_data)

        for num, (name, info) in enumerate(topics_data.items(), start=1):
            self._render_topic_card(num, name, info, counts)

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
        self._persist_user(selected_topic=name)

        # Clear temp counts for updated topics since we'll get fresh data from DB on rerun
        temp = SessionManager.get("temp_counts", {})
        if current and current in temp:
            del temp[current]
        if name in temp:
            del temp[name]
        SessionManager.set("temp_counts", temp)

        CacheManager.clear_topics_cache()
        st.rerun(scope="fragment")
        return True

    def _deselect_topic(self, name: str) -> bool:
        """Release the currently-held predefined topic."""
        self.db.update_topic_count(name, -1)
        self._bump_temp(name, -1)
        SessionManager.update({
            "selected_option": None,
        })
        self._persist_user(selected_topic="")

        # Clear temp count for updated topic since we'll get fresh data from DB on rerun
        temp = SessionManager.get("temp_counts", {})
        if name in temp:
            del temp[name]
        SessionManager.set("temp_counts", temp)

        CacheManager.clear_topics_cache()
        st.rerun(scope="fragment")
        return True

    # ------------------------------------------------------------------ #
    # Persistence + navigation
    # ------------------------------------------------------------------ #
    def _persist_user(
        self,
        selected_topic: str = "",
    ) -> bool:
        """Update the user's topic selection in the database using phone number."""
        # Get the phone number from session
        phone_number = SessionManager.get("phone_number", "")
        if not phone_number:
            return False

        # Find the topic ID corresponding to the selected topic name
        topic_id = None
        if selected_topic:
            topics = self.db.get_all_topics()
            for topic in topics:
                if topic.get("topic_name") == selected_topic:
                    topic_id = topic.get("_id")
                    break

        # Update only the phone_number and topic_id fields
        # This will preserve existing name and teammate_name values
        user_data = {
            "phone_number": phone_number,
            "topic_id": topic_id,
        }
        return self.db.save_or_update_user(user_data)

    def _has_selection(self) -> bool:
        """Whether the user currently has a selected topic."""
        return SessionManager.get("selected_option", None) is not None

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
            # Every selection was already auto-saved; this just confirms.
            SessionManager.set("submitted", True)
            return True
        return False