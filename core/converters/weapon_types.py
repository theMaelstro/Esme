"""
Converter functions for numeric datatypes.
"""
def get_weapon_type_emoji(weapon_type: int) -> str:
    """Format weapon type emoji."""
    weapon_types = {
    0: "<:Wgs:986251238750441492>", # GS
    1: "<:Whbg:986251717026926592>", # HBG
    2: "<:Whammer:986251437954727976>", # H
    3: "<:Wlance:986251511485067315>", # L
    4: "<:Wsns:986252280384876594>", # SNS
    5: "<:Wlbg:986251637146390548>", #LBG
    6: "<:Wdbs:986251366672519178>", #DB
    7: "<:Wls:986251298955472926>", # LS
    8: "<:Whh:986251970824245318>", # HH
    9: "<:Wgl:986251566795333642>", # GL
    10: "<:Wbow:986252340661194752>", # B
    11: "<:Wtonfa:986249617626787890>", # T
    12: "<:Wswaxe:986251790066515998>", # SA
    13: "<:WMS:986342634299752519>" # MS
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
