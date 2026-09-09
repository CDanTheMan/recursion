"""Independent relational equations for every field of an O/A/C transition."""


def require(value, message):
    if not value:
        raise ValueError(message)


def state_valid(state, n):
    tick, offered, arrivals, *policies = state
    require(1 <= offered <= n and len(arrivals) == n, "offered inventory")
    require(arrivals[0] == 0 and all(0 < arrivals[i] <= tick for i in range(1, offered)), "arrival times")
    require(all(arrivals[i] == -1 for i in range(offered, n)), "unoffered times")
    require(all(arrivals[i] < arrivals[i + 1] for i in range(offered - 1)), "FIFO offers")
    for index, p in enumerate(policies):
        v, cap, pos, active, checked, retry, reads, starts, checks, failures, retries, postponed, waits = p
        require(1 <= v <= offered and len(reads) == len(waits) == n, "record conservation")
        require(0 <= pos <= cap <= v and -1 <= checked <= v, "capture bounds")
        require(all(x >= 0 for x in reads) and all(x >= 0 for x in waits[:v]), "nonnegative work and completed waiting")
        require(all(x == -1 for x in waits[v:]), "pending service not discarded")
        require(checks <= starts <= checks + 1 and active == (starts == checks + 1), "collector lifecycle")
        require(0 <= retries <= failures <= checks and postponed >= 0, "event accounting")
        require(retry == (failures > retries), "deferred retry accounting")
        if index == 1:
            require(failures == retries == 0 and (not active or cap == v), "sealed window stability")
        else:
            require(postponed == 0, "optimistic append remains open")


def transition(before, action, after, n):
    require(action in ("O", "A", "C"), "declared action")
    state_valid(before, n)
    state_valid(after, n)
    tick, offered, arrivals, *old_policies = before
    ntick, noffered, narrivals, *new_policies = after
    offer = action == "O" and offered < n
    require(ntick == tick + 1 and noffered == offered + int(offer), "shared clock and supply")
    require(narrivals == tuple(ntick if offer and i == offered else arrivals[i] for i in range(n)), "exact offer timestamps")
    for index, (p, q) in enumerate(zip(old_policies, new_policies)):
        v, cap, pos, active, checked, retry, reads, starts, checks, failures, retries, postponed, waits = p
        nv, ncap, npos, nactive, nchecked, nretry, nreads, nstarts, nchecks, nfailures, nretries, npostponed, nwaits = q
        queued_service = action == "A" and v < offered
        closed = index == 1 and active
        service = queued_service and not closed
        opening = action == "C" and not active and checked != v
        reading = action == "C" and active and pos < cap
        finishing = action == "C" and active and pos == cap
        failed = finishing and cap != v
        successful = finishing and cap == v
        require(nv == v + int(service), "one FIFO append service")
        require(nwaits == tuple(ntick - arrivals[i] if service and i == v else waits[i] for i in range(n)), "complete service waiting")
        require(ncap == (v if opening else cap), "captured count")
        require(npos == (0 if opening else pos + int(reading)), "one read opportunity")
        require(nactive == (True if opening else False if finishing else active), "collection phase")
        require(nchecked == (cap if successful else checked), "local unchanged-count check")
        require(nretry == (False if opening else True if failed else retry), "retry obligation")
        require(nreads == tuple(reads[i] + int(reading and i == pos) for i in range(n)), "all per-record read work")
        require(nstarts == starts + int(opening) and nchecks == checks + int(finishing), "traversal events")
        require(nfailures == failures + int(failed) and nretries == retries + int(opening and retry), "failure versus actual retry")
        require(npostponed == postponed + int(queued_service and closed), "postponed append opportunity")


def complete(state, n):
    state_valid(state, n)
    require(state[1] == n, "all original records offered")
    for p in state[3:]:
        require(p[0] == n and p[4] == n and not p[3], "quiet continuation fully serviced and checked")


def initial_valid(state, n):
    require(state[:2] == (0, 1), "initial clock and serviced record")
    require(state[2] == tuple(0 if i == 0 else -1 for i in range(n)), "initial offer timestamps")
    for p in state[3:]:
        require(p[:6] == (1, 0, 0, False, -1, False), "initial collector and prefix")
        require(p[6] == (0,) * n and p[7:12] == (0,) * 5, "zero initial measured work")
        require(p[12] == tuple(0 if i == 0 else -1 for i in range(n)), "initial waiting accounting")
    state_valid(state, n)


def metric_valid(state, reported):
    require(set(reported) == {"optimistic", "sealed"}, "both reported alternatives")
    for name, p in zip(("optimistic", "sealed"), state[3:]):
        expected = {
            "visible": p[0], "offered": state[1], "pending": list(range(p[0], state[1])),
            "pending_ages": [state[0] - state[2][i] for i in range(p[0], state[1])],
            "read_counts": p[6], "read_work": sum(p[6]), "captures": p[7],
            "completed_traversals": p[8], "invalidated_traversals": p[9], "retry_starts": p[10],
            "postponed_append_opportunities": p[11], "completed_waits": p[12][:p[0]],
            "last_checked": p[4], "collector_active": p[3],
        }
        require(reported[name] == expected, "independent complete metric projection: " + name)


def schedule_valid(node, choices, n):
    phase, depth, state = node
    if phase == "prefix" and depth < 6:
        require(choices == [(a, "prefix", depth + 1) for a in ("O", "A", "C")], "complete ternary prefix")
    elif phase in ("prefix", "offer"):
        expected = [("O", "offer", 0 if phase == "prefix" else depth + 1)] if state[1] < n else [("A", "service", 1)]
        require(choices == expected, "complete remaining FIFO offers before service suffix")
    else:
        bound = 2 * ((n + 1) * (n + 2) + 1)
        require(phase == "service" and 1 <= depth <= bound, "service phase bounds")
        expected = [] if depth == bound else [("C" if depth % 2 else "A", "service", depth + 1)]
        require(choices == expected, "exact alternating quiet service rounds")
