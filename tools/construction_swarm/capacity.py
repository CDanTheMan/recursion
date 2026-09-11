"""Conservative per-campaign admission against current host headroom."""
import ctypes
import os
import shutil

from .contracts import require

JOB_BYTES = 2 * 1024**3
RESERVE_BYTES = 3 * 1024**3


def free_memory():
    if os.name == 'nt':
        class Memory(ctypes.Structure):
            _fields_ = [('length', ctypes.c_ulong), ('load', ctypes.c_ulong)] + [
                (name, ctypes.c_ulonglong) for name in
                ['total', 'available', 'page_total', 'page_available', 'virtual_total',
                 'virtual_available', 'extended']]
        memory = Memory()
        memory.length = ctypes.sizeof(memory)
        require(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory)), 'memory observation failed')
        return memory.available
    from pathlib import Path
    values = dict(line.split(':', 1) for line in Path('/proc/meminfo').read_text().splitlines())
    return int(values['MemAvailable'].split()[0]) * 1024


def slot_ceiling(available):
    return max(0, (available - RESERVE_BYTES) // JOB_BYTES)


def admit_host(root):
    require(free_memory() >= JOB_BYTES + RESERVE_BYTES, 'less than 5 GiB free RAM')
    require(shutil.disk_usage(root).free >= 1024**3, 'less than 1 GiB free evidence disk')
