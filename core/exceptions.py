"""
Provides custom Exception subclasses.
"""
class UserEmptyField(Exception):
    """One of empty fields is empty."""

class InvalidUsername(Exception):
    """Username contains forbidden characters."""

class UsernameTooShort(Exception):
    """Username is too short."""

class UsernameTooLong(Exception):
    """Username is too long."""

class UnmatchingPasswords(Exception):
    """Paswords are not matching."""

class PasswordTooShort(Exception):
    """Password is too short."""

class PasswordTooLong(Exception):
    """Password is too long."""

class OldPasswordIncorrect(Exception):
    """Current password is invalid."""

class DiscordAlreadyRegistered(Exception):
    """Discord user is already registered in database."""

class DiscordNotRegistered(Exception):
    """Discord user is not registered in database."""

class UsernameAlreadyRegistered(Exception):
    """Username is already registered in database."""

class UsernameIncorrect(Exception):
    """Username is already registered in database."""

class PsnIDAlreadyRegistered(Exception):
    """Psn ID is already reegistered to a different user."""

class RestrictedUsername(Exception):
    """Username is restricted or contains inappropriate words."""

class TokenInvalid(Exception):
    """User token is invalid."""

class MissingPermissions(Exception):
    """User is missing elevated permissions."""

class MissingArgument(Exception):
    """Missing required positional argument."""

class InvalidArgument(Exception):
    """Invalid positional argument."""

class CoroutineFailed(Exception):
    """
    Coroutine returned False or None.
    Following task execution not possible.
    """

class SettingNotConfigured(Exception):
    """Setting not configured in json file."""
