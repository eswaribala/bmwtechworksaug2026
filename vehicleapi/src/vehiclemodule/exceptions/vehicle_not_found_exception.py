class VehicleNotFoundException(Exception):
    """Custom exception class for vehicle not found errors."""

    def __init__(self, message):
        super().__init__(message)
        self.message = message