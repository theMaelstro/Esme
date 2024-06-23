"""
Converter functions for numeric datatypes.
"""
def get_weapon_type(weapon_type: int):
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
