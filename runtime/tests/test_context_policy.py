from src.context_policy import build_agent_packet


def test_info_gap_visibility() -> None:
    payload = {"chapter_id": "ch001", "brief": "测试", "target_words": 1800}
    state = {
        "events": [
            {"id": "e1", "text": "only protagonist", "visible_to": ["protagonist"]},
            {"id": "e2", "text": "all", "visible_to": ["*"]},
        ],
        "facts": [
            {"id": "f1", "text": "director secret", "known_by": ["director"]},
            {"id": "f2", "text": "public", "known_by": ["*"]},
        ],
        "role_core": {"protagonist": ["成长"]},
    }

    protagonist = build_agent_packet("protagonist", payload, state)
    director = build_agent_packet("director", payload, state)

    assert len(protagonist["recent_events"]) == 2
    assert len(director["recent_events"]) == 1
    assert len(protagonist["known_facts"]) == 1
    assert len(director["known_facts"]) == 2
