"""
recipes.py - Rule-Based Recipe Suggestion Engine
Provides deterministic, rule-based recipe recommendations using available ingredients.
Note: This is a rule-based expert heuristic system (matching criteria & urgency weighting),
NOT a trained machine learning model.
"""

from typing import Dict, List, Set


# Knowledge base of versatile recipes designed to prevent household food waste
RECIPE_DATABASE = [
    {
        "id": "rec_01",
        "title": "Quick Garden Veggie Omelet",
        "category": "Breakfast & Quick Meals",
        "required_ingredients": ["egg"],
        "optional_ingredients": ["spinach", "cheese", "milk", "tomato", "ham", "avocado"],
        "time": "10 mins",
        "difficulty": "Easy",
        "waste_tip": "Omelets are the ultimate fridge-cleaner. Wilted greens and leftover cheese crusts melt perfectly.",
        "instructions": [
            "Whisk 2-3 eggs with a splash of milk, salt, and pepper in a bowl.",
            "Heat a pan with a drop of butter or oil over medium heat.",
            "Sauté spinach or diced vegetables for 1-2 minutes until tender.",
            "Pour the whisked eggs evenly over the pan.",
            "Sprinkle shredded cheese on top, fold the omelet in half, and serve hot.",
        ],
    },
    {
        "id": "rec_02",
        "title": "Rescue Green Smoothie Bowl",
        "category": "Breakfast & Drinks",
        "required_ingredients": ["spinach", "milk"],
        "optional_ingredients": ["banana", "yogurt", "avocado", "apple", "strawberries"],
        "time": "5 mins",
        "difficulty": "Very Easy",
        "waste_tip": "Blend softening fruits and delicate greens before they brown or wilt.",
        "instructions": [
            "Wash and add a handful of spinach into the blender.",
            "Add milk (or yogurt) along with your available fruits (banana, avocado, or berries).",
            "Blend on high speed until completely smooth and creamy.",
            "Pour into a bowl or tall glass and enjoy immediately.",
        ],
    },
    {
        "id": "rec_03",
        "title": "Savory Fridge-Cleanout Fried Rice",
        "category": "Lunch & Dinner",
        "required_ingredients": ["rice", "egg"],
        "optional_ingredients": ["carrots", "spinach", "chicken", "ham", "soy sauce", "garlic"],
        "time": "15 mins",
        "difficulty": "Easy",
        "waste_tip": "Day-old chilled rice fries significantly better than fresh rice without getting soggy.",
        "instructions": [
            "Heat oil in a wok or large frying pan over medium-high heat.",
            "Scramble the eggs quickly and set them aside.",
            "Sauté diced carrots, leftover meats, or vegetables until tender-crisp.",
            "Add cold cooked rice, breaking up any clumps with a spatula.",
            "Toss everything together with soy sauce and return the scrambled eggs.",
        ],
    },
    {
        "id": "rec_04",
        "title": "Creamy Avocado & Egg Toast",
        "category": "Breakfast & Snacks",
        "required_ingredients": ["avocado", "bread"],
        "optional_ingredients": ["egg", "cheese", "tomato", "spinach"],
        "time": "8 mins",
        "difficulty": "Very Easy",
        "waste_tip": "Fully ripe avocados must be used within 1-2 days to avoid browning and flavor loss.",
        "instructions": [
            "Toast bread slices until golden brown and crispy.",
            "Scoop out the avocado flesh and mash in a bowl with a pinch of salt, pepper, and lemon juice if available.",
            "Optionally fry or poach an egg.",
            "Spread mashed avocado generously over warm toast and crown with the egg or sliced cheese.",
        ],
    },
    {
        "id": "rec_05",
        "title": "Hearty Farmer's Vegetable Frittata",
        "category": "Brunch & Dinner",
        "required_ingredients": ["egg", "potatoes"],
        "optional_ingredients": ["spinach", "cheese", "milk", "carrots", "ham"],
        "time": "25 mins",
        "difficulty": "Medium",
        "waste_tip": "Frittatas bake easily in one pan and hold up well in the fridge for up to 3 days.",
        "instructions": [
            "Thinly slice potatoes and lightly parboil or pan-fry them until softened.",
            "Whisk 5-6 eggs with a splash of milk, shredded cheese, salt, and herbs.",
            "Layer the cooked potatoes, spinach, and ham in an oven-safe skillet.",
            "Pour egg mixture over the ingredients.",
            "Cook over low heat for 5 minutes, then bake or broil until golden and set.",
        ],
    },
    {
        "id": "rec_06",
        "title": "Golden Melty Grilled Cheese Toastie",
        "category": "Lunch & Snacks",
        "required_ingredients": ["bread", "cheese"],
        "optional_ingredients": ["ham", "spinach", "tomato", "avocado"],
        "time": "10 mins",
        "difficulty": "Very Easy",
        "waste_tip": "Dry or slightly stale bread crisps up into the crispest grilled sandwiches.",
        "instructions": [
            "Lightly butter the outer sides of two bread slices.",
            "Place cheddar or your available cheese slices between the bread.",
            "Add optional fillings like ham slices or baby spinach leaves.",
            "Grill on a skillet over medium-low heat until bread is golden and cheese is molten.",
        ],
    },
    {
        "id": "rec_07",
        "title": "Comforting Chicken & Veggie Skillet",
        "category": "Dinner",
        "required_ingredients": ["chicken"],
        "optional_ingredients": ["carrots", "potatoes", "spinach", "rice", "garlic"],
        "time": "25 mins",
        "difficulty": "Medium",
        "waste_tip": "Raw poultry should always be prioritized first when nearing its expiry date.",
        "instructions": [
            "Cut chicken breast into bite-sized cubes and season with salt and pepper.",
            "Sear chicken in a hot skillet with olive oil until golden on all sides.",
            "Add diced carrots and potatoes with a splash of water, cover, and steam until tender.",
            "Stir in spinach during the final 2 minutes until wilted.",
            "Serve on its own or over warm cooked rice.",
        ],
    },
    {
        "id": "rec_08",
        "title": "Creamy Berry Yogurt Parfait",
        "category": "Breakfast & Dessert",
        "required_ingredients": ["yogurt"],
        "optional_ingredients": ["strawberries", "banana", "apple", "bread"],
        "time": "5 mins",
        "difficulty": "Very Easy",
        "waste_tip": "Yogurt nearing its date makes refreshing parfaits, salad dressings, or marinades.",
        "instructions": [
            "Spoon a generous layer of Greek yogurt into a glass or bowl.",
            "Slice fresh strawberries or other ripe fruits.",
            "Layer alternating fruit slices and yogurt.",
            "Optionally garnish with toasted breadcrumbs, granola, or nuts for crunch.",
        ],
    },
    {
        "id": "rec_09",
        "title": "Rustic Root Vegetable Soup",
        "category": "Soups & Warm Bowls",
        "required_ingredients": ["carrots", "potatoes"],
        "optional_ingredients": ["spinach", "chicken", "rice", "garlic"],
        "time": "30 mins",
        "difficulty": "Easy",
        "waste_tip": "Simmering root vegetables softens slightly bendy carrots and older potatoes wonderfully.",
        "instructions": [
            "Chop carrots and potatoes into bite-sized cubes.",
            "Sauté in a pot with a touch of oil until fragrant.",
            "Add vegetable or chicken stock (or water with salt) and bring to a gentle boil.",
            "Simmer for 20 minutes until root vegetables are tender.",
            "Stir in spinach leaves right before turning off the heat, season and serve.",
        ],
    },
    {
        "id": "rec_10",
        "title": "Classic Cinnamon French Toast",
        "category": "Breakfast & Brunch",
        "required_ingredients": ["bread", "egg", "milk"],
        "optional_ingredients": ["strawberries", "banana", "apple", "yogurt"],
        "time": "12 mins",
        "difficulty": "Easy",
        "waste_tip": "French toast was invented specifically to revive dry, stale bread by soaking it in custard.",
        "instructions": [
            "Whisk eggs, milk, a dash of sugar, and cinnamon in a shallow bowl.",
            "Dip bread slices on both sides until thoroughly soaked with custard.",
            "Cook in a hot buttered pan for 2-3 minutes per side until puffed and golden brown.",
            "Serve topped with fresh sliced fruit, yogurt, or honey.",
        ],
    },
    {
        "id": "rec_11",
        "title": "Crispy Golden Hash Browns",
        "category": "Breakfast & Sides",
        "required_ingredients": ["potatoes"],
        "optional_ingredients": ["cheese", "egg", "ham"],
        "time": "15 mins",
        "difficulty": "Easy",
        "waste_tip": "Grate older potatoes and squeeze out excess moisture for maximum crispiness.",
        "instructions": [
            "Peel and coarsely grate potatoes.",
            "Squeeze grated potatoes tightly in a clean towel to remove excess starch and moisture.",
            "Press into a hot oiled skillet in an even layer.",
            "Fry until deeply golden and crispy on the bottom, flip, and finish the other side.",
            "Top with melted cheddar cheese if desired.",
        ],
    },
    {
        "id": "rec_12",
        "title": "Fresh Garden Chopped Salad",
        "category": "Salads & Sides",
        "required_ingredients": ["spinach"],
        "optional_ingredients": ["avocado", "cheese", "strawberries", "apple", "carrots", "egg"],
        "time": "8 mins",
        "difficulty": "Very Easy",
        "waste_tip": "Crisp up slightly wilted salad leaves by soaking them in ice-cold water for 5 minutes.",
        "instructions": [
            "Wash and gently dry spinach leaves.",
            "Slice available fruits (apples, strawberries, or avocado) and vegetables.",
            "Cube or crumble cheddar cheese on top.",
            "Toss with olive oil, lemon juice, or yogurt dressing, and serve immediately.",
        ],
    },
]


