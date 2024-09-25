class ConfigurationError(Exception):
    def __init__(self, reason: str):
        self.reason = reason

    def __str__(self):
        return f'ConfigurationError: {self.reason}'

