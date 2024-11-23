class UserAlreadyExistsException(Exception):
    ...


class MissingFieldException(Exception):
    ...


class PasswordInsecureException(Exception):
    ...


class InvalidEmailException(Exception):
    ...


class MaximumListingsReachedException(Exception):
    ...


class InvalidValueForFieldException(Exception):
    ...


class FilePathDoesNotExistException(Exception):
    ...


class AllowedOnlyForPeopleOver18YearsException(Exception):
    ...
