"""Deterministic food checker service.

Provides rule-based ingredient screening against saved user allergens.

Design & Matching Limitations:
- Deterministic keyword and alias matching: Ingredients are evaluated using case-insensitive,
  trimmed exact matches and word-boundary matching (e.g., 'peanut' matching 'roasted peanuts'
  or 'groundnut' matching alias 'groundnut').
- Conservative matching: Substring searching is constrained to word boundaries to minimize false positives
  (such as 'nut' matching 'donut' or 'minute').
- Incomplete coverage: Simple keyword comparison cannot detect chemical derivatives, unlisted allergen
  families, manufacturer misspellings, unannounced recipe changes, or physical cross-contamination.
- Development-only: No AI semantic reasoning or clinical diagnostics are performed.
"""
import re
from typing import List

from app.models.allergy import Allergy
from app.schemas.food_check import AllergenMatch, FoodCheckResponse

SAFETY_DISCLAIMER = (
    "This food check is an automated screening tool and does not constitute medical advice, "
    "a clinical diagnosis, or a safety guarantee. A result of 'no_listed_allergen_identified' "
    "does NOT establish that the food is safe to consume. Incomplete manufacturer labels, "
    "alternative synonyms, chemical derivatives, manufacturing facility contamination, and "
    "kitchen cross-contact can cause allergens to be omitted or undetected. Always verify physical "
    "product packaging and consult a certified healthcare professional."
)


def normalize_text(text: str) -> str:
    """Normalize text by stripping whitespace and converting to lowercase."""
    return text.strip().lower()


def term_matches_ingredient(term: str, ingredient: str) -> bool:
    """
    Check if a normalized allergen term matches an ingredient.

    Matching rules:
    1. Exact normalized match: e.g. 'groundnut' == 'groundnut'.
    2. Word boundary match with optional plural suffix:
       e.g. 'peanut' matches 'roasted peanuts' or 'peanut butter'.
    """
    norm_term = normalize_text(term)
    norm_ing = normalize_text(ingredient)

    if not norm_term or not norm_ing:
        return False

    # 1. Exact match
    if norm_term == norm_ing:
        return True

    # 2. Word boundary match with optional plural 's' or 'es'
    escaped_term = re.escape(norm_term)
    pattern = rf"\b{escaped_term}(?:e?s)?\b"
    if re.search(pattern, norm_ing):
        return True

    return False


def check_food_for_allergens(
    food_name: str,
    user_id: int,
    raw_ingredients: List[str],
    user_allergies: List[Allergy],
) -> FoodCheckResponse:
    """
    Screen supplied ingredients against the user's saved allergies.
    """
    # Clean ingredients list (ignore null, empty, or whitespace-only strings)
    clean_ingredients = [ing.strip() for ing in raw_ingredients if ing and ing.strip()]

    # Case 1: Missing or empty ingredients list -> unable_to_verify
    if not clean_ingredients:
        return FoodCheckResponse(
            food_name=food_name.strip(),
            user_id=user_id,
            status="unable_to_verify",
            message="No valid ingredients were provided for verification.",
            detected_allergens=[],
            detected_ingredients=[],
            matches=[],
            disclaimer=SAFETY_DISCLAIMER,
        )

    matches: List[AllergenMatch] = []
    detected_allergens_set = set()
    detected_ingredients_set = set()

    for ingredient in clean_ingredients:
        for allergy in user_allergies:
            matched_term = None

            # Test primary allergen name
            if term_matches_ingredient(allergy.allergen_name, ingredient):
                matched_term = allergy.allergen_name
            else:
                # Test configured aliases
                if allergy.aliases and isinstance(allergy.aliases, list):
                    for alias in allergy.aliases:
                        if isinstance(alias, str) and term_matches_ingredient(alias, ingredient):
                            matched_term = alias
                            break

            if matched_term:
                matches.append(
                    AllergenMatch(
                        allergen_name=allergy.allergen_name,
                        category=allergy.category,
                        matched_ingredient=ingredient,
                        matched_term=matched_term,
                    )
                )
                detected_allergens_set.add(allergy.allergen_name)
                detected_ingredients_set.add(ingredient)

    # Case 2: One or more allergens detected
    if matches:
        return FoodCheckResponse(
            food_name=food_name.strip(),
            user_id=user_id,
            status="potential_allergen_detected",
            message="Potential allergen(s) detected in the provided ingredients list.",
            detected_allergens=sorted(list(detected_allergens_set)),
            detected_ingredients=sorted(list(detected_ingredients_set)),
            matches=matches,
            disclaimer=SAFETY_DISCLAIMER,
        )

    # Case 3: No saved allergens identified in the ingredients list
    return FoodCheckResponse(
        food_name=food_name.strip(),
        user_id=user_id,
        status="no_listed_allergen_identified",
        message=(
            "No saved user allergens were detected in the provided ingredient list. "
            "Please note that this does not establish or guarantee that the food is safe."
        ),
        detected_allergens=[],
        detected_ingredients=[],
        matches=[],
        disclaimer=SAFETY_DISCLAIMER,
    )
