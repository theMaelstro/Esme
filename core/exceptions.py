"""
Provides custom Exception subclasses.
"""
class CommandOnCooldown(Exception):
    """Command action is on cooldown."""

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

class UserNotBound(Exception):
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

class GuildAlreadyApplied(Exception):
    """
    Character already applied to given guild.
    """

class GuildFull(Exception):
    """
    Guild is full. Expel some members
    to make space for new ones.
    """

class GuildNameInvalid(Exception):
    """Guild Name is invalid."""

class GuildLeaderCandidateMissing(Exception):
    """No valid candidate to replace guild leader."""

class SettingNotConfigured(Exception):
    """Setting not configured in json file."""

class CharacterExists(Exception):
    """Character already exists."""

class CharacterNotInGuild(Exception):
    """Character is not a Guild member."""

class CharacterNotSet(Exception):
    """Character is not set."""

class CharacterAlreadyInGuild(Exception):
    """Character is already a guild member."""

class CharacterPendingInvite(Exception):
    """Character is already pending invite from guild."""

class CharacterNameInvalid(Exception):
    """Character Name is invalid."""

class CharactersAreEqual(Exception):
    """Characters cannot be swapped."""

class CharacterIsLeader(Exception):
    """Character is guild leader and cannot be swapped."""

class UsersAreEqual(Exception):
    """Users are equal."""

class MissingGuildApplications(Exception):
    """No Guild Applications found."""

class IncorrectPasswordHash(Exception):
    """Incorrect password hash."""

class EmptyContent(Exception):
    """Parsed username or message content is empty or consists of special characters in its entirety."""

class HTTPServerUnreachable(Exception):
    """HTTP Server did not respond."""

class InvalidChannel(Exception):
    """Command used in invalid channel."""

class TermsRejected(Exception):
    """Exception raised for custom error scenarios."""

    def __init__(self):
        self.message = "Terms not accepted."
        self.readable = (
            "You have not agreed to **Terms of Service**." +
            "\nNo further action will be taken." +
            "\n\nIf you wish to delete your **account bind data** please use `/account delete` command." +
            "\n\nIn case you want to review these **Terms of Service** again and access bot commands " +
            "that require binding of an in-game account with a bot, you can do so by using the `/terms` command."
        )
        super().__init__(self.message)

class TermsNotFound(Exception):
    """Could not find terms data."""

class LicenseNotFound(Exception):
    """Could not find license data."""
