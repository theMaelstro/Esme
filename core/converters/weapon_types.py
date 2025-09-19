"""
Converter functions for numeric datatypes.
"""
from discord import Emoji
from dataclasses import dataclass
def get_weapon_type_emoji(weapon_type: int) -> str:
    """Format weapon type emoji."""
    weapon_types = {
    0: "<:wgs:1254599178655502427>", # GS
    1: "<:whbg:1254599181604225146>", # HBG
    2: "<:wh:1254599179888758874>", # H
    3: "<:wl:1254599184951152650>", # L
    4: "<:wsns:1254599193998393416>", # SNS
    5: "<:wlbg:1254599186012442647>", #LBG
    6: "<:wdb:1254599176017412197>", #DB
    7: "<:wls:1254599492775444490>", # LS
    8: "<:whh:1254599182925430874>", # HH
    9: "<:wgl:1254599177464451194>", # GL
    10: "<:wb:1254599174616514560>", # B
    11: "<:wt:1254599495350489242>", # T
    12: "<:wsa:1254599494088261682>", # SA
    13: "<:wms:1254599189711814758>" # MS
    }
    return weapon_types[weapon_type]

def get_weapon_type_image_url(weapon_type: int) -> str:
    """Format weapon type emoji."""
    weapon_types = {
    0: "https://static.wikia.nocookie.net/monsterhunter/images/c/c2/Great_Sword_Icon_White.png/revision/latest/scale-to-width-down/30?cb=20151024184144", # GS
    1: "https://static.wikia.nocookie.net/monsterhunter/images/9/99/Heavy_Bowgun_Icon_White.png/revision/latest/scale-to-width-down/30?cb=20151024192351", # HBG
    2: "https://static.wikia.nocookie.net/monsterhunter/images/9/99/Hammer_Icon_White.png/revision/latest/scale-to-width-down/30?cb=20151024190849", # H
    3: "https://static.wikia.nocookie.net/monsterhunter/images/0/0b/Lance_Icon_White.png/revision/latest/scale-to-width-down/30?cb=20151025102605", # L
    4: "https://static.wikia.nocookie.net/monsterhunter/images/e/e5/Sword_and_Shield_Icon_White.png/revision/latest/scale-to-width-down/30?cb=20151025112102", # SNS
    5: "https://static.wikia.nocookie.net/monsterhunter/images/0/09/Light_Bowgun_Icon_White.png/revision/latest/scale-to-width-down/30?cb=20151025103728", #LBG
    6: "https://static.wikia.nocookie.net/monsterhunter/images/7/74/Dual_Blades_Icon_White.png/revision/latest/scale-to-width-down/30?cb=20151024183210", #DB
    7: "https://static.wikia.nocookie.net/monsterhunter/images/1/1e/Long_Sword_Icon_White.png/revision/latest/scale-to-width-down/30?cb=20151024170006", # LS
    8: "https://static.wikia.nocookie.net/monsterhunter/images/4/46/Hunting_Horn_Icon_White.png/revision/latest/scale-to-width-down/30?cb=20151025094318", # HH
    9: "https://static.wikia.nocookie.net/monsterhunter/images/1/17/Gunlance_Icon_White.png/revision/latest/scale-to-width-down/30?cb=20151024185913", # GL
    10: "https://static.wikia.nocookie.net/monsterhunter/images/a/a4/Bow_Icon_White.png/revision/latest/scale-to-width-down/30?cb=20151024174635", # B
    11: "https://static.wikia.nocookie.net/monsterhunter/images/e/ef/Tonfa_Icon_White.png/revision/latest/scale-to-width-down/30?cb=20140427034613", # T
    12: "https://static.wikia.nocookie.net/monsterhunter/images/4/40/Switch_Axe_Icon_White.png/revision/latest/scale-to-width-down/30?cb=20170719204530", # SA
    13: "https://static.wikia.nocookie.net/monsterhunter/images/8/81/Magnet_Spike_Icon_White.png/revision/latest/scale-to-width-down/30?cb=20180706153233" # MS
    }
    return weapon_types[weapon_type]


@dataclass
class FeatureEmoji:
    enabled: Emoji = None
    disabled: Emoji = None

@dataclass
class FeatureEmojis:
    bow: FeatureEmoji
    gunlance: FeatureEmoji
    hammer: FeatureEmoji
    hunting_horn: FeatureEmoji
    light_bowgun: FeatureEmoji
    magnet_spike: FeatureEmoji
    sword_shield: FeatureEmoji
    dual_blades: FeatureEmoji
    great_sword: FeatureEmoji
    heavy_bowgun: FeatureEmoji
    lance: FeatureEmoji
    long_sword: FeatureEmoji
    switch_axe: FeatureEmoji
    tonfa: FeatureEmoji

