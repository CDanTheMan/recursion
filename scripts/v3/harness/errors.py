"""Failures raised by the harness slice."""


class HarnessError(RuntimeError):
    """A task was not planned, admitted, or executed."""


class LiveProviderDisabled(HarnessError):
    """A headless CLI adapter refused to start without an explicit live opt-in."""


class ProviderCLIMissing(HarnessError):
    """The provider executable is not on PATH."""


class ProviderTimeout(HarnessError):
    """The provider process exceeded its configured timeout."""


class ProviderAvailability(HarnessError):
    """The provider cannot take work until a cooldown ends."""

    def __init__(
        self,
        message: str,
        *,
        reason: str,
        until: str | None = None,
        retry_after: float | None = None,
    ) -> None:
        super().__init__(message)
        self.reason = reason
        self.until = until
        self.retry_after = retry_after


class ProviderRateLimited(ProviderAvailability):
    """The provider asked the harness to slow down."""

    def __init__(self, message: str, *, until: str | None = None, retry_after: float | None = None) -> None:
        super().__init__(message, reason="rate-limited", until=until, retry_after=retry_after)


class ProviderQuotaExhausted(ProviderAvailability):
    """The provider reported that its quota is exhausted."""

    def __init__(self, message: str, *, until: str | None = None, retry_after: float | None = None) -> None:
        super().__init__(message, reason="quota-exhausted", until=until, retry_after=retry_after)


class ProviderAuthExpired(ProviderAvailability):
    """The provider rejected the attempt because sign-in is no longer valid."""

    def __init__(self, message: str, *, until: str | None = None, retry_after: float | None = None) -> None:
        super().__init__(message, reason="auth-expired", until=until, retry_after=retry_after)


class ProviderTransient(HarnessError):
    """A short-lived process error that may succeed on retry."""


class RunCancelled(HarnessError):
    """A run was cancelled before this attempt finished."""
