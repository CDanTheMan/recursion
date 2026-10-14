"""Failures raised by the harness slice."""


class HarnessError(RuntimeError):
    """A task was not planned, admitted, or executed."""


class LiveProviderDisabled(HarnessError):
    """A headless CLI adapter refused to start without an explicit live opt-in."""
