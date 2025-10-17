"""
Item constants and enums based on traditional MUD item system.
Defines item types, flags, wear positions, weapon types, and damage types.
"""

from enum import IntEnum, Enum


# ============================================================================
# Item Types
# ============================================================================

class ItemType(IntEnum):
    """Item types used in the game"""
    LIGHT = 1
    SCROLL = 2
    WAND = 3
    STAFF = 4
    WEAPON = 5
    SHEARS = 6  # cloth cutting
    FILE = 7  # gem cutting/jewel crafting
    TREASURE = 8
    ARMOR = 9
    POTION = 10
    CLOTHING = 11
    FURNITURE = 12
    TRASH = 13
    # 14 missing
    CONTAINER = 15
    DYE = 16
    DRINK_CON = 17
    KEY = 18
    FOOD = 19
    MONEY = 20
    LAPIDARY = 21  # gem cutting
    BOAT = 22
    CORPSE_NPC = 23
    CORPSE_PC = 24
    FOUNTAIN = 25
    PILL = 26
    STOVE = 27
    MAP = 28
    PORTAL = 29
    WARP_STONE = 30
    ROOM_KEY = 31
    GEM = 32
    JEWELRY = 33
    # 34 is open
    PEN = 35
    PAPER = 36
    SKIN = 37  # for skinning skill
    SCRY = 38  # used for scrying
    THIEVES_TOOLS = 39  # lock picking, trap setting/disarming
    BANDAGE = 40  # bandage used for healing
    SALVE = 41  # for use in herbalism
    HERB = 42  # used for herbalism
    MINING_TOOL = 43  # used for mining
    FISH_POLE = 44  # used for fishing
    SIEVE = 45  # prospecting tool
    ALCHEMY_LAB = 46  # used for brewing
    MISSILE = 47
    PUDDLE = 48
    TRACKS = 49  # for ranger tracking
    ANVIL = 50
    LOOM = 51
    FIRE = 52
    BUILDING = 53
    TREE = 54
    BLACKSMITH_HAMMER = 55
    FIGURINE = 56
    SHIP_HELM = 57
    ALCHEMY_RECIPE = 58
    COOKING_RECIPE = 59
    BLACKSMITH_PLANS = 60
    TAILORING_PLANS = 61
    FLASK = 62
    INGREDIENT = 63
    SHOVEL = 64
    INSTRUMENT = 65
    # 66 unused
    SHEATH = 67
    PIPE = 68
    FLINT = 69  # lighting fires
    SEED = 70
    PLANT = 71
    CLAN_INVITE = 72
    CHISEL = 73
    WORKBENCH = 74
    MORTAR_PESTLE = 75
    QUIVER = 76
    SOUL = 77
    SOUL_CONTAINER = 78
    BAIT = 79
    DICE = 80
    LONG_HANDLE = 81  # deprecated
    SHORT_HANDLE = 82  # deprecated
    SHAFT = 83
    ARROW_HEAD = 84
    SOCKET_GEM = 85
    SOCKET_RUNE = 86
    UTENSIL = 87  # cooking
    LOCK = 88
    PIGMENT = 89
    # 90 missing
    TOME = 91
    SAW = 92
    FISH = 93
    SKILLET = 94
    SAUCE_PAN = 95
    BAKING_PAN = 96
    GRIDDLE = 97
    STEW_POT = 98
    STILL = 99  # make alcohol
    WAGON = 100
    HARNESS = 101
    UNUSED = 9999


# ============================================================================
# Item Extra Flags
# ============================================================================

class ItemFlag(Enum):
    """Extra flags for items - primary set"""
    GLOW = "glow"
    HUM = "hum"
    DARK = "dark"
    EMBALMED = "embalmed"
    CURSED = "cursed"
    INVIS = "invis"
    MAGIC = "magic"
    NODROP = "nodrop"
    BLESS = "bless"
    ANTI_GOOD = "anti_good"
    ANTI_EVIL = "anti_evil"
    ANTI_NEUTRAL = "anti_neutral"
    NOREMOVE = "noremove"
    INVENTORY = "inventory"  # used to make items infinite at shops
    NOPURGE = "nopurge"
    ROT_DEATH = "rot_death"
    VIS_DEATH = "vis_death"
    ROT_DAYLIGHT = "rot_daylight"
    RANDOM_ROOM = "random_room"
    NOLOCATE = "nolocate"
    MELT_DROP = "melt_drop"
    HAD_TIMER = "had_timer"
    SELL_EXTRACT = "sell_extract"
    NO_SAC = "no_sac"
    BURN_PROOF = "burn_proof"
    NOUNCURSE = "nouncurse"
    FIRE_TRAP = "fire_trap"
    GAS_TRAP = "gas_trap"
    POISON_TRAP = "poison_trap"
    DART_TRAP = "dart_trap"
    INDESTRUCTIBLE = "indestructible"
    ANTIMAGIC = "antimagic"


