"""Exposure assistant service.

Provides rule-based first-aid interim guidance based on reported symptoms.

Design & Safety Constraints:
- Non-diagnostic: Does not diagnose anaphylaxis or allergic disease.
- Emergency prioritization: Recognizes red-flag respiratory, airway, and cardiovascular symptoms.
- Clear medication boundaries: Epinephrine/adrenaline is highlighted as the primary intervention for
  severe allergic emergencies per patient-prescribed plans. Antihistamines are explicitly not substitutes.
- No medication dosing or vomiting induction: Never recommends medication dosages or emesis.
"""
from typing import List

from app.schemas.exposure import FirstAidGuidance

# Keywords and phrases indicative of potentially life-threatening or rapidly progressing symptoms
SEVERE_SYMPTOMS_TRIGGERS = [
    "breath",  # trouble breathing, shortness of breath, difficulty breathing
    "wheez",  # wheezing
    "stridor",
    "gasp",
    "chok",
    "throat",  # throat swelling, tight throat, swollen throat
    "tongue",  # tongue swelling, swollen tongue
    "swollen lip",
    "lip swell",
    "mouth swell",
    "collaps",  # collapse
    "faint",  # fainting, passed out
    "dizzi",  # severe dizziness
    "lightheaded",
    "loss of consciousness",
    "unconscious",
    "pass out",
    "passed out",
    "confusion",
    "cyanosis",
    "blue lip",
    "blue skin",
    "chest tight",
    "chest pain",
    "anaphyla",
    "rapidly progress",
    "rapid progression",
]

MILD_SYMPTOM_TRIGGERS = [
    "itch",
    "itchy",
    "hive",
    "hives",
    "rash",
    "tingl",
    "tingling",
    "sneeze",
    "sneezing",
    "runny nose",
    "stomach ache",
    "nausea",
]

FIRST_AID_DISCLAIMER = (
    "This guidance is general educational and first-aid information only. It is NOT a clinical diagnosis, "
    "medical evaluation, or replacement for emergency services or a certified healthcare provider. "
    "SafeBiteAI does not recommend medication doses or prescribe treatments. In any emergency, call emergency "
    "services immediately."
)


def evaluate_symptoms(symptoms: List[str]) -> FirstAidGuidance:
    """
    Evaluates reported symptoms and generates cautious, rule-based interim guidance.
    """
    cleaned_symptoms = [s.strip().lower() for s in symptoms if s and s.strip()]

    # Check for severe red-flag triggers
    is_severe = False
    for symptom in cleaned_symptoms:
        for trigger in SEVERE_SYMPTOMS_TRIGGERS:
            if trigger in symptom:
                is_severe = True
                break
        if is_severe:
            break

    # Branch 1: Severe / Rapidly progressing symptoms detected
    if is_severe:
        return FirstAidGuidance(
            urgency="EMERGENCY",
            emergency_warning=(
                "CRITICAL EMERGENCY WARNING: Potential severe allergic reaction detected. "
                "Call local emergency services immediately. In India, call 112 (or 911 / 999 / local equivalent). "
                "If the person has a prescribed epinephrine/adrenaline auto-injector (e.g. EpiPen), "
                "use it immediately according to their prescribed emergency plan. "
                "Do NOT delay emergency care to complete forms, observe symptoms, or wait for an app response."
            ),
            instructions=[
                "1. CALL EMERGENCY SERVICES IMMEDIATELY: Dial 112 in India (or your local emergency number).",
                "2. USE PRESCRIBED EPINEPHRINE: If the person has a prescribed adrenaline/epinephrine auto-injector, administer it without delay per their emergency medical plan.",
                "3. POSITION PROPERLY: Lie flat with legs raised. If breathing is difficult, sit up gently. Do NOT stand up or walk suddenly.",
                "4. DO NOT DELAY FOR ANYTHING: Immediate medical intervention is vital.",
                "5. DO NOT INDUCE VOMITING: Never attempt to induce vomiting as it can worsen airway obstruction.",
            ],
            medication_warning=(
                "IMPORTANT: Antihistamines must NEVER be used as a substitute for epinephrine in anaphylaxis. "
                "Antihistamines do not relieve airway swelling, vocal cord closure, or cardiovascular collapse."
            ),
            disclaimer=FIRST_AID_DISCLAIMER,
        )

    # Branch 2: Mild or localized symptoms reported
    if cleaned_symptoms:
        return FirstAidGuidance(
            urgency="MONITOR_CLOSELY",
            emergency_warning=None,
            instructions=[
                "1. STOP EATING IMMEDIATELY: Cease consumption of the suspected food and prevent any further exposure.",
                "2. HAVE SOMEONE STAY WITH YOU: Do not stay alone. Have an adult or companion monitor your symptoms continuously.",
                "3. WATCH CAREFULLY FOR WORSENING: Symptoms can progress rapidly. If you develop difficulty breathing, throat or tongue swelling, dizziness, or collapse, call 112 immediately and use prescribed epinephrine if available.",
                "4. CONTACT A HEALTHCARE PROFESSIONAL: Reach out to a doctor or local urgent care clinic for individualized advice and evaluation.",
                "5. DO NOT INDUCE VOMITING: Inducing vomiting can cause esophageal injury or aspiration and is unsafe.",
            ],
            medication_warning=(
                "Note: Antihistamines are not a substitute for epinephrine if a reaction progresses to a serious or systemic state. "
                "Always consult a healthcare provider before taking any medication."
            ),
            disclaimer=FIRST_AID_DISCLAIMER,
        )

    # Branch 3: No symptoms specifically listed
    return FirstAidGuidance(
        urgency="PRECAUTIONARY",
        emergency_warning=None,
        instructions=[
            "1. STOP EATING: Discontinue eating the suspected food item immediately.",
            "2. CLOSE OBSERVATION: Monitor yourself closely over the next several hours for any delayed or developing symptoms.",
            "3. SEEK IMMEDIATE CARE IF SYMPTOMS ARISE: If any symptoms emerge—particularly swelling or difficulty breathing—call 112 (India) or your local emergency number right away.",
            "4. DO NOT INDUCE VOMITING: Do not induce vomiting.",
        ],
        medication_warning=(
            "Note: Antihistamines do not replace epinephrine in serious reactions. Follow prescribed medical action plans."
        ),
        disclaimer=FIRST_AID_DISCLAIMER,
    )
