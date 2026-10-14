"""Failures raised by the harness slice."""


class HarnessError(RuntimeError):
    """A task was not planned, admitted, or executed."""


class LiveProviderDisabled(HarnessError):
    """A headless CLI adapter refused to start without an explicit live opt-in."""


class ProviderCLIMissing(HarnessError):
    """The provider executable is not on PATH."""


class ProviderTimeout(HarnessError):
    """The provider process exceeded its configured timeout."""


class ProviderRateLimited(HarnessError):
    """The provider asked the harness to slow down."""


class RunCancelled(HarnessError):
    """A run was cancelled before this attempt finished."""
