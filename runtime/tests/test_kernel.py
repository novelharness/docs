from src.kernel import ClaudeCodeLikeRuntime


def test_kernel_run_lifecycle() -> None:
    kernel = ClaudeCodeLikeRuntime()
    run = kernel.create_run(
        {
            "chapter_id": "ch009",
            "brief": "信息差导致误判",
            "target_words": 2200,
        }
    )

    assert run.status == "PENDING"
    assert len(run.tasks) == 6

    executed = kernel.execute_all(run.run_id)
    assert executed.status in {"PASS", "REWRITE"}
    assert len(executed.events) >= 6
