"""Bounded trusted CLI transport; this is not itself a filesystem sandbox."""
import os
import signal
import subprocess
import threading
import time


def execute(argv, cwd, env, timeout, output_limit, stop=lambda: False):
    job = None
    if os.name == 'nt':
        from ._windows import Job, Process
        job = Job(max_processes=16, memory_bytes=2 * 1024**3)
        try:
            proc = Process(argv, cwd, env, job=job)
        except BaseException:
            job.close()
            raise
    else:
        proc = subprocess.Popen(argv, cwd=cwd, env=env, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                start_new_session=True)
    proc.stdin.close()
    buffers = [bytearray(), bytearray()]
    overflow = threading.Event()
    mutex = threading.Lock()

    def drain(stream, buf):
        while True:
            chunk = stream.read(4096)
            if not chunk:
                break
            with mutex:
                remaining = output_limit - sum(map(len, buffers))
                buf.extend(chunk[:max(0, remaining)])
                if len(chunk) > remaining:
                    overflow.set()

    threads = [threading.Thread(target=drain, args=(stream, buf), daemon=True)
               for stream, buf in zip((proc.stdout, proc.stderr), buffers)]
    for thread in threads:
        thread.start()
    begin = time.monotonic()
    reason = None
    quiescent = False
    try:
        while proc.poll() is None:
            if stop():
                reason = 'cancelled'
            elif overflow.is_set():
                reason = 'output-limit'
            elif time.monotonic() - begin >= timeout:
                reason = 'timeout'
            if reason:
                break
            time.sleep(.025)
    finally:
        # Always reap descendants, including children left behind by a successful CLI.
        try:
            if job:
                job.terminate()
                until = time.monotonic() + 5
                while time.monotonic() < until:
                    if job.accounting()['ActiveProcesses'] == 0:
                        quiescent = True
                        break
                    time.sleep(.025)
            else:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                # Direct process/pipe observation only. Cgroups add Linux tree proof.
            proc.wait(5)
            for thread in threads:
                thread.join(5)
            readers_done = not any(t.is_alive() for t in threads)
            if not job:
                quiescent = readers_done
            code = proc.poll()
        finally:
            if job:
                try:
                    job.close()  # kill-on-close even if terminate/accounting raised
                finally:
                    proc.close()
            else:
                proc.stdout.close()
                proc.stderr.close()
    return {'exit_code': code, 'reason': reason or ('output-limit' if overflow.is_set() else None),
            'local_quiescent': quiescent and readers_done,
            'elapsed_seconds': time.monotonic() - begin,
            'stdout': bytes(buffers[0]), 'stderr': bytes(buffers[1])}