class ItemFlag2(Enum):
    """Extra flags for items - secondary set"""
    HIDDEN = "hidden"
    WEAR_CAST = "wear_cast"
    EPIC = "epic"
    LEGENDARY = "legendary"
    ARTIFACT = "artifact"
    QUEST_ITEM = "quest_item"
    CAN_PUSH = "can_push"
    CAN_PULL = "can_pull"
    CAN_PRY = "can_pry"
    CAN_PRESS = "can_press"
    BUOYANT = "buoyant"
    SPIKED = "spiked"  # Shields
    OBSCURE = "obscure"
    UNIQUE = "unique"  # Cannot be loaded more than once per reboot
    SHOCK_TRAP = "shock_trap"
    WATERPROOF = "waterproof"
    RUSTED = "rusted"
    NO_RECHARGE = "no_recharge"
    PHYLACTORY = "phylactory"  # Liches
    HARDSTAFF = "hardstaff"  # Fireproof and Acidproof
    SHILLELAGH = "shillelagh"  # Druid weapon enchant
    KEEP_DEATH = "keep_death"
    MIRROR = "mirror"
    CLAN_ITEM = "clan_item"
    FUNERAL_RITES = "funeral_rites"


# ============================================================================
# Wear Flags / Equipment Slots
# ============================================================================

class WearFlag(Enum):
    """Wear flags - where items can be equipped"""
    TAKE = "take"
    FINGER = "finger"
    NECK = "neck"
    CHEST = "chest"
    HEAD = "head"
    LEGS = "legs"
    FEET = "feet"
    HANDS = "hands"
    ARMS = "arms"
    SHIELD = "shield"
    SHOULDERS = "shoulders"
    WAIST = "waist"
    WRIST = "wrist"
    WIELD = "wield"
    HOLD = "hold"
    FLOAT = "float"
    TAIL = "tail"
    SHEATH = "sheath"
    EAR = "ear"
    QUIVER = "quiver"
    TWO_HANDED = "two_handed"


# ============================================================================
# Weapon Types
# ============================================================================

class WeaponType(IntEnum):
    """Weapon type classification"""
    SHORT_SWORD = 0
    DAGGER = 1
    SPEAR = 2
    MACE = 3
    AXE = 4
    FLAIL = 5
    WHIP = 6
    POLEARM = 7
    BOW = 8
    CROSSBOW = 9
    STAFF = 10
    LONG_SWORD = 11
    FIST_WEAPON = 12
    ARROW = 13


class InstrumentType(IntEnum):
    """Instrument types"""
    WOODWIND = 0
    BRASS = 1
    STRINGED = 2
    PERCUSSION = 3


# ============================================================================
# Weapon Flags / Special Abilities
# ============================================================================

class WeaponFlag(Enum):
    """Special weapon properties and damage types"""
    FLAMING = "flaming"
    FROST = "frost"
    VAMPIRIC = "vampiric"
    SHARP = "sharp"
    VORPAL = "vorpal"
    LIFEBLOOM = "lifebloom"
    SHOCKING = "shocking"
    POISON = "poison"
    LIGHT_DAM = "light_dam"
    NEGATIVE_DAM = "negative_dam"
    FIRE_DAM = "fire_dam"
    COLD_DAM = "cold_dam"
    LIGHTNING_DAM = "lightning_dam"
    AIR_DAM = "air_dam"
    EARTH_DAM = "earth_dam"
    HOLY_DAM = "holy_dam"
    ENERGY_DAM = "energy_dam"
    WATER_DAM = "water_dam"
    ANTI_GOBLIN = "anti_goblin"
    ANTI_GIANT = "anti_giant"
    ANTI_UNDEAD = "anti_undead"
    ANTI_DRAGON = "anti_dragon"


# ============================================================================
# Damage Types
# ============================================================================

class DamageType(Enum):
    """Damage types for weapons and spells"""
    PHYSICAL = "physical"  # Base physical damage
    SLASHING = "slashing"  # Swords, axes
    PIERCING = "piercing"  # Daggers, arrows, spears
    BLUDGEONING = "bludgeoning"  # Maces, hammers, clubs
    FIRE = "fire"
    COLD = "cold"
    LIGHTNING = "lightning"
    POISON = "poison"
    ACID = "acid"
    LIGHT = "light"
    NEGATIVE = "negative"  # Necromantic
    HOLY = "holy"
    ENERGY = "energy"  # Pure magical
    AIR = "air"
    EARTH = "earth"
    WATER = "water"
    PSYCHIC = "psychic"
    SONIC = "sonic"