class ApplicationEmojis:
    def __init__(
        self,
        emojis: list[Emoji]
    ):
        my_emoji = FeatureEmojis(
            FeatureEmoji(None, None),
            FeatureEmoji(None, None),
            FeatureEmoji(None, None),
            FeatureEmoji(None, None),
            FeatureEmoji(None, None),
            FeatureEmoji(None, None),
            FeatureEmoji(None, None),
            FeatureEmoji(None, None),
            FeatureEmoji(None, None),
            FeatureEmoji(None, None),
            FeatureEmoji(None, None),
            FeatureEmoji(None, None),
            FeatureEmoji(None, None),
            FeatureEmoji(None, None)
        )
        for emoji in emojis:
            match emoji.name:
                case "bow_a":
                    my_emoji.bow.enabled = emoji
                case "gl_a":
                    my_emoji.gunlance.enabled = emoji
                case "ham_a":
                    my_emoji.hammer.enabled = emoji
                case "hh_a":
                    my_emoji.hunting_horn.enabled = emoji
                case "lbg_a":
                    my_emoji.light_bowgun.enabled = emoji
                case "ms_a":
                    my_emoji.magnet_spike.enabled = emoji
                case "sns_a":
                    my_emoji.sword_shield.enabled = emoji
                case "dnb_a":
                    my_emoji.dual_blades.enabled = emoji
                case "gs_a":
                    my_emoji.great_sword.enabled = emoji
                case "hbg_a":
                    my_emoji.heavy_bowgun.enabled = emoji
                case "lan_a":
                    my_emoji.lance.enabled = emoji
                case "ls_a":
                    my_emoji.long_sword.enabled = emoji
                case "sa_a":
                    my_emoji.switch_axe.enabled = emoji
                case "ton_a":
                    my_emoji.tonfa.enabled = emoji
                case "bow_d":
                    my_emoji.bow.disabled = emoji
                case "gl_d":
                    my_emoji.gunlance.disabled = emoji
                case "ham_d":
                    my_emoji.hammer.disabled = emoji
                case "hh_d":
                    my_emoji.hunting_horn.disabled = emoji
                case "lbg_d":
                    my_emoji.light_bowgun.disabled = emoji
                case "ms_d":
                    my_emoji.magnet_spike.disabled = emoji
                case "sns_d":
                    my_emoji.sword_shield.disabled = emoji
                case "dnb_d":
                    my_emoji.dual_blades.disabled = emoji
                case "gs_d":
                    my_emoji.great_sword.disabled = emoji
                case "hbg_d":
                    my_emoji.heavy_bowgun.disabled = emoji
                case "lan_d":
                    my_emoji.lance.disabled = emoji
                case "ls_d":
                    my_emoji.long_sword.disabled = emoji
                case "sa_d":
                    my_emoji.switch_axe.disabled = emoji
                case "ton_d":
                    my_emoji.tonfa.disabled = emoji
        self.emoji = my_emoji

    def get_bow(self, b: str):
        if b == "1":
            return self.emoji.bow.enabled
        return self.emoji.bow.disabled

    def get_gunlance(self, b: str):
        if b == "1":
            return self.emoji.gunlance.enabled
        return self.emoji.gunlance.disabled

    def get_hammer(self, b: str):
        if b == "1":
            return self.emoji.hammer.enabled
        return self.emoji.hammer.disabled

    def get_hunting_horn(self, b: str):
        if b == "1":
            return self.emoji.hunting_horn.enabled
        return self.emoji.hunting_horn.disabled

    def get_light_bowgun(self, b: str):
        if b == "1":
            return self.emoji.light_bowgun.enabled
        return self.emoji.light_bowgun.disabled

    def get_magnet_spike(self, b: str):
        if b == "1":
            return self.emoji.magnet_spike.enabled
        return self.emoji.magnet_spike.disabled

    def get_sword_shield(self, b: str):
        if b == "1":
            return self.emoji.sword_shield.enabled
        return self.emoji.sword_shield.disabled

    def get_dual_blades(self, b: str):
        if b == "1":
            return self.emoji.dual_blades.enabled
        return self.emoji.dual_blades.disabled

    def get_great_sword(self, b: str):
        if b == "1":
            return self.emoji.great_sword.enabled
        return self.emoji.great_sword.disabled

    def get_heavy_bowgun(self, b: str):
        if b == "1":
            return self.emoji.heavy_bowgun.enabled
        return self.emoji.heavy_bowgun.disabled

    def get_lance(self, b: str):
        if b == "1":
            return self.emoji.lance.enabled
        return self.emoji.lance.disabled

    def get_long_sword(self, b: str):
        if b == "1":
            return self.emoji.long_sword.enabled
        return self.emoji.long_sword.disabled

    def get_switch_axe(self, b: str):
        if b == "1":
            return self.emoji.switch_axe.enabled
        return self.emoji.switch_axe.disabled

    def get_tonfa(self, b: str):
        if b == "1":
            return self.emoji.tonfa.enabled
        return self.emoji.tonfa.disabled
