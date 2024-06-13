"""Table mappings module"""
import datetime
from typing import List

from sqlalchemy import ForeignKey, LargeBinary, String
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

class Base(AsyncAttrs, DeclarativeBase):
    """Base table object"""

class B(Base):
    """Table B"""
    __tablename__ = "b"
    id: Mapped[int] = mapped_column(primary_key=True)
    a_id: Mapped[int] = mapped_column(ForeignKey("a.id"))
    data: Mapped[str]

class A(Base):
    """Table A"""
    __tablename__ = "a"
    id: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[str]
    create_date: Mapped[datetime.datetime] = mapped_column(server_default=func.now()) # pylint: disable=[not-callable]
    bs: Mapped[List[B]] = relationship()

class Achievements(Base):
    """Achievements table object"""
    __tablename__ = "a"

class Bans(Base):
    """Bans table object"""
    __tablename__ = "bans"
    id: Mapped[int] = mapped_column(primary_key=True)
    expires: Mapped[datetime.datetime] = mapped_column(server_default=func.now()) # pylint: disable=[not-callable]

class CafeAccepted(Base):
    """Cafe Accepted table object"""
    __tablename__ = "a"

class CafeBonus(Base):
    """Cafe Bonus table object"""
    __tablename__ = "a"

class Characters(Base):
    """Characters table object"""
    __tablename__ = "a"

class DiscordLink(Base):
    """Discord Link table object"""
    __tablename__ = "discordlink"
    id: Mapped[int] = mapped_column(primary_key=True)
    discordname: Mapped[str]
    user_id: Mapped[int]

class Distribution(Base):
    """Distribution table object"""
    __tablename__ = "a"

class DistributionItems(Base):
    """Distribution Items table object"""
    __tablename__ = "a"

class DistributionsAccepted(Base):
    """Distributions Accepted table object"""
    __tablename__ = "a"

class EventQuests(Base):
    """Event Quests table object"""
    __tablename__ = "a"

class Events(Base):
    """Events table object"""
    __tablename__ = "a"

class FeatureWeapon(Base):
    """Feature Weapon table object"""
    __tablename__ = "a"

class FestaPrizes(Base):
    """Festa Prizes table object"""
    __tablename__ = "a"

class FestaPrizesAccepted(Base):
    """Festa Prizes Accepted table object"""
    __tablename__ = "a"

class FestaRegistrations(Base):
    """Festa Registrations table object"""
    __tablename__ = "a"

class FestaSubmissions(Base):
    """Festa Submissions table object"""
    __tablename__ = "a"

class FestaTrials(Base):
    """Festa Trials table object"""
    __tablename__ = "festa_trials"
    id: Mapped[int] = mapped_column(primary_key=True)
    objective: Mapped[int]
    goal_id: Mapped[int]
    times_req: Mapped[int]
    locale_req: Mapped[int]
    reward: Mapped[int]

class FestaPointsItems(Base):
    """Festa Points Items table object"""
    __tablename__ = "a"

class GachaBox(Base):
    """Gacha Box table object"""
    __tablename__ = "a"

class GachaEntries(Base):
    """Gacha Entries table object"""
    __tablename__ = "a"

class GachaItems(Base):
    """Gacha Items table object"""
    __tablename__ = "a"

class GachaShop(Base):
    """Gacha Shop table object"""
    __tablename__ = "a"

class GachaStepUp(Base):
    """Gacha Step Up table object"""
    __tablename__ = "a"

class Goocoo(Base):
    """Goocoo table object"""
    __tablename__ = "a"

class GuildAdventures(Base):
    """Guild Adventures table object"""
    __tablename__ = "a"

class GuildAlliances(Base):
    """Guild Alliances table object"""
    __tablename__ = "a"

class GuildApplications(Base):
    """Guild Applications table object"""
    __tablename__ = "a"

class GuildCharacters(Base):
    """Guild Characters table object"""
    __tablename__ = "a"

class GuildHunts(Base):
    """Guild Hunts table object"""
    __tablename__ = "a"

