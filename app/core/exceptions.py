from fastapi import HTTPException, status


class UserNotFoundException(HTTPException):

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


class EmailAlreadyExistsException(HTTPException):

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )