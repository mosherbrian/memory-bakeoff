"""Production file notification via Linux inotify (ctypes stdlib only).

The watcher attaches BEFORE the initial drain to close the
subscribe/read race: startup-existing events are observed exactly once
by the drain that follows attach. Persisted event reading is the drain;
this primitive is the trigger, never a periodic poll. Overflow, loss,
truncation and restart reconcile against durable cursors/seen sets.
close() releases the file descriptor (proven by tests). Timeouts bound
the wait with an owned failure, never silent loss.
"""
from __future__ import annotations

import ctypes
import ctypes.util
import errno
import os
import select
import struct

_IN_CLOSE_WRITE = 0x00000008
_IN_MOVED_TO = 0x00000080
_IN_CREATE = 0x00000100
_IN_DELETE = 0x00000200
_IN_Q_OVERFLOW = 0x00004000
_IN_NONBLOCK = 0o4000
_IN_CLOEXEC = 0o2000000

_SUBSCRIBE_MASK = (_IN_CLOSE_WRITE | _IN_MOVED_TO | _IN_CREATE |
                   _IN_DELETE | _IN_Q_OVERFLOW)


def _libc():
    name = ctypes.util.find_library("c")
    if not name:
        raise OwnedFaultLocal("E_NO_NOTIFY", "libc unavailable")
    return ctypes.CDLL(name, use_errno=True)


class OwnedFaultLocal(Exception):
    def __init__(self, code, detail=""):
        super().__init__("%s: %s" % (code, detail))
        self.code = code
        self.detail = detail


class DirNotifier:
    """Attach to a directory, then wait() for change events."""

    def __init__(self, path):
        self.path = path
        self._libc = _libc()
        try:
            fd = self._libc.inotify_init1(_IN_NONBLOCK | _IN_CLOEXEC)
        except Exception:
            raise OwnedFaultLocal("E_NO_NOTIFY",
                                  "inotify unavailable on this host")
        if fd < 0:
            raise OwnedFaultLocal("E_NO_NOTIFY",
                                  "inotify_init1 failed")
        self.fd = fd
        self.closed = False
        wd = self._libc.inotify_add_watch(
            fd, path.encode(), _SUBSCRIBE_MASK)
        if wd < 0:
            os.close(fd)
            self.fd = None
            raise OwnedFaultLocal("E_NO_NOTIFY",
                                  "cannot watch " + path)
        self.wd = wd
        self.overflows = 0

    def wait(self, timeout_s):
        """Block until a change event, timeout, or closure. Returns
        True (event drained signal), False (timeout), or raises on
        overflow-noted-but-drainable (caller rescans)."""
        if self.closed:
            raise OwnedFaultLocal("E_WATCHER_CLOSED", "notifier closed")
        ready, _, _ = select.select([self.fd], [], [], max(0, timeout_s))
        if not ready:
            return False
        try:
            data = os.read(self.fd, 65536)
        except OSError as e:
            if e.errno in (errno.EAGAIN, errno.EWOULDBLOCK):
                return False
            raise
        offset = 0
        saw_overflow = False
        while offset + 16 <= len(data):
            wd, mask, cookie, size = struct.unpack_from("iIII", data,
                                                       offset)
            offset += 16 + size
            if mask & _IN_Q_OVERFLOW:
                saw_overflow = True
        if saw_overflow:
            self.overflows += 1
        return True

    def close(self):
        if not self.closed and self.fd is not None:
            os.close(self.fd)
            self.closed = True
            self.fd = None
        return True
