"""Ask a different provider to approve or send a task back."""

from __future__ import annotations

from scripts.v3.harness.dispatch import execute_with_policy
from scripts.v3.harness.errors import HarnessError, RunCancelled
from scripts.v3.harness.providers import ProviderRequest
from scripts.v3.harness.usage import add_usage, empty_usage, parse_usage


NOTE_LIMIT = 1000


def parse_verdict(text: str) -> tuple[str, str]:
    """Read ``VERDICT approve`` or ``VERDICT revise``. Anything else is revise."""

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return "revise", "reviewer returned no verdict"
    first = lines[0]
    notes = "\n".join(lines[1:])[:NOTE_LIMIT]
    if first == "VERDICT approve":
        return "approve", notes
    if first == "VERDICT revise":
        return "revise", notes
    return "revise", "reviewer returned an unreadable verdict"


def review_prompt(task: str, output: str, diff: str) -> str:
    return "\n".join(
        (
            "Review this completed task.",
            "Reply with a first line of exactly 'VERDICT approve' or 'VERDICT revise'.",
            "",
            "Task:",
            task,
            "",
            "Output:",
            _clip(output),
            "",
            "Diff:",
            _clip(diff),
        )
    )


def execute_and_review(
    *,
    task: str,
    packet_id: str,
    route_id: str,
    candidates: list[str],
    allow_live: bool,
    retries: int,
    backoff_seconds: float,
    timeout_seconds: dict[str, int] | None,
    max_rounds: int,
    cwd: str | None,
    diff_of=None,
    log: object,
    open_adapter,
    sleep,
    should_stop,
    accept_unreviewed: bool = False,
    seal=None,
    snapshot=None,
    restore=None,
) -> dict:
    """Run the worker, then review with a different provider for up to ``max_rounds``.

    A reviewer that edits the worktree is rejected and the edits are removed.
    When no reviewer finishes, ``accept_unreviewed`` decides whether the worker
    result stands. The default records the task as unreviewed.
    """

    attempts: list[dict] = []
    reviews: list[dict] = []
    usage = empty_usage()
    request = ProviderRequest(task=task, packet_id=packet_id, route_id=route_id, kind="execute", cwd=cwd)
    result, worker_attempts = execute_with_policy(
        request,
        candidates,
        allow_live=allow_live,
        retries=retries,
        log=log,
        open_adapter=open_adapter,
        backoff_seconds=backoff_seconds,
        sleep=sleep,
        should_stop=should_stop,
        timeout_seconds=timeout_seconds,
    )
    attempts.extend(worker_attempts)
    add_usage(usage, parse_usage(result.text))
    if max_rounds <= 0:
        return _done(result, attempts, reviews, usage, disposition="completed")

    for round_index in range(1, max_rounds + 1):
        if should_stop is not None and should_stop():
            raise RunCancelled("run cancelled")
        reviewers = [name for name in candidates if name != result.provider]
        if not reviewers:
            reviews.append(
                {
                    "attempts": [],
                    "notes": "no distinct reviewer",
                    "reviewer": None,
                    "round": round_index,
                    "verdict": "skipped",
                }
            )
            return _unreviewed(result, attempts, reviews, usage, accept_unreviewed=accept_unreviewed)
        if seal is not None:
            seal()
        before = None if snapshot is None else snapshot()
        current_diff = "" if diff_of is None else diff_of()
        review_request = ProviderRequest(
            task=review_prompt(task, result.text, current_diff),
            packet_id=packet_id,
            route_id=route_id,
            kind="review",
            cwd=cwd,
        )
        try:
            review_result, review_attempts = execute_with_policy(
                review_request,
                reviewers,
                allow_live=allow_live,
                retries=retries,
                log=log,
                open_adapter=open_adapter,
                backoff_seconds=backoff_seconds,
                sleep=sleep,
                should_stop=should_stop,
                timeout_seconds=timeout_seconds,
            )
        except RunCancelled:
            if restore is not None:
                restore(before)
            raise
        except HarnessError as exc:
            wrote = restore is not None and restore(before)
            failed = list(getattr(exc, "attempts", []) or [])
            attempts.extend(failed)
            notes = "no reviewer completed"
            if wrote:
                notes = "no reviewer completed; reviewer modified the worktree"
            reviews.append(
                {
                    "attempts": failed,
                    "notes": notes,
                    "reviewer": None,
                    "round": round_index,
                    "verdict": "skipped",
                }
            )
            return _unreviewed(result, attempts, reviews, usage, accept_unreviewed=accept_unreviewed)
        attempts.extend(review_attempts)
        add_usage(usage, parse_usage(review_result.text))
        wrote = restore is not None and restore(before)
        if wrote:
            verdict, notes = "rejected-write", "reviewer modified the worktree"
        else:
            verdict, notes = parse_verdict(review_result.text)
        reviews.append(
            {
                "attempts": review_attempts,
                "notes": notes,
                "reviewer": review_result.provider,
                "round": round_index,
                "verdict": verdict,
            }
        )
        if verdict == "approve":
            return _done(result, attempts, reviews, usage, disposition="completed")
        if round_index == max_rounds:
            return _done(result, attempts, reviews, usage, disposition="review-rejected")
        revise = ProviderRequest(
            task=task + "\n\nReview notes:\n" + notes,
            packet_id=packet_id,
            route_id=route_id,
            kind="execute",
            cwd=cwd,
        )
        result, again = execute_with_policy(
            revise,
            [result.provider],
            allow_live=allow_live,
            retries=retries,
            log=log,
            open_adapter=open_adapter,
            backoff_seconds=backoff_seconds,
            sleep=sleep,
            should_stop=should_stop,
            timeout_seconds=timeout_seconds,
        )
        attempts.extend(again)
        add_usage(usage, parse_usage(result.text))
    return _done(result, attempts, reviews, usage, disposition="review-rejected")


def _unreviewed(result, attempts: list[dict], reviews: list[dict], usage: dict, *, accept_unreviewed: bool) -> dict:
    disposition = "completed" if accept_unreviewed else "unreviewed"
    return _done(result, attempts, reviews, usage, disposition=disposition)


def _done(result, attempts: list[dict], reviews: list[dict], usage: dict, *, disposition: str) -> dict:
    return {
        "accepted": disposition == "completed",
        "attempts": attempts,
        "disposition": disposition,
        "result": result,
        "reviews": reviews,
        "usage": usage,
    }


def _clip(text: str, limit: int = 2000) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n[truncated]"