# ============================================================================
# Furniture Flags
# ============================================================================

class FurnitureFlag(Enum):
    """Furniture interaction flags"""
    STAND_AT = "stand_at"
    STAND_ON = "stand_on"
    STAND_IN = "stand_in"
    SIT_AT = "sit_at"
    SIT_ON = "sit_on"
    SIT_IN = "sit_in"
    REST_AT = "rest_at"
    REST_ON = "rest_on"
    REST_IN = "rest_in"
    SLEEP_AT = "sleep_at"
    SLEEP_ON = "sleep_on"
    SLEEP_IN = "sleep_in"
    PUT_AT = "put_at"
    PUT_ON = "put_on"
    PUT_IN = "put_in"
    PUT_INSIDE = "put_inside"


# ============================================================================
# Gate/Portal Flags
# ============================================================================

class GateFlag(Enum):
    """Magical gate/portal flags"""
    NORMAL_EXIT = "normal_exit"
    NOCURSE = "nocurse"
    GOWITH = "gowith"
    BUGGY = "buggy"
    RANDOM = "random"
    DIMENSIONAL_MINE = "dimensional_mine"


# ============================================================================
# Item Quality Tiers
# ============================================================================

class QualityTier(Enum):
    """Item quality tiers"""
    JUNK = "junk"
    POOR = "poor"
    COMMON = "common"
    GOOD = "good"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    ARTIFACT = "artifact"
    MYTHIC = "mythic"


# ============================================================================
# Socket Types
# ============================================================================

class SocketType(Enum):
    """Types of sockets in items"""
    GEM = "gem"
    RUNE = "rune"
    ENCHANT = "enchant"


class GemType(Enum):
    """Gem types for socketing"""
    RUBY = "ruby"  # Fire damage/resistance
    SAPPHIRE = "sapphire"  # Cold damage/resistance
    EMERALD = "emerald"  # Nature/poison
    DIAMOND = "diamond"  # Holy/light
    AMETHYST = "amethyst"  # Arcane/magic
    TOPAZ = "topaz"  # Lightning
    ONYX = "onyx"  # Negative/shadow
    PEARL = "pearl"  # Water
    CITRINE = "citrine"  # Earth
    GARNET = "garnet"  # Blood/vampiric
    OPAL = "opal"  # Multi-element
    MOONSTONE = "moonstone"  # Psychic/mental


# ============================================================================
# Material Types
# ============================================================================

class MaterialType(Enum):
    """Material types for items"""
    # Metals
    IRON = "iron"
    STEEL = "steel"
    BRONZE = "bronze"
    COPPER = "copper"
    SILVER = "silver"
    GOLD = "gold"
    MITHRIL = "mithril"
    ADAMANTINE = "adamantine"
    DARKSTEEL = "darksteel"
    OBSIDIAN = "obsidian"
    
    # Woods
    OAK = "oak"
    PINE = "pine"
    MAPLE = "maple"
    ASH = "ash"
    EBONY = "ebony"
    IRONWOOD = "ironwood"
    YEW = "yew"
    
    # Fabrics
    COTTON = "cotton"
    LINEN = "linen"
    WOOL = "wool"
    SILK = "silk"
    LEATHER = "leather"
    HIDE = "hide"
    SCALES = "scales"
    DRAGONHIDE = "dragonhide"
    
    # Magical
    ETHEREAL = "ethereal"
    CRYSTAL = "crystal"
    BONE = "bone"
    CHITIN = "chitin"


# ============================================================================
# Helper Functions
# ============================================================================

def get_weapon_base_damage_type(weapon_type: WeaponType) -> DamageType:
    """Get the base damage type for a weapon type"""
    damage_map = {
        WeaponType.SHORT_SWORD: DamageType.SLASHING,
        WeaponType.LONG_SWORD: DamageType.SLASHING,
        WeaponType.DAGGER: DamageType.PIERCING,
        WeaponType.SPEAR: DamageType.PIERCING,
        WeaponType.MACE: DamageType.BLUDGEONING,
        WeaponType.AXE: DamageType.SLASHING,
        WeaponType.FLAIL: DamageType.BLUDGEONING,
        WeaponType.WHIP: DamageType.SLASHING,
        WeaponType.POLEARM: DamageType.PIERCING,
        WeaponType.BOW: DamageType.PIERCING,
        WeaponType.CROSSBOW: DamageType.PIERCING,
        WeaponType.STAFF: DamageType.BLUDGEONING,
        WeaponType.FIST_WEAPON: DamageType.BLUDGEONING,
        WeaponType.ARROW: DamageType.PIERCING,
    }
    return damage_map.get(weapon_type, DamageType.PHYSICAL)


