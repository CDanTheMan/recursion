"""Bounded JSONL observer for disposable installed-harness probes."""
import json
import threading
import time

SECRET_KEYS = {"access_token", "refresh_token", "id_token", "accesstoken", "refreshtoken", "authorization", "apikey", "api_key", "email", "chatgptaccountid", "account_id", "accountid"}

def redact(value):
    if isinstance(value, dict):
        return {k: "[REDACTED]" if k.lower() in SECRET_KEYS else redact(v) for k, v in value.items()}
    if isinstance(value, list): return [redact(x) for x in value]
    return value

class Rpc:
    def __init__(self, process, max_frame=2*1024**2, max_total=16*1024**2, max_events=6000):
        self.process = process
        self.max_frame, self.max_total, self.max_events = max_frame, max_total, max_events
        self.events, self.pending, self.errors = [], [], []
        self.total = 0; self.counter = 0; self.ended = False
        self.condition = threading.Condition(); self.write_lock = threading.Lock()
        self.start = time.monotonic()
        self.threads = [threading.Thread(target=self._read, args=(name, stream), daemon=True)
                        for name, stream in (("stdout", process.stdout), ("stderr", process.stderr))]
        for thread in self.threads: thread.start()

    def _record(self, direction, payload):
        with self.condition:
            if len(self.events) >= self.max_events: raise RuntimeError("event bound exceeded")
            self.events.append({"seq":len(self.events), "elapsed_s":round(time.monotonic()-self.start,6),
                                "direction":direction,"payload":redact(payload)})
            self.condition.notify_all()

    def _read(self, name, stream):
        try:
            while True:
                raw = stream.readline(self.max_frame+1)
                if not raw: break
                with self.condition:
                    self.total += len(raw)
                    if len(raw)>self.max_frame or self.total>self.max_total: raise RuntimeError("stream byte bound exceeded")
                if name == "stdout":
                    value = json.loads(raw)
                    self._record("receive",value)
                    with self.condition:
                        self.pending.append(value); self.condition.notify_all()
                else:
                    self._record("stderr",raw.decode("utf-8",errors="replace").rstrip())
        except BaseException as exc:
            with self.condition: self.errors.append(type(exc).__name__+": "+str(exc)); self.condition.notify_all()
        finally:
            if name=="stdout":
                with self.condition: self.ended=True; self.condition.notify_all()

    def send_raw(self, data, record=True):
        if len(data)>self.max_frame: raise ValueError("outgoing frame bound exceeded")
        if record:self._record("send_raw",{"length":len(data),"utf8":data.decode('utf-8',errors='replace')})
        with self.write_lock: self.process.stdin.write(data); self.process.stdin.flush()

    def send(self, value):
        self._record("send",value)
        self.send_raw((json.dumps(value,separators=(",",":"))+"\n").encode(),record=False)

    def begin(self, method, params):
        self.counter += 1
        self.send({"id":self.counter,"method":method,"params":params})
        return self.counter

    def wait(self, predicate, seconds=20):
        deadline=time.monotonic()+seconds
        with self.condition:
            while True:
                if self.errors: raise RuntimeError("; ".join(self.errors))
                for i,value in enumerate(self.pending):
                    if predicate(value): return self.pending.pop(i)
                if self.ended: raise EOFError("harness stdout closed before expected event")
                remaining=deadline-time.monotonic()
                if remaining<=0: raise TimeoutError("expected RPC response/event not observed")
                self.condition.wait(min(remaining,.25))

    def result(self, request_id, seconds=20, allow_error=False):
        value=self.wait(lambda x:x.get("id")==request_id and ("result" in x or "error" in x),seconds)
        if "error" in value and not allow_error: raise RuntimeError(json.dumps(value["error"]))
        return value

    def request(self, method, params, seconds=20, allow_error=False):
        return self.result(self.begin(method,params),seconds,allow_error)

    def event(self, method, seconds=20, match=lambda x:True):
        return self.wait(lambda x:x.get("method")==method and match(x),seconds)

    def finish(self):
        for thread in self.threads: thread.join(timeout=2)
        return {"events":self.events,"stream_errors":self.errors,"bytes":self.total,"stdout_ended":self.ended,
                "reader_threads_alive":sum(thread.is_alive() for thread in self.threads)}

def validate_trace(trace):
    if trace is None or trace["stream_errors"] or not trace["stdout_ended"] or trace["reader_threads_alive"]:
        raise ValueError("incomplete or failed stream observation")
    if [e["seq"] for e in trace["events"]]!=list(range(len(trace["events"]))):
        raise ValueError("noncontiguous observer trace")
