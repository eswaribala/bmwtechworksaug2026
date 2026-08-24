class VehicleDataException(Exception):
    """Custom exception class for vehicle data errors."""

    def __init__(self, message):
        super().__init__(message)
        self.message = message