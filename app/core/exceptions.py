"""Custom exception classes."""


class DecisionFlowError(Exception):
    """Base exception for DecisionFlow errors."""

    pass


class LLMError(DecisionFlowError):
    """Exception raised for LLM-related errors."""

    def __init__(
        self,
        message: str,
        *,
        retryable: bool = False,
        status_code: int | None = None,
        original_error: Exception | None = None,
    ) -> None:
        super().__init__(message)
        self.retryable = retryable
        self.status_code = status_code
        self.original_error = original_error


class LLMTimeoutError(LLMError):
    """Exception raised when LLM call times out."""

    def __init__(self, message: str = "LLM request timed out") -> None:
        super().__init__(message, retryable=True)


class LLMRateLimitError(LLMError):
    """Exception raised when LLM rate limit is exceeded."""

    def __init__(
        self,
        message: str = "LLM rate limit exceeded",
        retry_after: int | None = None,
    ) -> None:
        super().__init__(message, retryable=False, status_code=429)
        self.retry_after = retry_after


class ValidationError(DecisionFlowError):
    """Exception raised for validation errors."""

    pass


class AgentError(DecisionFlowError):
    """Exception raised for agent execution errors."""

    def __init__(self, message: str, agent_name: str | None = None) -> None:
        super().__init__(message)
        self.agent_name = agent_name


