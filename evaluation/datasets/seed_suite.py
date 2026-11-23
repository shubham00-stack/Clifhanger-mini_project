"""Seed benchmark dataset suite with Weak, Moderate, and Strong narrative endings."""

from typing import Any, Dict, List
from packages.schemas.enums import ScoreBand, CliffhangerType


SEED_BENCHMARK_SUITE: List[Dict[str, Any]] = [
    # ==================== WEAK ENDINGS ====================
    {
        "id": "weak_01_domestic_routine",
        "title": "The Sunday Morning Routine",
        "genre": "slice_of_life",
        "target_level": "weak",
        "story_text": (
            "Arthur woke at seven as usual. The autumn rain was tapping gently on the bedroom window. "
            "He slipped on his woolen slippers and went downstairs to brew a fresh pot of Earl Grey tea. "
            "The morning paper lay on the welcome mat, damp at the corners. He folded it neatly, placed it "
            "beside his favorite teacup, and wondered if he should rake the lawn this afternoon or leave it until Tuesday."
        ),
        "ending_segment": (
            "He folded it neatly, placed it beside his favorite teacup, and wondered if he should rake the lawn "
            "this afternoon or leave it until Tuesday."
        ),
        "ground_truth_dimensions": {
            "unresolved_question": 25.0,
            "stakes": 15.0,
            "emotional_intensity": 20.0,
            "character_consequence": 15.0,
            "surprise": 10.0,
            "urgency": 10.0,
            "causal_setup": 60.0,
            "information_gap": 15.0,
            "originality": 20.0,
        },
        "expected_final_score": 21.0,
        "expected_score_band": ScoreBand.NO_MEANINGFUL,
        "expected_taxonomy": [CliffhangerType.RELATIONSHIP.value],
        "verified_quotes": [
            "wondered if he should rake the lawn this afternoon or leave it until Tuesday."
        ],
    },
    {
        "id": "weak_02_resolved_departure",
        "title": "The Boarded Train",
        "genre": "drama",
        "target_level": "weak",
        "story_text": (
            "Claire checked her ticket twice at Platform 4. All the luggage had been safely stowed in the overhead rack. "
            "Her brother stood on the platform, giving a small thumbs up through the double glass. "
            "The whistle blew twice, the diesel engine purred to life, and the train slowly pulled away from the station. "
            "Claire leaned her head against the headrest, closed her eyes, and prepared for a peaceful four-hour ride."
        ),
        "ending_segment": (
            "Claire leaned her head against the headrest, closed her eyes, and prepared for a peaceful four-hour ride."
        ),
        "ground_truth_dimensions": {
            "unresolved_question": 35.0,
            "stakes": 25.0,
            "emotional_intensity": 30.0,
            "character_consequence": 25.0,
            "surprise": 20.0,
            "urgency": 15.0,
            "causal_setup": 70.0,
            "information_gap": 20.0,
            "originality": 25.0,
        },
        "expected_final_score": 31.0,
        "expected_score_band": ScoreBand.WEAK,
        "expected_taxonomy": [CliffhangerType.RELATIONSHIP.value],
        "verified_quotes": [
            "closed her eyes, and prepared for a peaceful four-hour ride."
        ],
    },
    {
        "id": "weak_03_completed_assignment",
        "title": "The Signed Ledger",
        "genre": "historical",
        "target_level": "weak",
        "story_text": (
            "Master Aldous reviewed the tax ledger one final time. Every bushel of wheat was accounted for, "
            "and every tenant's tithe stamped in wax. He dipped his quill into the dark ink, applied his flourish "
            "to the bottom parchment, and blew gently to dry the seal. He blew out the candle and went to bed."
        ),
        "ending_segment": (
            "He blew out the candle and went to bed."
        ),
        "ground_truth_dimensions": {
            "unresolved_question": 20.0,
            "stakes": 20.0,
            "emotional_intensity": 15.0,
            "character_consequence": 15.0,
            "surprise": 15.0,
            "urgency": 10.0,
            "causal_setup": 75.0,
            "information_gap": 10.0,
            "originality": 20.0,
        },
        "expected_final_score": 23.25,
        "expected_score_band": ScoreBand.NO_MEANINGFUL,
        "expected_taxonomy": [CliffhangerType.MISSION.value],
        "verified_quotes": [
            "He blew out the candle and went to bed."
        ],
    },

    # ==================== MODERATE ENDINGS ====================
    {
        "id": "mod_01_the_unmarked_envelope",
        "title": "The Unmarked Envelope",
        "genre": "mystery",
        "target_level": "moderate",
        "story_text": (
            "Detective Miller returned to his desk after three hours in the records archive. "
            "The precinct floor was half empty, the fluorescent lights buzzing with low fatigue. "
            "Resting directly on his keyboard was a thick manila envelope bearing no postmark or stamp. "
            "Inside lay a glossy photograph of his own townhouse taken yesterday at dawn, alongside a hotel room key."
        ),
        "ending_segment": (
            "Inside lay a glossy photograph of his own townhouse taken yesterday at dawn, alongside a hotel room key."
        ),
        "ground_truth_dimensions": {
            "unresolved_question": 65.0,
            "stakes": 55.0,
            "emotional_intensity": 58.0,
            "character_consequence": 55.0,
            "surprise": 60.0,
            "urgency": 52.0,
            "causal_setup": 68.0,
            "information_gap": 62.0,
            "originality": 50.0,
        },
        "expected_final_score": 59.25,
        "expected_score_band": ScoreBand.MODERATE,
        "expected_taxonomy": [CliffhangerType.MYSTERY.value, CliffhangerType.THREAT.value],
        "verified_quotes": [
            "Inside lay a glossy photograph of his own townhouse taken yesterday at dawn, alongside a hotel room key."
        ],
    },
    {
        "id": "mod_02_eavesdropped_warning",
        "title": "Behind the Velvet Curtain",
        "genre": "political_drama",
        "target_level": "moderate",
        "story_text": (
            "Senator Vance excused herself from the dinner gala to take a call in the library. "
            "Before reaching her phone, she heard muffled voices from behind the partition. "
            "'Tomorrow's vote will proceed as planned,' Minister Hayes whispered coldly, 'and Senator Vance "
            "will find that her subcommittee chairmanship has already been vacated.'"
        ),
        "ending_segment": (
            "'Tomorrow's vote will proceed as planned,' Minister Hayes whispered coldly, 'and Senator Vance will find that her subcommittee chairmanship has already been vacated.'"
        ),
        "ground_truth_dimensions": {
            "unresolved_question": 62.0,
            "stakes": 58.0,
            "emotional_intensity": 55.0,
            "character_consequence": 62.0,
            "surprise": 58.0,
            "urgency": 56.0,
            "causal_setup": 65.0,
            "information_gap": 60.0,
            "originality": 52.0,
        },
        "expected_final_score": 59.35,
        "expected_score_band": ScoreBand.MODERATE,
        "expected_taxonomy": [CliffhangerType.REVELATION.value, CliffhangerType.REVERSAL.value],
        "verified_quotes": [
            "Senator Vance will find that her subcommittee chairmanship has already been vacated."
        ],
    },
    {
        "id": "mod_03_strange_frequency",
        "title": "Substation 9",
        "genre": "sci_fi",
        "target_level": "moderate",
        "story_text": (
            "Technician Aris logged the nightly telemetry for the deep satellite array. "
            "Just as she scheduled the automated backup, channel 14 flared with unexpected carrier waves. "
            "A synthetic harmonic tone looped three times, followed by coordinates pointing directly to the observatory's perimeter fence."
        ),
        "ending_segment": (
            "A synthetic harmonic tone looped three times, followed by coordinates pointing directly to the observatory's perimeter fence."
        ),
        "ground_truth_dimensions": {
            "unresolved_question": 66.0,
            "stakes": 50.0,
            "emotional_intensity": 54.0,
            "character_consequence": 48.0,
            "surprise": 58.0,
            "urgency": 50.0,
            "causal_setup": 62.0,
            "information_gap": 64.0,
            "originality": 55.0,
        },
        "expected_final_score": 56.7,
        "expected_score_band": ScoreBand.MODERATE,
        "expected_taxonomy": [CliffhangerType.MYSTERY.value],
        "verified_quotes": [
            "A synthetic harmonic tone looped three times, followed by coordinates pointing directly to the observatory's perimeter fence."
        ],
    },

    # ==================== STRONG ENDINGS ====================
    {
        "id": "str_01_the_ticking_fail_safe",
        "title": "Containment Breach at Cryo-Lab 4",
        "genre": "techno_thriller",
        "target_level": "strong",
        "story_text": (
            "Dr. Marcus Kane reached the bio-vault emergency console with his hands shaking in chemical burns. "
            "Behind him, the reinforced blast glass began spider-webbing under hydraulic pressure. "
            "He slotted the master override key, but the screen turned crimson. The automated defense voice echoed: "
            "'Primary quarantine breached. Complete thermal purge initiated. T-minus ten seconds. Escape pods jettisoned.'"
        ),
        "ending_segment": (
            "'Primary quarantine breached. Complete thermal purge initiated. T-minus ten seconds. Escape pods jettisoned.'"
        ),
        "ground_truth_dimensions": {
            "unresolved_question": 88.0,
            "stakes": 92.0,
            "emotional_intensity": 90.0,
            "character_consequence": 85.0,
            "surprise": 80.0,
            "urgency": 95.0,
            "causal_setup": 86.0,
            "information_gap": 75.0,
            "originality": 78.0,
        },
        "expected_final_score": 87.2,
        "expected_score_band": ScoreBand.VERY_STRONG,
        "expected_taxonomy": [CliffhangerType.THREAT.value, CliffhangerType.COUNTDOWN.value],
        "verified_quotes": [
            "Complete thermal purge initiated. T-minus ten seconds. Escape pods jettisoned."
        ],
    },
    {
        "id": "str_02_the_unmasking_betrayal",
        "title": "The Cipher Protocol",
        "genre": "spy_thriller",
        "target_level": "strong",
        "story_text": (
            "Agent Sarah Vance cornered the rogue syndicate courier on the catwalk above the turbine hall. "
            "'Step away from the control matrix!' she shouted, drawing her sidearm. "
            "The courier paused, lowered the ballistic hood, and turned around slowly. "
            "Standing in front of her was Director Holloway—her mentor and the man who had ordered the raid."
        ),
        "ending_segment": (
            "Standing in front of her was Director Holloway—her mentor and the man who had ordered the raid."
        ),
        "ground_truth_dimensions": {
            "unresolved_question": 90.0,
            "stakes": 88.0,
            "emotional_intensity": 88.0,
            "character_consequence": 92.0,
            "surprise": 95.0,
            "urgency": 82.0,
            "causal_setup": 85.0,
            "information_gap": 80.0,
            "originality": 82.0,
        },
        "expected_final_score": 88.4,
        "expected_score_band": ScoreBand.VERY_STRONG,
        "expected_taxonomy": [CliffhangerType.IDENTITY.value, CliffhangerType.REVELATION.value, CliffhangerType.MORAL.value],
        "verified_quotes": [
            "Standing in front of her was Director Holloway—her mentor and the man who had ordered the raid."
        ],
    },
    {
        "id": "str_03_the_irreversible_choice",
        "title": "Orbital Descent",
        "genre": "sci_fi_thriller",
        "target_level": "strong",
        "story_text": (
            "Captain Cole gripped the damaged thruster controls as the atmospheric descent angle sharpened to critical. "
            "The onboard flight computer flashed a binary ultimatum on the HUD: "
            "Reroute emergency auxiliary power to shield the colony below from the falling reactor core, or reserve thrusters "
            "to save the three crew members in the command module. There was five seconds before reentry blackout."
        ),
        "ending_segment": (
            "There was five seconds before reentry blackout."
        ),
        "ground_truth_dimensions": {
            "unresolved_question": 86.0,
            "stakes": 94.0,
            "emotional_intensity": 90.0,
            "character_consequence": 90.0,
            "surprise": 80.0,
            "urgency": 96.0,
            "causal_setup": 88.0,
            "information_gap": 72.0,
            "originality": 80.0,
        },
        "expected_final_score": 87.8,
        "expected_score_band": ScoreBand.VERY_STRONG,
        "expected_taxonomy": [CliffhangerType.DECISION.value, CliffhangerType.MORAL.value, CliffhangerType.THREAT.value],
        "verified_quotes": [
            "There was five seconds before reentry blackout."
        ],
    },
]
