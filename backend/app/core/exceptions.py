class AppError(Exception):
    status_code: int = 400
    code: str = "APP_ERROR"

    def __init__(self, message: str, details: dict | None = None):
        self.message = message
        self.details = details
        super().__init__(message)


class UnauthorizedError(AppError):
    status_code = 401
    code = "UNAUTHORIZED"


class ForbiddenError(AppError):
    status_code = 403
    code = "FORBIDDEN"


class NotFoundError(AppError):
    status_code = 404
    code = "NOT_FOUND"


class ConflictError(AppError):
    status_code = 409
    code = "CONFLICT"
