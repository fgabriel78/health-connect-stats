class HealthConnectError(Exception):
    """Base exception for Health Connect Stats application."""
    pass

class ConfigError(HealthConnectError):
    """Configuration related errors."""
    pass

class FitbitAPIError(HealthConnectError):
    """Fitbit API related errors."""
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code

class FitbitAuthError(HealthConnectError):
    """Authentication related errors."""
    pass