def _normalize_ingredient_name(text: str) -> str:
    """Helper to standardize ingredient names for substring & keyword matching."""
    return text.strip().lower()


def _is_ingredient_present(target_keyword: str, inventory_names: Set[str]) -> bool:
    """
    Checks if a target ingredient keyword exists in the user's inventory names.
    Handles singular/plural variations and compound names.
    Examples:
      target 'egg' matches 'Brown Eggs' or 'Egg'
      target 'spinach' matches 'Fresh Spinach'
      target 'milk' matches 'Whole Milk' or 'Oat Milk'
      target 'potato' matches 'Potatoes'
    """
    target = target_keyword.lower()
    for item_name in inventory_names:
        item = item_name.lower()
        if target in item:
            return True
        # Check plural/singular variations
        if target.endswith("s") and target[:-1] in item:
            return True
        if item.endswith("s") and target in item[:-1]:
            return True
        if target == "potatoes" and "potato" in item:
            return True
        if target == "potato" and "potatoes" in item:
            return True
        if target == "strawberries" and "strawberry" in item:
            return True
        if target == "tomatoes" and "tomato" in item:
            return True
    return False


def get_rule_based_recipe_suggestions(
    active_items: List[Dict],
    prioritize_urgent: bool = True,
    min_match_ratio: float = 0.3,
) -> List[Dict]:
    """
    Rule-Based Expert Engine for Recipe Recommendations:
    1. Extracts available active ingredients and notes their freshness status.
    2. Matches each recipe's required and optional ingredient lists against inventory.
    3. Calculates an ingredient match percentage:
         Match % = (matched_core / total_core) * 80% + (matched_optional / total_optional) * 20%
    4. Weights recipes that rescue 'Urgent' or 'Use Soon' ingredients higher.
    5. Returns ranked list with clear reasoning and missing ingredient checklists.
    """
    if not active_items:
        return []

    # Map inventory items: name -> status_label
    inventory_dict = {}
    urgent_keywords = set()
    use_soon_keywords = set()

    for item in active_items:
        clean_name = item["name"].strip()
        inventory_dict[clean_name] = item.get("status_label", "Fresh")
        
        # Track items in urgent or use-soon condition
        if item.get("status_label") == "Urgent":
            urgent_keywords.add(clean_name.lower())
        elif item.get("status_label") == "Use Soon":
            use_soon_keywords.add(clean_name.lower())

    inventory_names = set(inventory_dict.keys())

    suggestions = []

    for recipe in RECIPE_DATABASE:
        required = recipe["required_ingredients"]
        optional = recipe["optional_ingredients"]

        # Check required ingredients
        matched_required = []
        missing_required = []
        for req in required:
            if _is_ingredient_present(req, inventory_names):
                matched_required.append(req.title())
            else:
                missing_required.append(req.title())

        # Check optional ingredients
        matched_optional = []
        missing_optional = []
        for opt in optional:
            if _is_ingredient_present(opt, inventory_names):
                matched_optional.append(opt.title())
            else:
                missing_optional.append(opt.title())

        req_ratio = len(matched_required) / len(required) if required else 1.0
        opt_ratio = len(matched_optional) / len(optional) if optional else 0.0
        
        # Overall match score (0 to 100)
        match_score = int(round((req_ratio * 75) + (opt_ratio * 25)))

        # Skip recipes where essential core requirements have no match at all
        if req_ratio < min_match_ratio and match_score < 40:
            continue

        # Check which urgent/use-soon items this recipe rescues
        rescued_urgent = []
        rescued_use_soon = []

        all_matched_keywords = [m.lower() for m in matched_required + matched_optional]

        for item_name, status in inventory_dict.items():
            name_lower = item_name.lower()
            for kw in all_matched_keywords:
                if kw in name_lower or name_lower in kw:
                    if status == "Urgent" and item_name not in rescued_urgent:
                        rescued_urgent.append(item_name)
                    elif status == "Use Soon" and item_name not in rescued_use_soon:
                        rescued_use_soon.append(item_name)

        # Calculate waste rescue priority bonus
        urgency_bonus = (len(rescued_urgent) * 20) + (len(rescued_use_soon) * 10)
        final_rank_score = match_score + urgency_bonus

        suggestions.append({
            "id": recipe["id"],
            "title": recipe["title"],
            "category": recipe["category"],
            "time": recipe["time"],
            "difficulty": recipe["difficulty"],
            "waste_tip": recipe["waste_tip"],
            "instructions": recipe["instructions"],
            "match_score": min(match_score, 100),
            "final_rank_score": final_rank_score,
            "matched_required": matched_required,
            "missing_required": missing_required,
            "matched_optional": matched_optional,
            "missing_optional": missing_optional,
            "rescued_urgent": rescued_urgent,
            "rescued_use_soon": rescued_use_soon,
            "can_cook_now": len(missing_required) == 0,
        })

    # Sort results
    if prioritize_urgent:
        # Sort by urgency rescues first, then can_cook_now, then match_score
        suggestions.sort(
            key=lambda x: (
                len(x["rescued_urgent"]) > 0,
                x["can_cook_now"],
                x["final_rank_score"],
                x["match_score"],
            ),
            reverse=True,
        )
    else:
        suggestions.sort(
            key=lambda x: (x["can_cook_now"], x["match_score"]),
            reverse=True,
        )

    return suggestions
