"""Independent named-component implementation; no unified transition import."""
from pg_encoding import FIELDS


def step(encoded, action, size):
    tick = encoded[0] + 1
    supply = {"count": encoded[1], "arrivals": list(encoded[2])}
    if action == "O":
        if supply["count"] != size:
            supply["arrivals"][supply["count"]] = tick
            supply["count"] += 1
    results = []
    for index in range(2):
        parts = dict(zip(FIELDS, encoded[3 + index]))
        if action == "C":
            if parts["active"]:
                ordinal = parts["position"]
                if ordinal == parts["captured"]:
                    parts["active"] = False
                    parts["checks"] += 1
                    if parts["captured"] != parts["visible"]:
                        parts["invalidated"] += 1
                        parts["retry_needed"] = True
                    else:
                        parts["checked"] = parts["captured"]
                else:
                    tally = list(parts["reads"])
                    tally[ordinal] += 1
                    parts["reads"] = tuple(tally)
                    parts["position"] = ordinal + 1
            elif parts["visible"] != parts["checked"]:
                parts["active"] = True
                parts["captured"] = parts["visible"]
                parts["position"] = 0
                parts["captures"] += 1
                if parts["retry_needed"]:
                    parts["retries"] += 1
                parts["retry_needed"] = False
        if action == "A":
            next_record = parts["visible"]
            if next_record != supply["count"]:
                closed = index == 1 and parts["active"]
                if closed:
                    parts["postponed"] += 1
                else:
                    waiting = list(parts["waits"])
                    waiting[next_record] = tick - supply["arrivals"][next_record]
                    parts["waits"] = tuple(waiting)
                    parts["visible"] = next_record + 1
        results.append(tuple(parts[field] for field in FIELDS))
    return (tick, supply["count"], tuple(supply["arrivals"]), *results)