class GuildHuntsClaimed(Base):
    """Guild Hunts Claimed table object"""
    __tablename__ = "a"

class GuildMeals(Base):
    """Guild Meals table object"""
    __tablename__ = "a"

class GuildPosts(Base):
    """Guild Posts table object"""
    __tablename__ = "a"

class Guilds(Base):
    """Guild table object"""
    __tablename__ = "guilds"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(24))
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now()) # pylint: disable=[not-callable]
    leader_id: Mapped[int]
    main_motto: Mapped[int]
    rank_rp: Mapped[int]
    comment: Mapped[str] = mapped_column(String(255))
    icon: Mapped[bytes] = mapped_column(LargeBinary())
    sub_motto: Mapped[int]
    item_box: Mapped[bytes] = mapped_column(LargeBinary())
    event_rp: Mapped[int]
    pugi_name_1: Mapped[str] = mapped_column(String(12))
    pugi_name_2: Mapped[str] = mapped_column(String(12))
    pugi_name_3: Mapped[str] = mapped_column(String(12))
    recruiting: Mapped[bool]
    pugi_outfit_1: Mapped[int]
    pugi_outfit_2: Mapped[int]
    pugi_outfit_3: Mapped[int]
    pugi_outfits: Mapped[int]
    tower_mission_page: Mapped[int]
    tower_rp: Mapped[int]
    #room_rp: Mapped[int]
    #room_expiry: Mapped[datetime.datetime]

class KillLogs(Base):
    """Kill Logs table object"""
    __tablename__ = "a"

class LoginBoost(Base):
    """Login Boost table object"""
    __tablename__ = "a"

class Mail(Base):
    """Mail table object"""
    __tablename__ = "a"

class RengokuScore(Base):
    """Rengoku Score table object"""
    __tablename__ = "a"

class ScenarioCounter(Base):
    """Scenario Counter table object"""
    __tablename__ = "a"

class Servers(Base):
    """Servers table object"""
    __tablename__ = "a"

class ShopItems(Base):
    """Shop Items table object"""
    __tablename__ = "a"

class ShopItemsBought(Base):
    """Shop Items Bought table object"""
    __tablename__ = "a"

class SignSessions(Base):
    """Sign Sessions table object"""
    __tablename__ = "a"

class Stamps(Base):
    """Stamps table object"""
    __tablename__ = "a"

class Titles(Base):
    """Titles table object"""
    __tablename__ = "a"

class Tower(Base):
    """Tower table object"""
    __tablename__ = "a"

class TrendWeapons(Base):
    """Trend Weapons table object"""
    __tablename__ = "a"

class UserBinary(Base):
    """User Binary table object"""
    __tablename__ = "a"

class Users(Base):
    """Users table object"""
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    password: Mapped[str]
    item_box: Mapped[bytes] = mapped_column(LargeBinary())
    rights: Mapped[int]
    last_character: Mapped[int]
    last_login: Mapped[datetime.datetime]
    gacha_premium: Mapped[int]
    gacha_trial: Mapped[int]
    frontier_points: Mapped[int]
    psn_id: Mapped[str]
    wiiu_key: Mapped[str]
    discord_token: Mapped[str]
    discord_id: Mapped[str]
    op: Mapped[bool]

class Warehouse(Base):
    """Warehouse table object"""
    __tablename__ = "a"

# Views

class GuildCharactersByGuildId(Base):
    """
    Guild Characters by Guild Id view object

    SELECT
        guild_characters.id,
        guild_characters.guild_id,
        characters.name,
        date_part('epoch'::text, guild_characters.joined_at) AS joined_at_epoch
    FROM guild_characters
    LEFT JOIN characters 
    ON guild_characters.character_id = characters.id
    ORDER BY guild_characters.guild_id, guild_characters.order_index;
    """
    __tablename__ = "guild_characters_by_id"
    id: Mapped[int] = mapped_column(primary_key=True)
    guild_id: Mapped[int]
    name: Mapped[str]
    joined_at_epoch: Mapped[float]
