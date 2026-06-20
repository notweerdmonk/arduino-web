"""Tests for pub/sub topic router with :: separator"""

import pytest

from board_manager.router import TopicRouter, _match


class TestTopicMatch:
    def test_exact_match(self):
        assert _match("board::port1::event", "board::port1::event")

    def test_single_level_wildcard(self):
        assert _match("board::port1::event", "board::+::event")
        assert _match("board::anything::event", "board::+::event")

    def test_multi_level_wildcard(self):
        assert _match("board::port1::event", "board::*")

    def test_no_match_different_port(self):
        assert not _match("board::port1::event", "board::port2::event")

    def test_no_match_different_depth(self):
        assert not _match("board::port1::event::extra", "board::+::event")

    def test_wildcard_only(self):
        assert _match("anything::at::all", "*")

    def test_empty_topic_no_match(self):
        assert not _match("", "board::+::event")

    def test_plus_must_match_segment(self):
        assert not _match("board::event", "board::+::event")

    def test_trailing_star(self):
        assert _match("a::b::c::d", "a::b::*")

    def test_port_with_slashes(self):
        assert _match("board::/dev/ttyACM0::event", "board::+::event")


class TestTopicRouter:
    def test_subscribe_and_publish(self):
        router = TopicRouter()
        received = []

        def handler(msg):
            received.append(msg)

        router.subscribe("sub1", "board::+::event", handler=handler)
        router.publish("board::/dev/ttyACM0::event", {"type": "connected"})
        assert len(received) == 1
        assert received[0] == {"type": "connected"}

    def test_multiple_subscribers(self):
        router = TopicRouter()
        r1, r2 = [], []

        router.subscribe("s1", "board::+::event", handler=lambda m: r1.append(m))
        router.subscribe("s2", "board::+::event", handler=lambda m: r2.append(m))
        router.publish("board::p1::event", {"x": 1})

        assert len(r1) == 1
        assert len(r2) == 1

    def test_unsubscribe(self):
        router = TopicRouter()
        received = []
        router.subscribe("s1", "board::+::event", handler=lambda m: received.append(m))
        router.unsubscribe("s1", "board::+::event")
        router.publish("board::p1::event", {"x": 1})
        assert len(received) == 0

    def test_unsubscribe_all(self):
        router = TopicRouter()
        received = []
        router.subscribe("s1", "board::+::event", handler=lambda m: received.append(m))
        router.subscribe("s1", "resp::+", handler=lambda m: received.append(m))
        router.unsubscribe_all("s1")
        router.publish("board::p1::event", {"x": 1})
        router.publish("resp::r1", {"y": 2})
        assert len(received) == 0

    def test_publish_no_subscribers(self):
        router = TopicRouter()
        result = router.publish("some::topic", {"x": 1})
        assert result == []

    def test_subscriber_not_called_for_non_matching(self):
        router = TopicRouter()
        received = []
        router.subscribe("s1", "board::p1::event", handler=lambda m: received.append(m))
        router.publish("board::p2::event", {"x": 1})
        assert len(received) == 0

    def test_handler_not_required(self):
        router = TopicRouter()
        router.subscribe("s1", "board::+::event")
        result = router.publish("board::p1::event", {"x": 1})
        assert result == ["s1"]

    def test_subscribers_for(self):
        router = TopicRouter()
        router.subscribe("s1", "board::+::event")
        router.subscribe("s2", "board::+::status")
        router.subscribe("s3", "board::p1::*")

        subs = router.subscribers_for("board::p1::event")
        assert "s1" in subs
        assert "s3" in subs
        assert "s2" not in subs

    def test_patterns_property(self):
        router = TopicRouter()
        router.subscribe("s1", "board::+::event")
        router.subscribe("s2", "resp::+")
        assert set(router.patterns) == {"board::+::event", "resp::+"}

    def test_subscribe_twice_same_pattern(self):
        router = TopicRouter()
        received = []
        router.subscribe("s1", "board::+::event", handler=lambda m: received.append(m))
        router.subscribe("s1", "board::+::event", handler=lambda m: received.append(m))
        router.publish("board::p1::event", {"x": 1})
        assert len(received) == 1

    def test_cleanup_empty_patterns(self):
        router = TopicRouter()
        router.subscribe("s1", "board::+::event")
        router.unsubscribe("s1", "board::+::event")
        assert router.patterns == []
