"""
Item Enhancement System for DungeonCrawlerAI.
Provides magical enhancements for items and crafting combinations.
"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Tuple
import random

from models import Item, ItemType, ItemQuality, Hero


class ItemEnhancement(Enum):
    """Magical enhancements that can be applied to items."""
    BLESSED = "blessed"
    VOLATILE = "volatile"
    CHAINED = "chained"
    ILLUSION = "illusion"
    ANCIENT = "ancient"
    DEMONIC = "demonic"
    ETHEREAL = "ethereal"


@dataclass
class EnhancementEffect:
    """Describes the effect of an item enhancement."""
    name: str
    description: str
    value_modifier: float
    special_effect: str
    triggers_suspicion: bool
    curse_interaction: str


ENHANCEMENT_EFFECTS: Dict[ItemEnhancement, EnhancementEffect] = {
    ItemEnhancement.BLESSED: EnhancementEffect(
        name="Blessed",
        description="Divine protection increases effectiveness by 50%",
        value_modifier=1.5,
        special_effect="protected",
        triggers_suspicion=False,
        curse_interaction="Curse corruption fails - divine protection repels darkness"
    ),
    ItemEnhancement.VOLATILE: EnhancementEffect(
        name="Volatile",
        description="Unstable magic causes explosion when picked up",
        value_modifier=0.0,
        special_effect="explodes_on_pickup",
        triggers_suspicion=True,
        curse_interaction="Curse can trigger the explosion remotely"
    ),
    ItemEnhancement.CHAINED: EnhancementEffect(
        name="Chained",
        description="Corruption spreads to adjacent items automatically",
        value_modifier=1.0,
        special_effect="spreads_corruption",
        triggers_suspicion=False,
        curse_interaction="Corruption spreads to all adjacent items in inventory"
    ),
    ItemEnhancement.ILLUSION: EnhancementEffect(
        name="Illusion",
        description="Not real - disappears after pickup",
        value_modifier=0.0,
        special_effect="vanishes_on_pickup",
        triggers_suspicion=True,
        curse_interaction="Curse reveals the illusion prematurely"
    ),
    ItemEnhancement.ANCIENT: EnhancementEffect(
        name="Ancient",
        description="Incredibly valuable but attracts stronger enemies",
        value_modifier=2.0,
        special_effect="attracts_enemies",
        triggers_suspicion=False,
        curse_interaction="Ancient power resists initial corruption but eventually succumbs"
    ),
    ItemEnhancement.DEMONIC: EnhancementEffect(
        name="Demonic",
        description="Already cursed - drains 5 HP per turn while held",
        value_modifier=1.5,
        special_effect="hp_drain",
        triggers_suspicion=False,
        curse_interaction="Already cursed - no additional effect possible"
    ),
    ItemEnhancement.ETHEREAL: EnhancementEffect(
        name="Ethereal",
        description="50% chance to phase through hero's hands",
        value_modifier=1.0,
        special_effect="phase_chance",
        triggers_suspicion=False,
        curse_interaction="Curse anchors the item, preventing phasing"
    ),
}


class ItemEnhancer:
    """Handles applying and removing enhancements from items."""

    def __init__(self):
        """Initialize the item enhancer."""
        self._enhanced_items: Dict[int, ItemEnhancement] = {}

    def enhance_item(self, item: Item, enhancement: ItemEnhancement) -> Item:
        """
        Apply an enhancement to an item.

        Args:
            item: The item to enhance.
            enhancement: The enhancement to apply.

        Returns:
            The enhanced item with modified properties.
        """
        effect = ENHANCEMENT_EFFECTS[enhancement]
        item.value = int(item.original_value * effect.value_modifier)
        self._enhanced_items[id(item)] = enhancement

        if enhancement == ItemEnhancement.DEMONIC:
            item.quality = ItemQuality.CURSED

        return item

    def remove_enhancement(self, item: Item) -> Item:
        """
        Remove any enhancement from an item.

        Args:
            item: The item to remove enhancement from.

        Returns:
            The item with enhancement removed and original value restored.
        """
        if id(item) in self._enhanced_items:
            del self._enhanced_items[id(item)]
            item.value = item.original_value
        return item

    def get_enhancement(self, item: Item) -> Optional[ItemEnhancement]:
        """
        Get the current enhancement on an item.

        Args:
            item: The item to check.

        Returns:
            The enhancement if present, None otherwise.
        """
        return self._enhanced_items.get(id(item))

    def get_random_enhancement(self) -> ItemEnhancement:
        """
        Get a random enhancement type.

        Returns:
            A randomly selected ItemEnhancement.
        """
        return random.choice(list(ItemEnhancement))

    def apply_enhancement_effect(self, item: Item, hero: Hero) -> dict:
        """
        Apply the enhancement effect when an item is looted.

        Args:
            item: The looted item.
            hero: The hero looting the item.

        Returns:
            Dictionary describing what happened during looting.
        """
        enhancement = self.get_enhancement(item)
        if enhancement is None:
            return {"success": True, "effect": "none", "message": "Item looted normally"}

        effect = ENHANCEMENT_EFFECTS[enhancement]
        result = {
            "success": True,
            "effect": effect.special_effect,
            "message": "",
            "damage": 0,
            "item_kept": True
        }

        if effect.triggers_suspicion:
            hero.increase_suspicion(15)

        if enhancement == ItemEnhancement.BLESSED:
            result["message"] = "Divine light emanates from the item - it feels protected"

        elif enhancement == ItemEnhancement.VOLATILE:
            damage = 30
            hero.take_damage(damage)
            result["damage"] = damage
            result["item_kept"] = False
            result["message"] = f"The item explodes! Hero takes {damage} damage!"

        elif enhancement == ItemEnhancement.CHAINED:
            corrupted_count = 0
            for inv_item in hero.inventory:
                if inv_item.quality == ItemQuality.NORMAL:
                    inv_item.corrupt()
                    corrupted_count += 1
            result["message"] = f"Dark chains spread corruption to {corrupted_count} items!"
            result["corrupted_count"] = corrupted_count

        elif enhancement == ItemEnhancement.ILLUSION:
            result["item_kept"] = False
            result["success"] = False
            result["message"] = "The item shimmers and vanishes - it was never real!"

        elif enhancement == ItemEnhancement.ANCIENT:
            result["message"] = "Ancient power radiates from the item - enemies stir in the darkness"
            result["attracts_enemies"] = True

        elif enhancement == ItemEnhancement.DEMONIC:
            result["message"] = "Demonic energy binds to your soul - the item drains life while held"
            result["hp_drain_per_turn"] = 5

        elif enhancement == ItemEnhancement.ETHEREAL:
            if random.random() < 0.5:
                result["item_kept"] = False
                result["success"] = False
                result["message"] = "The item phases through your hands and returns to the ground!"
                result["relootable"] = True
            else:
                result["message"] = "You grasp the ethereal item firmly"

        return result

    def check_curse_interaction(self, item: Item) -> str:
        """
        Determine what happens when a curse tries to corrupt an enhanced item.

        Args:
            item: The item the curse is targeting.

        Returns:
            Description of the interaction result.
        """
        enhancement = self.get_enhancement(item)
        if enhancement is None:
            return "Item has no enhancement - curse corrupts normally"

        effect = ENHANCEMENT_EFFECTS[enhancement]
        return effect.curse_interaction


class ItemCrafting:
    """Handles item combination and crafting recipes."""

    RECIPES: Dict[Tuple[ItemType, ItemType], dict] = {
        (ItemType.WEAPON, ItemType.WEAPON): {
            "result_type": ItemType.WEAPON,
            "name": "Dual-Forged Blade",
            "value_multiplier": 1.8,
            "description": "Two weapons merged into one powerful blade"
        },
        (ItemType.ARMOR, ItemType.ARMOR): {
            "result_type": ItemType.ARMOR,
            "name": "Reinforced Platemail",
            "value_multiplier": 1.7,
            "description": "Layered armor provides superior protection"
        },
        (ItemType.HEALTH_POTION, ItemType.HEALTH_POTION): {
            "result_type": ItemType.HEALTH_POTION,
            "name": "Concentrated Elixir",
            "value_multiplier": 2.5,
            "description": "A potent healing brew"
        },
        (ItemType.WEAPON, ItemType.TREASURE): {
            "result_type": ItemType.WEAPON,
            "name": "Gilded Weapon",
            "value_multiplier": 1.5,
            "description": "A weapon adorned with precious gems"
        },
        (ItemType.ARMOR, ItemType.TREASURE): {
            "result_type": ItemType.ARMOR,
            "name": "Royal Guard Armor",
            "value_multiplier": 1.6,
            "description": "Armor fit for royalty"
        },
        (ItemType.HEALTH_POTION, ItemType.TREASURE): {
            "result_type": ItemType.HEALTH_POTION,
            "name": "Golden Elixir",
            "value_multiplier": 2.0,
            "description": "A healing potion infused with gold dust"
        },
    }

    def __init__(self):
        """Initialize the crafting system."""
        pass

    def combine_items(self, item1: Item, item2: Item) -> Optional[Item]:
        """
        Attempt to combine two items into a new item.

        Args:
            item1: First item to combine.
            item2: Second item to combine.

        Returns:
            New combined item if recipe exists, None otherwise.
        """
        if not self.can_combine(item1, item2):
            return None

        recipe = self._get_recipe(item1.item_type, item2.item_type)
        if recipe is None:
            return None

        combined_value = int((item1.original_value + item2.original_value) * recipe["value_multiplier"])

        worst_quality = ItemQuality.NORMAL
        if item1.quality == ItemQuality.CURSED or item2.quality == ItemQuality.CURSED:
            worst_quality = ItemQuality.CURSED
        elif item1.quality == ItemQuality.CORRUPTED or item2.quality == ItemQuality.CORRUPTED:
            worst_quality = ItemQuality.CORRUPTED

        new_item = Item(
            item_type=recipe["result_type"],
            name=recipe["name"],
            value=combined_value,
            quality=worst_quality
        )

        return new_item

    def get_combination_recipes(self) -> dict:
        """
        Get all available crafting recipes.

        Returns:
            Dictionary of all recipes with descriptions.
        """
        recipes = {}
        for (type1, type2), recipe in self.RECIPES.items():
            key = f"{type1.value} + {type2.value}"
            recipes[key] = {
                "result": recipe["name"],
                "result_type": recipe["result_type"].value,
                "value_multiplier": recipe["value_multiplier"],
                "description": recipe["description"]
            }
        return recipes

    def can_combine(self, item1: Item, item2: Item) -> bool:
        """
        Check if two items can be combined.

        Args:
            item1: First item to check.
            item2: Second item to check.

        Returns:
            True if a valid recipe exists for the combination.
        """
        return self._get_recipe(item1.item_type, item2.item_type) is not None

    def _get_recipe(self, type1: ItemType, type2: ItemType) -> Optional[dict]:
        """
        Get the recipe for combining two item types.

        Args:
            type1: First item type.
            type2: Second item type.

        Returns:
            Recipe dictionary if exists, None otherwise.
        """
        if (type1, type2) in self.RECIPES:
            return self.RECIPES[(type1, type2)]
        if (type2, type1) in self.RECIPES:
            return self.RECIPES[(type2, type1)]
        return None
