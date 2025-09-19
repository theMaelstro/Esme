"""
Config module contains Config class
with methods to handle reading and writing of config.ini file.
"""
import os.path
import json
import configparser
import dataclasses
import logging

@dataclasses.dataclass
class CommandSimple:
    """Class representing single config command settings."""
    enabled: bool
    cooldown: float
    permission: int

@dataclasses.dataclass
class ElevatedCommand:
    """
    Class representing single config
    elevated (admin) command settings.
    """
    enabled: bool
    cooldown: float
    permission: int
    admin_permission: int

@dataclasses.dataclass
class CommandValidated:
    """Class representing single config command settings."""
    enabled: bool
    cooldown: float
    hard_cooldown: int
    permission: int

@dataclasses.dataclass
class Toggle:
    """Class representing single config toggle settings."""
    enabled: bool

@dataclasses.dataclass
class Listeners:
    """Class representing config listeners settings."""
    discord: Toggle
    guild_applications: Toggle
    events: Toggle

@dataclasses.dataclass
class Tasks:
    """Class representing config tasks settings."""
    live_chat: Toggle
    players_count: Toggle

@dataclasses.dataclass
class Cogs:
    """Class representing config cogs settings."""
    group_account: Toggle
    group_guild: Toggle

@dataclasses.dataclass
class General:
    """Class representing config general settings."""
    debug: bool
    log_level: str

@dataclasses.dataclass
class Discord:
    """Class representing config discord settings."""
    token: str
    guild_id: str
    guild_channel_id: str
    status_category_id: str
    live_chat_category_id: str
    logs_channel_id: str
    elevated_users: list

@dataclasses.dataclass
class Erupe:
    """Class representing config erupe settings."""
    clan_member_limits: list
    timestamp_offset: int

@dataclasses.dataclass
class LiveChat:
    """Class representing config live chat settings"""
    listen_port: int
    remote_port: int
    api_key: str

@dataclasses.dataclass
class Database:
    """Class representing config database settings."""
    host: str
    username: str
    password: str
    port: int
    database: str

@dataclasses.dataclass
class Commands:
    """Class representing config commands settings."""
    account_bind_credentials: CommandSimple
    account_bind_token: CommandSimple
    account_card: ElevatedCommand
    account_character_backup: CommandValidated
    account_character_create: CommandSimple
    account_character_select: CommandSimple
    account_psn_clear: CommandSimple
    account_set_psn: CommandSimple
    account_token_reset: CommandSimple
    features: CommandSimple
    guild_application_list: CommandSimple
    guild_application_resolve: CommandSimple
    guild_apply: CommandSimple
    guild_invite: CommandSimple
    guild_list: CommandSimple
    guild_members: CommandSimple
    guild_members_expel: CommandSimple
    guild_members_list: CommandSimple
    guild_members_swap: CommandSimple
    guild_poogie: CommandSimple
    guild_set_leader: CommandSimple
    keyflag: CommandSimple
    ping: CommandSimple
    players_online: CommandSimple
    road_check: CommandSimple

@dataclasses.dataclass
class Features:
    """Class representing config features settings."""
    listeners: Listeners
    tasks: Tasks
    cogs_groups: Cogs

