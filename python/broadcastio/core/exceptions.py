from broadcastio.core.error_codes import ErrorCode


class BroadcastioError(Exception):
    """
    Base exception for all broadcastio errors.
    """

    code: str = "BROADCASTIO_ERROR"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ConfigurationError(BroadcastioError):
    code = ErrorCode.PROVIDER_MISCONFIGURED


class OrchestrationError(BroadcastioError):
    code = ErrorCode.NO_PROVIDERS


class ProviderError(BroadcastioError):
    code = ErrorCode.PROVIDER_MISCONFIGURED


class AttachmentError(BroadcastioError):
    code = ErrorCode.ATTACHMENT_NOT_FOUND


class ValidationError(BroadcastioError):
    code = ErrorCode.INVALID_MESSAGE
