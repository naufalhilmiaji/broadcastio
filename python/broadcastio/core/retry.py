from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Set

from broadcastio.core.exceptions import ErrorCode, ValidationError

_ALLOWED_BACKOFFS = {"none", "fixed", "exponential"}


@dataclass(frozen=True)
class RetryPolicy:
    """
    Defines retry behavior for a single provider.

    Retries are explicit, observable, and scoped per provider.
    """

    max_attempts: int = 1
    backoff: str = "none"  # "none" | "fixed" | "exponential"
    base_delay: float = 0.0
    max_delay: Optional[float] = None
    retry_on: Optional[Set[ErrorCode]] = None

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        # max_attempts
        if not isinstance(self.max_attempts, int) or self.max_attempts < 1:
            raise ValidationError("RetryPolicy.max_attempts must be an integer >= 1")

        # backoff strategy
        if self.backoff not in _ALLOWED_BACKOFFS:
            raise ValidationError(
                f"RetryPolicy.backoff must be one of {_ALLOWED_BACKOFFS}"
            )

        # base_delay
        if self.base_delay < 0:
            raise ValidationError("RetryPolicy.base_delay must be >= 0")

        # max_delay
        if self.max_delay is not None:
            if self.max_delay < 0:
                raise ValidationError("RetryPolicy.max_delay must be >= 0")
            if self.max_delay < self.base_delay:
                raise ValidationError("RetryPolicy.max_delay must be >= base_delay")

        # retry_on
        if self.retry_on is not None:
            if not isinstance(self.retry_on, set):
                raise ValidationError(
                    "RetryPolicy.retry_on must be a set of ErrorCode values"
                )

            invalid = [
                code for code in self.retry_on if not isinstance(code, ErrorCode)
            ]
            if invalid:
                raise ValidationError(
                    f"RetryPolicy.retry_on contains invalid ErrorCode values: {invalid}"
                )

    def should_retry(self, error_code: ErrorCode) -> bool:
        """
        Returns True if the given error code is retryable under this policy.
        """
        if self.retry_on is None:
            return error_code == ErrorCode.PROVIDER_UNAVAILABLE

        return error_code in self.retry_on