def get_weapon_base_speed(weapon_type: WeaponType) -> float:
    """Get the base attack speed for a weapon type (lower is faster)"""
    speed_map = {
        WeaponType.DAGGER: 0.8,
        WeaponType.SHORT_SWORD: 1.0,
        WeaponType.LONG_SWORD: 1.2,
        WeaponType.MACE: 1.1,
        WeaponType.AXE: 1.3,
        WeaponType.FLAIL: 1.4,
        WeaponType.WHIP: 0.9,
        WeaponType.SPEAR: 1.1,
        WeaponType.POLEARM: 1.5,
        WeaponType.BOW: 1.2,
        WeaponType.CROSSBOW: 1.6,
        WeaponType.STAFF: 1.3,
        WeaponType.FIST_WEAPON: 0.7,
        WeaponType.ARROW: 0.1,  # Not wielded
    }
    return speed_map.get(weapon_type, 1.0)


def get_material_weight_modifier(material: MaterialType) -> float:
    """Get the weight modifier for a material type"""
    weight_map = {
        # Metals - heavy
        MaterialType.IRON: 1.0,
        MaterialType.STEEL: 1.1,
        MaterialType.BRONZE: 1.2,
        MaterialType.COPPER: 0.9,
        MaterialType.SILVER: 1.05,
        MaterialType.GOLD: 1.9,
        MaterialType.MITHRIL: 0.5,
        MaterialType.ADAMANTINE: 0.8,
        MaterialType.DARKSTEEL: 1.3,
        MaterialType.OBSIDIAN: 0.9,
        
        # Woods - light to medium
        MaterialType.OAK: 0.5,
        MaterialType.PINE: 0.4,
        MaterialType.MAPLE: 0.5,
        MaterialType.ASH: 0.45,
        MaterialType.EBONY: 0.7,
        MaterialType.IRONWOOD: 0.8,
        MaterialType.YEW: 0.4,
        
        # Fabrics - very light
        MaterialType.COTTON: 0.1,
        MaterialType.LINEN: 0.1,
        MaterialType.WOOL: 0.15,
        MaterialType.SILK: 0.05,
        MaterialType.LEATHER: 0.3,
        MaterialType.HIDE: 0.4,
        MaterialType.SCALES: 0.6,
        MaterialType.DRAGONHIDE: 0.5,
        
        # Magical
        MaterialType.ETHEREAL: 0.01,
        MaterialType.CRYSTAL: 0.8,
        MaterialType.BONE: 0.3,
        MaterialType.CHITIN: 0.4,
    }
    return weight_map.get(material, 1.0)


def get_material_durability_modifier(material: MaterialType) -> float:
    """Get the durability modifier for a material type"""
    durability_map = {
        # Metals
        MaterialType.IRON: 1.0,
        MaterialType.STEEL: 1.3,
        MaterialType.BRONZE: 0.9,
        MaterialType.COPPER: 0.7,
        MaterialType.SILVER: 0.8,
        MaterialType.GOLD: 0.6,
        MaterialType.MITHRIL: 1.8,
        MaterialType.ADAMANTINE: 2.5,
        MaterialType.DARKSTEEL: 2.0,
        MaterialType.OBSIDIAN: 1.1,
        
        # Woods
        MaterialType.OAK: 0.8,
        MaterialType.PINE: 0.6,
        MaterialType.MAPLE: 0.7,
        MaterialType.ASH: 0.75,
        MaterialType.EBONY: 1.0,
        MaterialType.IRONWOOD: 1.2,
        MaterialType.YEW: 0.7,
        
        # Fabrics
        MaterialType.COTTON: 0.3,
        MaterialType.LINEN: 0.4,
        MaterialType.WOOL: 0.4,
        MaterialType.SILK: 0.5,
        MaterialType.LEATHER: 0.6,
        MaterialType.HIDE: 0.7,
        MaterialType.SCALES: 1.1,
        MaterialType.DRAGONHIDE: 1.5,
        
        # Magical
        MaterialType.ETHEREAL: 0.1,
        MaterialType.CRYSTAL: 0.9,
        MaterialType.BONE: 0.5,
        MaterialType.CHITIN: 0.8,
    }
    return durability_map.get(material, 1.0)

