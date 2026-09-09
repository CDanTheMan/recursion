"""Immutable state encoding and schedules, without a transition implementation."""

# Per-policy tuple fields. Pending requests are the exact FIFO suffix [visible, offered).
FIELDS = ("visible", "captured", "position", "active", "checked", "retry_needed",
          "reads", "captures", "checks", "invalidated", "retries", "postponed", "waits", "budget")


def initial(n):
    policy = (1, 0, 0, False, -1, False, (0,) * n, 0, 0, 0, 0, 0,
              (0,) + (-1,) * (n - 1), 2)
    return (0, 1, (0,) + (-1,) * (n - 1), policy, policy, policy)


def opportunities(node, n):
    """A finite arbitrary prefix, then one specified bounded quiet continuation."""
    phase, index, state = node
    if phase == "prefix":
        if index < 6:
            return [(a, "prefix", index + 1) for a in "OAC"]
        return [("O", "offer", 0)] if state[1] < n else [("A", "service", 1)]
    if phase == "offer":
        return [("O", "offer", index + 1)] if state[1] < n else [("A", "service", 1)]
    rounds = (n + 1) * (n + 2) + 1
    if index < 2 * rounds:
        return [("A" if index % 2 == 0 else "C", "service", index + 1)]
    return []


def metrics(state):
    clock, offered, stamps, *policies = state
    result = {}
    for name, p in zip(("one", "drain", "two"), policies):
        v, cap, pos, active, checked, retry, reads, captures, checks, invalid, retries, postponed, waits, budget = p
        result[name] = {"visible": v, "offered": offered, "pending": list(range(v, offered)),
                        "pending_ages": [clock - stamps[i] for i in range(v, offered)],
                        "read_counts": reads, "read_work": sum(reads), "captures": captures,
                        "completed_traversals": checks, "invalidated_traversals": invalid,
                        "retry_starts": retries, "postponed_append_opportunities": postponed,
                        "completed_waits": waits[:v], "last_checked": checked,
                        "collector_active": active, "remaining_before_reseal": budget}
    return result
