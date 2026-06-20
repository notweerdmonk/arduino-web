"""Pub/sub topic router with MQTT-style wildcards

Separator: :: (double colon — never appears in serial port paths).
Wildcards: + matches exactly one level, * matches any remaining levels.
"""

from collections import defaultdict
from typing import Callable, Optional

_SEP = "::"


def _match(topic: str, pattern: str) -> bool:
    """Match a topic string against a wildcard pattern.

    Supports ``+`` (single level) and ``*`` (remaining levels) wildcards.

    Args:
        topic: The topic to match.
        pattern: The pattern to match against.

    Returns:
        True if the topic matches the pattern.
    """
    t_segs = topic.split(_SEP)
    p_segs = pattern.split(_SEP)

    ti = 0
    pi = 0
    while pi < len(p_segs) and ti < len(t_segs):
        p = p_segs[pi]
        if p == "+":
            ti += 1
            pi += 1
        elif p == "*":
            return True
        elif p == t_segs[ti]:
            ti += 1
            pi += 1
        else:
            return False

    if pi == len(p_segs) and ti == len(t_segs):
        return True
    if pi == len(p_segs) and pi > 0 and p_segs[-1] == "*":
        return True

    return False


SubscriberId = str
EventHandler = Callable[[dict], None]


class TopicRouter:
    """Topic-based pub/sub router with wildcard support."""

    def __init__(self):
        """Initialize the router with empty subscriptions and handlers."""
        self._subs: dict[str, set[SubscriberId]] = defaultdict(set)
        self._handlers: dict[SubscriberId, Optional[EventHandler]] = {}

    def subscribe(
        self,
        subscriber_id: SubscriberId,
        topic_pattern: str,
        handler: Optional[EventHandler] = None,
    ) -> None:
        """Subscribe a client to a topic pattern.

        Args:
            subscriber_id: Unique client identifier.
            topic_pattern: Topic pattern with optional ``+`` and ``*`` wildcards.
            handler: Optional callback invoked on publish.
        """
        self._subs[topic_pattern].add(subscriber_id)
        if handler is not None:
            self._handlers[subscriber_id] = handler

    def unsubscribe(self, subscriber_id: SubscriberId, topic_pattern: str) -> None:
        """Remove a subscription for a client on a specific pattern."""
        self._subs[topic_pattern].discard(subscriber_id)
        if not self._subs[topic_pattern]:
            del self._subs[topic_pattern]

    def unsubscribe_all(self, subscriber_id: SubscriberId) -> None:
        """Remove all subscriptions for a client."""
        for pattern in list(self._subs):
            self._subs[pattern].discard(subscriber_id)
            if not self._subs[pattern]:
                del self._subs[pattern]
        self._handlers.pop(subscriber_id, None)

    def publish(self, topic: str, message: dict) -> list[SubscriberId]:
        """Publish a message to all subscribers whose patterns match the topic.

        Args:
            topic: The topic string.
            message: The message dict.

        Returns:
            List of subscriber IDs that received the message.
        """
        seen: set[SubscriberId] = set()
        matched: list[SubscriberId] = []
        for pattern, subscribers in self._subs.items():
            if _match(topic, pattern):
                for sid in subscribers:
                    if sid not in seen:
                        seen.add(sid)
                        matched.append(sid)
                        handler = self._handlers.get(sid)
                        if handler:
                            handler(message)
        return matched

    def subscribers_for(self, topic: str) -> set[SubscriberId]:
        """Return all subscriber IDs matching a given topic.

        Args:
            topic: The topic string.

        Returns:
            Set of matching subscriber IDs.
        """
        result: set[SubscriberId] = set()
        for pattern, subscribers in self._subs.items():
            if _match(topic, pattern):
                result.update(subscribers)
        return result

    @property
    def patterns(self) -> list[str]:
        """Return all registered topic patterns."""
        return list(self._subs.keys())
