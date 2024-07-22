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
class Command:
    """Class representing single config command settings."""
    enabled: bool
    cooldown: float

@dataclasses.dataclass
class Listener:
    """Class representing single config listener settings."""
    enabled: bool

@dataclasses.dataclass
class Listeners:
    """Class representing config listeners settings."""
    discord: Listener
    guild_applications: Listener
    events: Listener

@dataclasses.dataclass
class General:
    """Class representing config general settings."""
    debug: bool
    log_level: str

@dataclasses.dataclass
class Discord:
    """Class representing config discord settings."""
    token: str
    server_id: str
    # TODO: More complex administration permissions with access levels
    # where 0 = admin
    admin_user_ids: list
    guild_id: str
    guild_channel_id: str
    logs_channel_id: str

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
    account_bind_credentials: Command
    account_bind_token: Command
    account_set_psn: Command
    account_token_reset: Command
    character_select: Command
    guild_list: Command
    guild_members: Command
    guild_poogie: Command
    guild_set_leader: Command
    ping: Command
    road_check: Command

@dataclasses.dataclass
class Features:
    """Class representing config features settings."""
    listeners: Listeners

class Config:
    """Config class object."""
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.general: General
        self.discord: Discord
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
                'server_id': None,
                'admin_user_ids': [],
                'guild_id': None,
                'guild_channel_id': None,
                'logs_channel_id': None
            },
            "Database": {
                "host": "localhost",
                "username": "postgres",
                "password": None,
                "port": 5432,
                "database": "erupe"
            },
            'Commands': {
                'account_bind_credentials': {"enabled": True, "cooldown": 60.0},
                'account_bind_token': {"enabled": True, "cooldown": 60.0},
                'account_set_psn': {"enabled": True, "cooldown": 60.0},
                'account_token_reset': {"enabled": True, "cooldown": 60.0},
                'character_select': {"enabled": True, "cooldown": 60.0},
                'guild_list': {"enabled": True, "cooldown": 60.0},
                'guild_members': {"enabled": True, "cooldown": 60.0},
                'guild_poogie': {"enabled": True, "cooldown": 60.0},
                'guild_set_leader': {"enabled": True, "cooldown": 60.0},
                'ping': {"enabled": True, "cooldown": 60.0},
                'road_check': {"enabled": True, "cooldown": 60.0}
            },
            'Features': {
                'Listeners': {
                    'discord': False,
                    'guild_applications': True,
                    'events': True
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
                my_json['Discord']['server_id'],
                my_json['Discord']['admin_user_ids'],
                my_json['Discord']['guild_id'],
                my_json['Discord']['guild_channel_id'],
                my_json['Discord']['logs_channel_id']
            )

            self.database = Database(
                my_json['Database']['host'],
                my_json['Database']['username'],
                my_json['Database']['password'],
                my_json['Database']['port'],
                my_json['Database']['database'],
            )

            self.commands = Commands(
                Command(
                    my_json['Commands']['account_bind_credentials']['enabled'],
                    my_json['Commands']['account_bind_credentials']['cooldown']
                ),
                Command(
                    my_json['Commands']['account_bind_token']['enabled'],
                    my_json['Commands']['account_bind_token']['cooldown']
                ),
                Command(
                    my_json['Commands']['account_set_psn']['enabled'],
                    my_json['Commands']['account_set_psn']['cooldown']
                ),
                Command(
                    my_json['Commands']['account_token_reset']['enabled'],
                    my_json['Commands']['account_token_reset']['cooldown']
                ),
                Command(
                    my_json['Commands']['character_select']['enabled'],
                    my_json['Commands']['character_select']['cooldown']
                ),
                Command(
                    my_json['Commands']['guild_list']['enabled'],
                    my_json['Commands']['guild_list']['cooldown']
                ),
                Command(
                    my_json['Commands']['guild_members']['enabled'],
                    my_json['Commands']['guild_members']['cooldown']
                ),
                Command(
                    my_json['Commands']['guild_poogie']['enabled'],
                    my_json['Commands']['guild_poogie']['cooldown']
                ),
                Command(
                    my_json['Commands']['guild_set_leader']['enabled'],
                    my_json['Commands']['guild_set_leader']['cooldown']
                ),
                Command(
                    my_json['Commands']['ping']['enabled'],
                    my_json['Commands']['ping']['cooldown']
                ),
                Command(
                    my_json['Commands']['road_check']['enabled'],
                    my_json['Commands']['road_check']['cooldown']
                ),
            )

            self.features = Features(
                Listeners(
                    Listener(
                        my_json['Features']['Listeners']['discord']
                    ),
                    Listener(
                        my_json['Features']['Listeners']['guild_applications']
                    ),
                    Listener(
                        my_json['Features']['Listeners']['events']
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

CONFIG = Config()
