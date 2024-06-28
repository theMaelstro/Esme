"""
Converter functions for numeric datatypes.
"""
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