class Config:
    """Config class object."""
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.general: General
        self.discord: Discord
        self.erupe: Erupe
        self.livechat: LiveChat
        self.database: Database
        self.commands: Commands
        self.features: Features

    def create_config(self):
        """Create default config."""

        logging.info("Creating config.")
        # a Python object (dict):
        my_json = {
            'General': {
                'debug': True,
                'log_level': 'info'
            },
            'Discord': {
                'token': None,
                'guild_id': None,
                'guild_channel_id': None,
                'status_category_id': None,
                'live_chat_category_id': None,
                'logs_channel_id': None,
                'elevated_users': [
                    [0, []],
                    [1, []],
                    [2, []],
                    [3, []]
                ]
            },
            'LiveChat': {
                'listen_port': None,
                'remote_port': None,
                'api_key': None
            },
            'Database': {
                'host': 'localhost',
                'username': 'postgres',
                'password': None,
                'port': 5432,
                'database': 'erupe'
            },
            'Erupe': {
                'clan_member_limits': [[0, 30], [3, 40], [7, 50], [10, 60]],
                'timestamp_offset': 0
            },
            'Commands': {
                'account_bind_credentials': {'enabled': True, 'cooldown': 0.0, 'permission': None},
                'account_bind_token': {'enabled': True, 'cooldown': 0.0, 'permission': None},
                'account_card': {'enabled': True, 'cooldown': 0.0, 'permission': None, 'admin_permission': 0},
                'account_character_create': {'enabled': True, 'cooldown': 0.0, 'permission': None},
                'account_character_select': {'enabled': True, 'cooldown': 0.0, 'permission': None},
                'account_psn_clear': {'enabled': True, 'cooldown': 0.0, 'permission': None},
                'account_set_psn': {'enabled': True, 'cooldown': 0.0, 'permission': None},
                'account_token_reset': {'enabled': True, 'cooldown': 0.0, 'permission': None},
                'features': {'enabled': True, 'cooldown': 0.0, 'permission': None},
                'guild_application_list': {'enabled': True, 'cooldown': 0.0, 'permission': None},
                'guild_application_resolve': {'enabled': True, 'cooldown': 0.0, 'permission': None},
                'guild_apply': {'enabled': True, 'cooldown': 0.0, 'permission': None},
                'guild_invite': {'enabled': True, 'cooldown': 0.0, 'permission': None},
                'guild_list': {'enabled': True, 'cooldown': 0.0, 'permission': None},
                'guild_members': {'enabled': True, 'cooldown': 0.0, 'permission': None},
                'guild_members_expel': {'enabled': True, 'cooldown': 0.0, 'permission': None},
                'guild_members_list': {'enabled': True, 'cooldown': 0.0, 'permission': None},
                'guild_members_swap': {'enabled': True, 'cooldown': 0.0, 'permission': None},
                'guild_poogie': {'enabled': True, 'cooldown': 0.0, 'permission': 0},
                'guild_set_leader': {'enabled': True, 'cooldown': 0.0, 'permission': 0},
                'keyflag': {'enabled': True, 'cooldown': 0.0, 'permission': None},
                'ping': {'enabled': True, 'cooldown': 0.0, 'permission': None},
                'players_online': {'enabled': True, 'cooldown': 0.0, 'permission': None},
                'road_check': {'enabled': True, 'cooldown': 0.0, 'permission': 0}
            },
            'Features': {
                'Listeners': {
                    'discord': False,
                    'guild_applications': False,
                    'events': False
                },
                'Tasks': {
                    'live_chat': False,
                    'players_count': False
                },
                'Cogs': {
                    'group_account': {
                        'enabled': True
                    },
                    'group_guild': {'enabled': True},
                }
            }
        }

        try:
            # Write the configuration to a file
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(my_json, f, ensure_ascii=False, indent=4)

            logging.info(
                (
                    "Edit config.json and use /reload_config command"
                    "or restart bot for changes to take effect."
                )
            )

        except Exception as e:
            logging.error("CONFIG CREATE: %s", e)

    def read_config(self):
        """Read config."""

        try:
            logging.info("Reading config.")
            with open('config.json', encoding='utf-8') as f:
                my_json = json.load(f)

            self.general = General(
                my_json['General']['debug'],
                my_json['General']['log_level']
            )

            self.discord = Discord(
                my_json['Discord']['token'],
                my_json['Discord']['guild_id'],
                my_json['Discord']['guild_channel_id'],
                my_json['Discord']['status_category_id'],
                my_json['Discord']['live_chat_category_id'],
                my_json['Discord']['logs_channel_id'],
                my_json['Discord']['elevated_users']
            )

            self.erupe = Erupe(
                my_json['Erupe']['clan_member_limits'],
                my_json['Erupe']['timestamp_offset']
            )

            self.livechat = LiveChat(
                my_json['LiveChat']['listen_port'],
                my_json['LiveChat']['remote_port'],
                my_json['LiveChat']['api_key']
            )

            self.database = Database(
                my_json['Database']['host'],
                my_json['Database']['username'],
                my_json['Database']['password'],
                my_json['Database']['port'],
                my_json['Database']['database'],
            )

            self.commands = Commands(
                CommandSimple(
                    my_json['Commands']['account_bind_credentials']['enabled'],
                    my_json['Commands']['account_bind_credentials']['cooldown'],
                    my_json['Commands']['account_bind_credentials']['permission']
                ),
                CommandSimple(
                    my_json['Commands']['account_bind_token']['enabled'],
                    my_json['Commands']['account_bind_token']['cooldown'],
                    my_json['Commands']['account_bind_token']['permission']
                ),
                ElevatedCommand(
                    my_json['Commands']['account_card']['enabled'],
                    my_json['Commands']['account_card']['cooldown'],
                    my_json['Commands']['account_card']['permission'],
                    my_json['Commands']['account_card']['admin_permission']
                ),
                CommandValidated(
                    my_json['Commands']['account_character_backup']['enabled'],
                    my_json['Commands']['account_character_backup']['cooldown'],
                    my_json['Commands']['account_character_backup']['hard_cooldown'],
                    my_json['Commands']['account_character_backup']['permission']
                ),
                CommandSimple(
                    my_json['Commands']['account_character_create']['enabled'],
                    my_json['Commands']['account_character_create']['cooldown'],
                    my_json['Commands']['account_character_create']['permission']
                ),
                CommandSimple(
                    my_json['Commands']['account_character_select']['enabled'],
                    my_json['Commands']['account_character_select']['cooldown'],
                    my_json['Commands']['account_character_select']['permission']
                ),
                CommandSimple(
                    my_json['Commands']['account_psn_clear']['enabled'],
                    my_json['Commands']['account_psn_clear']['cooldown'],
                    my_json['Commands']['account_psn_clear']['permission']
                ),
                CommandSimple(
                    my_json['Commands']['account_set_psn']['enabled'],
                    my_json['Commands']['account_set_psn']['cooldown'],
                    my_json['Commands']['account_set_psn']['permission']
                ),
                CommandSimple(
                    my_json['Commands']['account_token_reset']['enabled'],
                    my_json['Commands']['account_token_reset']['cooldown'],
                    my_json['Commands']['account_token_reset']['permission']
                ),
                CommandSimple(
                    my_json['Commands']['features']['enabled'],
                    my_json['Commands']['features']['cooldown'],
                    my_json['Commands']['features']['permission']
                ),
                CommandSimple(
                    my_json['Commands']['guild_application_list']['enabled'],
                    my_json['Commands']['guild_application_list']['cooldown'],
                    my_json['Commands']['guild_application_list']['permission']
                ),
                CommandSimple(
                    my_json['Commands']['guild_application_resolve']['enabled'],
                    my_json['Commands']['guild_application_resolve']['cooldown'],
                    my_json['Commands']['guild_application_resolve']['permission']
                ),
                CommandSimple(
                    my_json['Commands']['guild_apply']['enabled'],
                    my_json['Commands']['guild_apply']['cooldown'],
                    my_json['Commands']['guild_apply']['permission']
                ),
                CommandSimple(
                    my_json['Commands']['guild_invite']['enabled'],
                    my_json['Commands']['guild_invite']['cooldown'],
                    my_json['Commands']['guild_invite']['permission']
                ),
                CommandSimple(
                    my_json['Commands']['guild_list']['enabled'],
                    my_json['Commands']['guild_list']['cooldown'],
                    my_json['Commands']['guild_list']['permission']
                ),
                CommandSimple(
                    my_json['Commands']['guild_members']['enabled'],
                    my_json['Commands']['guild_members']['cooldown'],
                    my_json['Commands']['guild_members']['permission']
                ),
                CommandSimple(
                    my_json['Commands']['guild_members_expel']['enabled'],
                    my_json['Commands']['guild_members_expel']['cooldown'],
                    my_json['Commands']['guild_members_expel']['permission']
                ),
                CommandSimple(
                    my_json['Commands']['guild_members_list']['enabled'],
                    my_json['Commands']['guild_members_list']['cooldown'],
                    my_json['Commands']['guild_members_list']['permission']
                ),
                CommandSimple(
                    my_json['Commands']['guild_members_swap']['enabled'],
                    my_json['Commands']['guild_members_swap']['cooldown'],
                    my_json['Commands']['guild_members_swap']['permission']
                ),
                CommandSimple(
                    my_json['Commands']['guild_poogie']['enabled'],
                    my_json['Commands']['guild_poogie']['cooldown'],
                    my_json['Commands']['guild_poogie']['permission']
                ),
                CommandSimple(
                    my_json['Commands']['guild_set_leader']['enabled'],
                    my_json['Commands']['guild_set_leader']['cooldown'],
                    my_json['Commands']['guild_set_leader']['permission']
                ),
                CommandSimple(
                    my_json['Commands']['keyflag']['enabled'],
                    my_json['Commands']['keyflag']['cooldown'],
                    my_json['Commands']['keyflag']['permission']
                ),
                CommandSimple(
                    my_json['Commands']['ping']['enabled'],
                    my_json['Commands']['ping']['cooldown'],
                    my_json['Commands']['ping']['permission']
                ),
                CommandSimple(
                    my_json['Commands']['players_online']['enabled'],
                    my_json['Commands']['players_online']['cooldown'],
                    my_json['Commands']['players_online']['permission']
                ),
                CommandSimple(
                    my_json['Commands']['road_check']['enabled'],
                    my_json['Commands']['road_check']['cooldown'],
                    my_json['Commands']['road_check']['permission']
                )
            )

            self.features = Features(
                Listeners(
                    Toggle(
                        my_json['Features']['Listeners']['discord']
                    ),
                    Toggle(
                        my_json['Features']['Listeners']['guild_applications']
                    ),
                    Toggle(
                        my_json['Features']['Listeners']['events']
                    )
                ),
                Tasks(
                    Toggle(
                        my_json['Features']['Tasks']['live_chat']
                    ),
                    Toggle(
                        my_json['Features']['Tasks']['players_count']
                    )
                ),
                Cogs(
                    Toggle(
                        my_json['Features']['Cogs']['group_account']['enabled']
                    ),
                    Toggle(
                        my_json['Features']['Cogs']['group_guild']['enabled']
                    )
                )
            )

        except Exception as e:
            logging.error("CONFIG CREATE: %s", e)

    def init_config(self):
        """Initialize config, check if valid config exists."""
        try:
            # Check if file exists.
            logging.info("Trying to find config")
            if not os.path.isfile('config.json'):
                raise FileNotFoundError

            logging.info("Config found.")
            self.read_config()

        except FileNotFoundError:
            logging.error("Config not found.")
            self.create_config()
            self.read_config()

    def check_permission(
        self,
        permission: int,
        discord_user,
    ) -> bool:
        """Get permission from config."""
        try:
            if permission is None:
                return True
            roles = [role.id for role in discord_user.roles]
            # User priority over role
            for value in reversed(self.discord.elevated_users):
                if permission >= value[0] and discord_user.id in value[1]:
                    return True
            # If no user permission check roles
            for value in reversed(self.discord.elevated_users):
                if permission >= value[0] and len(list(set(roles) & set(value[1]))) > 0:
                    return True
            return False

        except Exception as e:
            logging.error("Permission Error: %s", e)
            return False

CONFIG = Config()
