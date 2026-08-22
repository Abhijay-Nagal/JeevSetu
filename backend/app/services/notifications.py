"""Notifies a contributor when their observation's status changes.

Channel (in-app only vs. also email) is still an open decision — see
Docs/architecture.md "Open Risks". In-app notifications can read status_events
directly, so this is a no-op until an email provider is chosen.
"""


def notify_contributor(observation_id: str, new_status: str) -> None:
    pass
