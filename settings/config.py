"""
Config module contains Config class
with methods to handle reading and writing of config.ini file.
"""
import os.path
import json
from collections import namedtuple
import configparser
import dataclasses

@dataclasses.dataclass
class General:
    """Class representing config general settings."""
    debug: bool
    log_level: str

@dataclasses.dataclass
class Database:
    """Class representing config database settings."""
    host: str
    port: str
    password: str
    username: str
    db_auth: str
    db_characters: str

@dataclasses.dataclass
class Discord:
    """Class representing config discord settings."""
    server_id: str
    admin_user_ids: list
    logs_channel_id: str

@dataclasses.dataclass
class Commands:
    """Class representing config commands settings."""
    change_password: namedtuple
    character_list: namedtuple
    character_online_list: namedtuple
    guild_list: namedtuple
    realm: namedtuple
    recover_account: namedtuple
    register: namedtuple
    admin_execute_rc: bool
    account_details_admin: bool
    character_details_admin: bool
    reload_config: bool

@dataclasses.dataclass
class Game:
    """Class representing config game settings."""
    realm: str
    restricted_strings: list

class Config:
    """Config class object."""
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.general: General
        self.database: Database
        self.discord: Discord
        self.commands: Commands
        self.game: Game


    async def create_config(self):
        """Create default config."""

        print("INFO", "Creating config.")
        # a Python object (dict):
        my_json = {
            'General': {
                'debug': True,
                'log_level': 'info'
            },
            'Database': {
                'host': 'localhost',
                'port': '5432',
                'password': None,
                'username': None,
                'db_auth': 'acore_auth',
                'db_characters': 'acore_characters'
            },
            'Discord': {
                'server_id': None,
                'admin_user_ids': [],
                'logs_channel_id': None
            },
            'Commands': {
                'change_password': {"enabled": True, "cooldown": 60.0},
                'character_list': {"enabled": True, "cooldown": 60.0},
                'character_online_list': {"enabled": True, "cooldown": 60.0},
                'guild_list': {"enabled": True, "cooldown": 60.0},
                'realm': {"enabled": True, "cooldown": 60.0},
                'recover_account': {"enabled": True, "cooldown": 60.0},
                'register': {"enabled": True, "cooldown": 60.0},
                'admin_execute_rc': {"enabled": True},
                'account_details_admin': {"enabled": True},
                'character_details_admin': {"enabled": True},
                'reload_config': {"enabled": True},
            },
            'Game': {
                'realm': '127.0.0.1',
                'restricted_strings': ['ADMIN', 'RNDBOT']
            }
        }

        try:
            # Write the configuration to a file
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(my_json, f, ensure_ascii=False, indent=4)

            print(
                "INFO",
                (
                    "Edit config.json and use /reload_config command"
                    "or restart bot for changes to take effect."
                )
            )

        except Exception as e:
            print("CONFIG CREATE", e)

    async def read_config(self):
        """Read config."""

        try:
            print("INFO", "Reading config.")
            with open('config.json', encoding='utf-8') as f:
                my_json = json.load(f)

            self.general = General(
                my_json['General']['debug'],
                my_json['General']['log_level']
            )

            self.database = Database(
                my_json['Database']['host'],
                my_json['Database']['port'],
                my_json['Database']['password'],
                my_json['Database']['username'],
                my_json['Database']['db_auth'],
                my_json['Database']['db_characters'],
            )

            self.discord = Discord(
                my_json['Discord']['server_id'],
                my_json['Discord']['admin_user_ids'],
                my_json['Discord']['logs_channel_id']
            )

            command = namedtuple('Command', ['enabled', 'cooldown'])
            self.commands = Commands(
                command(
                    my_json['Commands']['character_list']['enabled'],
                    my_json['Commands']['character_list']['cooldown']
                ),
                command(
                    my_json['Commands']['change_password']['enabled'],
                    my_json['Commands']['change_password']['cooldown']
                ),
                command(
                    my_json['Commands']['character_online_list']['enabled'],
                    my_json['Commands']['character_online_list']['cooldown']
                ),
                command(
                    my_json['Commands']['guild_list']['enabled'],
                    my_json['Commands']['guild_list']['cooldown']
                ),
                command(
                    my_json['Commands']['realm']['enabled'],
                    my_json['Commands']['realm']['cooldown']
                ),
                command(
                    my_json['Commands']['recover_account']['enabled'],
                    my_json['Commands']['recover_account']['cooldown']
                ),
                command(
                    my_json['Commands']['register']['enabled'],
                    my_json['Commands']['register']['cooldown']
                ),
                my_json['Commands']['admin_execute_rc']['enabled'],
                my_json['Commands']['account_details_admin']['enabled'],
                my_json['Commands']['character_details_admin']['enabled'],
                my_json['Commands']['reload_config']['enabled']
            )

            self.game = Game(
                my_json['Game']['realm'],
                my_json['Game']['restricted_strings']
            )

        except Exception as e:
            print("CONFIG CREATE", e)

    async def init_config(self):
        """Initialize config, check if valid config exists."""
        try:
            # Check if file exists.
            print("INFO", "Trying to find config")
            if not os.path.isfile('config.json'):
                raise FileNotFoundError

            print("INFO", "Config found.")
            await self.read_config()

        except FileNotFoundError:
            print("WARNING", "Config not found.")
            await self.create_config()
            await self.read_config()

CONFIG = Config()
