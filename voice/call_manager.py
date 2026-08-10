import time
import logging

logger = logging.getLogger(__name__)


class CallManager:
    """
    In-memory storage for active phone calls.
    Maintains session state across stateless Twilio webhooks.
    """

    def __init__(self):
        # Maps CallSid -> State Dictionary
        self.sessions = {}
        # Cleanup threshold (e.g. 1 hour)
        self.cleanup_threshold_seconds = 3600

    def get_or_create_session(self, call_sid, from_number):
        """
        Retrieve existing session or create a new one.
        """

        if call_sid not in self.sessions:

            logger.info(
                "Creating new session for call %s",
                call_sid
            )

            self.sessions[call_sid] = {
                "call_sid": call_sid,
                "phone_number": from_number,
                "order_state": {},
                "language": "en", # Default language
                "conversation_history": [],
                "last_active": time.time(),
                "created_at": time.time(),
            }

        else:

            # Update last active timestamp
            self.sessions[call_sid]["last_active"] = time.time()

        return self.sessions[call_sid]

    def update_session(self, call_sid, key, value):
        """
        Update a specific key in the session.
        """
        if call_sid in self.sessions:
            self.sessions[call_sid][key] = value
            self.sessions[call_sid]["last_active"] = time.time()

    def get_session(self, call_sid):
        """
        Get session by CallSid without creating if missing.
        """
        session = self.sessions.get(call_sid)
        if session:
            session["last_active"] = time.time()
        return session

    def end_session(self, call_sid):
        """
        Remove session from memory.
        """
        if call_sid in self.sessions:
            logger.info(
                "Ending session for call %s",
                call_sid
            )
            del self.sessions[call_sid]

    def cleanup_old_sessions(self):
        """
        Removes sessions that haven't been active for a while.
        """
        now = time.time()
        expired = [
            sid for sid, session in self.sessions.items()
            if (now - session["last_active"]) > self.cleanup_threshold_seconds
        ]

        for sid in expired:
            self.end_session(sid)


# Global singleton instance for use by FastAPI routes
call_manager = CallManager()
