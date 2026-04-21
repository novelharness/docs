from src.orchestrator import run_pipeline


def test_pipeline_returns_pass() -> None:
    resp = run_pipeline(
        {
            "chapter_id": "ch001",
            "brief": "主角首次觉醒",
            "target_words": 2000,
        }
    )
    assert resp["status"] == "PASS"
    assert len(resp["steps"]) == 6
