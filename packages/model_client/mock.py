"""Deterministic MockModelClient for testing and offline evaluation without external tokens."""

import hashlib
import re
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel

from .base import BaseModelClient


class MockModelClient(BaseModelClient):
    """
    Deterministic mock provider that produces realistic, calibrated ratings
    and evidence citations based on narrative cues or explicit overrides.
    Enables fully reproducible unit, integration, and regression testing.
    """

    def __init__(self, override_payload: Optional[Dict[str, Any]] = None):
        self.override_payload = override_payload

    def analyze_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Type[BaseModel]] = None,
        temperature: float = 0.2,
    ) -> Dict[str, Any]:
        if self.override_payload:
            return self.override_payload

        prompt_lower = prompt.lower()
        sys_lower = (system_prompt or "").lower()

        # 1. Consistency Audit Request Handler
        if ("audit instructions" in prompt_lower or "proposed alternative ending:" in prompt_lower) and "target dimension to elevate:" not in prompt_lower:
            # Extract proposed text and source text cleanly between quotes
            prop_match = re.search(r"proposed alternative ending:\s*(?:\"\"\"|```)?(.*?)(?:\"\"\"|```|\n\s*audit instructions)", prompt, re.DOTALL | re.IGNORECASE)
            src_match = re.search(r"(?:original story excerpt|prior story context):\s*(?:\"\"\"|```)?(.*?)(?:\"\"\"|```|\n\s*proposed alternative ending)", prompt, re.DOTALL | re.IGNORECASE)
            
            proposed_text = prop_match.group(1).strip() if prop_match else ""
            source_text = src_match.group(1).strip() if src_match else ""

            unsupported = []
            prop_lower = proposed_text.lower()
            src_lower = source_text.lower()

            check_tropes = [
                ("countdown timer", r"\bcountdown(?:\s+timer)?\b"),
                ("blast doors", r"\bblast\s+doors?\b"),
                ("floor trembling", r"\b(?:floor|ground)\s+trembled\b"),
                ("t-minus timer", r"\bt-minus\b"),
                ("hydraulic seals", r"\bhydraulic\s+seals?\b"),
            ]
            for label, pattern in check_tropes:
                if re.search(pattern, prop_lower) and not re.search(pattern, src_lower):
                    unsupported.append(label)

            if unsupported:
                return {
                    "is_consistent": False,
                    "contradictions": [],
                    "unsupported_entities": unsupported,
                    "critique": f"Injected unsupported scene facts: {', '.join(unsupported)}.",
                }
            return {
                "is_consistent": True,
                "contradictions": [],
                "unsupported_entities": [],
                "critique": "Maintains strict continuity and preserves all established characters and facts.",
            }

        # 2. Targeted Rewrite Generation Request Handler
        if "target dimension to elevate:" in prompt_lower or "fact-preservation directive" in prompt_lower or "script doctor" in sys_lower:
            # Extract target dimension
            dim_match = re.search(r"target dimension to elevate:\s*([a-zA-Z0-9_]+)", prompt, re.IGNORECASE)
            target_dim = dim_match.group(1).lower() if dim_match else "urgency"

            style_match = re.search(r"requested dramatic style:\s*([a-zA-Z0-9_]+)", prompt, re.IGNORECASE)
            style = style_match.group(1).lower() if style_match else "intensified"

            # Extract original ending segment
            ending_match = re.search(r"original ending segment:\s*\"\"\"(.*?)\"\"\"", prompt, re.DOTALL | re.IGNORECASE)
            original_ending = ending_match.group(1).strip() if ending_match else ""

            # 1. Arjun & Dr. Meera Scenario (Door 17 / Underground Facility)
            if "arjun" in prompt_lower or "meera" in prompt_lower or "door 17" in prompt_lower:
                char_a = "Arjun" if "arjun" in prompt_lower else "The researcher"
                char_b = "Dr. Meera" if "meera" in prompt_lower else "Colleague"

                if target_dim == "urgency":
                    content = (
                        f"{original_ending}\n\n"
                        f"{char_a} stepped back from the reinforced glass of Door 17 as the monitor flared crimson. "
                        f"{char_b}'s security badge slipped from his fingers—the terminal access log showed "
                        f"she had already logged into the inner laboratory sixty seconds before he arrived."
                    )
                    rationale = "Elevated urgency through immediate access log contradiction and locked door dilemma."
                    mechanism = "Security badge log contradiction and immediate physical containment."
                elif target_dim == "stakes":
                    content = (
                        f"{original_ending}\n\n"
                        f"{char_a} gripped the cold steel handle of Door 17 as the thermal seal disengaged. "
                        f"The duplicate identity card inside the terminal wasn't an unauthorized counterfeit—"
                        f"it belonged to him, stamped with tomorrow's expiration date."
                    )
                    rationale = "Elevated stakes by revealing personal identity duplication within the facility."
                    mechanism = "Existential stakes through temporal duplicate identity records."
                else:  # unresolved_question or default
                    content = (
                        f"{original_ending}\n\n"
                        f"{char_b} reached toward the manual release valve for Door 17, but froze mid-motion. "
                        f"'{char_a},' she whispered, staring at the bioscan readout on the console, "
                        f"'if you are standing right in front of me... whose voice is answering from the intercom inside the vault?'"
                    )
                    rationale = "Elevated unresolved question with a chilling identity paradox."
                    mechanism = "Bioscan voice paradox cutting off on an agonizing question."

                return {
                    "target_dimension": target_dim,
                    "style": style,
                    "content": content,
                    "predicted_score_boost": 16.5,
                    "dramatic_rationale": rationale,
                    "preserved_facts": {
                        "characters": [char_a, char_b],
                        "location": "Underground research facility / Door 17",
                        "objects_used": ["Door 17", "security badge", "terminal console"],
                        "timeline": "Immediate continuation",
                    },
                    "suspense_mechanism": mechanism,
                    "has_unsupported_facts": False,
                    "unsupported_facts": [],
                }

            # 2. Riya & Aarav Scenario (The 3:17 AM Call / Blue Box / Hospital Photograph)
            if "riya" in prompt_lower or "aarav" in prompt_lower or "blue box" in prompt_lower or "3:17" in prompt_lower or "photograph" in prompt_lower:
                char_a = "Riya" if "riya" in prompt_lower else "The daughter"
                char_b = "Aarav" if "aarav" in prompt_lower else "The brother"

                if target_dim == "urgency":
                    content = (
                        f"{original_ending}\n\n"
                        f"A sudden silence gripped the room as {char_a}'s hands trembled against the brass clasp of the blue box. "
                        f"{char_b} stepped forward, pointing at the heart monitor as the digital pulse line "
                        f"flattened for two agonizing seconds before catching again."
                    )
                    rationale = "Elevated urgency through medical crisis and irreversible box opening."
                    mechanism = "Failing vitals and imminent physical consequence."
                elif target_dim == "stakes":
                    content = (
                        f"{original_ending}\n\n"
                        f"{char_a} pressed the folded letter into {char_b}'s hand, her voice barely a whisper. "
                        f"'The memory restoration didn't fail,' she said, looking down at their mother. "
                        f"'She remembers everything—including why she had our childhood records erased.'"
                    )
                    rationale = "Elevated stakes by exposing deliberate past memory erasure."
                    mechanism = "Reversal of familial truth and moral consequence."
                else:  # unresolved_question or default
                    content = (
                        f"{original_ending}\n\n"
                        f"{char_b} lifted the silver frame from the hospital bedside table, turning the photograph toward the light. "
                        f"Standing directly behind their mother's smiling portrait was a third figure holding the identical blue box—"
                        f"someone neither of them had ever seen."
                    )
                    rationale = "Elevated unresolved question through shocking photographic evidence."
                    mechanism = "Unexplained third figure in existing family photograph."

                return {
                    "target_dimension": target_dim,
                    "style": style,
                    "content": content,
                    "predicted_score_boost": 15.0,
                    "dramatic_rationale": rationale,
                    "preserved_facts": {
                        "characters": [char_a, char_b, "Mother"],
                        "location": "Hospital room bedside",
                        "objects_used": ["blue box", "hospital photograph", "heart monitor"],
                        "timeline": "Immediate scene continuation",
                    },
                    "suspense_mechanism": mechanism,
                    "has_unsupported_facts": False,
                    "unsupported_facts": [],
                }

            # 3. Thomas & Lin Scenario (Outpost 7 / Arctic Transceiver)
            if "thomas" in prompt_lower or "lin" in prompt_lower or "transceiver" in prompt_lower or "outpost" in prompt_lower:
                char_a = "Thomas"
                char_b = "Lin"
                if target_dim == "urgency":
                    content = (
                        f"{original_ending}\n\n"
                        f"{char_a} reached toward the dial as the static snapped into sharp clarity. "
                        f"The voice on the transceiver began reciting {char_b}'s confidential emergency code, "
                        f"while the magnetic spool spun into its final few feet of tape."
                    )
                    rationale = "Elevated urgency through depleting recording tape and immediate identification code."
                    mechanism = "Depleting recording media and direct character security code."
                elif target_dim == "stakes":
                    content = (
                        f"{original_ending}\n\n"
                        f"{char_b} gripped the edge of the console, staring at the frequency readout. "
                        f"The coordinates being repeated on the channel did not belong to a distant vessel—"
                        f"they marked the exact latitude of their own outpost."
                    )
                    rationale = "Elevated stakes by revealing immediate local threat to the station itself."
                    mechanism = "Coordinate realization directly implicating the protagonists' sanctuary."
                elif target_dim == "information_gap":
                    content = (
                        f"{original_ending}\n\n"
                        f"{char_a} froze as the transmission looped a second time. "
                        f"Underneath the radio hum, the sound of their own footsteps entering the room "
                        f"five seconds earlier played clearly through the speaker."
                    )
                    rationale = "Elevated information gap via an inexplicable temporal audio loop."
                    mechanism = "Feedback audio loop revealing an unseen surveillance or temporal distortion."
                elif target_dim == "character_consequence":
                    content = (
                        f"{original_ending}\n\n"
                        f"{char_a} reached forward to rip the logbook page before {char_b} could verify the timestamp. "
                        f"'If command confirms who sent this,' {char_a} whispered, 'neither of us walks out of here.'"
                    )
                    rationale = "Elevated character consequence via direct interpersonal conflict over evidence."
                    mechanism = "Threat of internal treason and career destruction."
                else:  # unresolved_question or default
                    content = (
                        f"{original_ending}\n\n"
                        f"{char_b} leaned close to the microphone as the carrier wave peaked. "
                        f"The voice on the other end murmured three words that only {char_a}'s missing crew "
                        f"could have known, then went dead."
                    )
                    rationale = "Elevated unresolved question with a cryptic clue from the past."
                    mechanism = "Intimate secret knowledge uttered over an unknown frequency."

                return {
                    "target_dimension": target_dim,
                    "style": style,
                    "content": content,
                    "predicted_score_boost": 17.5,
                    "dramatic_rationale": rationale,
                    "preserved_facts": {
                        "characters": [char_a, char_b],
                        "location": "Outpost radio room",
                        "objects_used": ["transceiver", "magnetic tape spool", "logbook"],
                        "timeline": "Immediate scene continuity",
                    },
                    "suspense_mechanism": mechanism,
                    "has_unsupported_facts": False,
                    "unsupported_facts": [],
                }

            # General grounded rewrite
            if original_ending:
                content = (
                    f"{original_ending}\n\n"
                    f"A heavy silence settled over the room as the realization took hold. "
                    f"The final question wasn't what had just transpired—it was what had to be done next."
                )
            else:
                content = prompt[:200]

            return {
                "target_dimension": target_dim,
                "style": style,
                "content": content,
                "predicted_score_boost": 14.0,
                "dramatic_rationale": f"Elevated {target_dim} through psychological tension while preserving facts.",
                "preserved_facts": {
                    "characters": ["Established characters"],
                    "location": "Established setting",
                    "objects_used": ["Established scene items"],
                    "timeline": "Unbroken continuity",
                },
                "suspense_mechanism": "Psychological dilemma and narrative confrontation",
                "has_unsupported_facts": False,
                "unsupported_facts": [],
            }

        # Calibrate output deterministically based on text content keywords or target_level hint
        prompt_lower = prompt.lower()

        # Extract realistic quote from prompt text if available
        quote_sample = "Complete thermal purge initiated. T-minus ten seconds. Escape pods jettisoned."
        if "ending" in prompt_lower:
            parts = re.split(r"ending[:\s]+", prompt, flags=re.IGNORECASE)
            if len(parts) > 1:
                ending_part = parts[1].strip()
                sentences = [s.strip() for s in ending_part.replace("\n", " ").split(".") if len(s.strip()) > 10]
                if sentences:
                    quote_sample = sentences[0]
        elif "context:" in prompt_lower:
            sentences = [s.strip() for s in prompt.replace("\n", " ").split(".") if len(s.strip()) > 10]
            if sentences:
                quote_sample = sentences[-1]

        if "target_level: strong" in prompt_lower or "strong" in prompt_lower or "electrifying" in prompt_lower or "bomb" in prompt_lower or "timer" in prompt_lower or "revelation" in prompt_lower:
            # Strong cliffhanger pattern (Score ~ 75-88)
            return {
                "dimension_scores": {
                    "unresolved_question": {"score": 88.0, "confidence": 0.95, "explanation": "Urgent life-or-death question hanging."},
                    "stakes": {"score": 90.0, "confidence": 0.95, "explanation": "Catastrophic loss of life imminent."},
                    "emotional_intensity": {"score": 85.0, "confidence": 0.90, "explanation": "High adrenaline dread."},
                    "character_consequence": {"score": 80.0, "confidence": 0.85, "explanation": "Protagonist identity exposed."},
                    "surprise": {"score": 82.0, "confidence": 0.85, "explanation": "Unexpected breach of security."},
                    "urgency": {"score": 92.0, "confidence": 0.95, "explanation": "Detonation in 00:03 seconds."},
                    "causal_setup": {"score": 86.0, "confidence": 0.90, "explanation": "Direct consequence of previous infiltration."},
                    "information_gap": {"score": 75.0, "confidence": 0.80, "explanation": "Audience realizes the trap before hero."},
                    "originality": {"score": 78.0, "confidence": 0.80, "explanation": "Clever mechanical misdirection."},
                },
                "taxonomy_classifications": [
                    {"type": "threat", "confidence": 0.95, "rationale": "Active danger mechanism."},
                    {"type": "countdown", "confidence": 0.92, "rationale": "Urgent countdown."},
                    {"type": "decision", "confidence": 0.85, "rationale": "Forced critical choice."},
                ],
                "evidence_quotes": [
                    {"quote": quote_sample, "relevance": 0.98, "location": "ending"},
                ],
                "open_questions": [
                    "Will the protagonist survive the blast or trigger the blast doors?",
                    "Who rewired the fail-safe behind their back?",
                ],
            }

        elif "target_level: weak" in prompt_lower or "weak" in prompt_lower or "mundane" in prompt_lower or "tea" in prompt_lower or "slept" in prompt_lower or "ledger" in prompt_lower or "train" in prompt_lower:
            # Weak cliffhanger pattern (Score ~ 25-35)
            return {
                "dimension_scores": {
                    "unresolved_question": {"score": 28.0, "confidence": 0.85, "explanation": "Vague question about tomorrow's schedule."},
                    "stakes": {"score": 20.0, "confidence": 0.85, "explanation": "Minor inconvenience if plans change."},
                    "emotional_intensity": {"score": 22.0, "confidence": 0.80, "explanation": "Low arousal, calm setting."},
                    "character_consequence": {"score": 18.0, "confidence": 0.75, "explanation": "No material change to character arc."},
                    "surprise": {"score": 15.0, "confidence": 0.75, "explanation": "Predictable sequence of events."},
                    "urgency": {"score": 12.0, "confidence": 0.80, "explanation": "No pressing temporal demand."},
                    "causal_setup": {"score": 65.0, "confidence": 0.80, "explanation": "Logically connected but low energy."},
                    "information_gap": {"score": 15.0, "confidence": 0.70, "explanation": "No meaningful secret revealed."},
                    "originality": {"score": 22.0, "confidence": 0.75, "explanation": "Conventional domestic scene."},
                },
                "taxonomy_classifications": [
                    {"type": "relationship", "confidence": 0.50, "rationale": "Casual conversation over breakfast."},
                ],
                "evidence_quotes": [
                    {"quote": quote_sample, "relevance": 0.85, "location": "ending"},
                ],
                "open_questions": [
                    "Will the protagonist remember their umbrella tomorrow morning?",
                ],
            }

        else:
            # Moderate cliffhanger pattern (Score ~ 54-62)
            return {
                "dimension_scores": {
                    "unresolved_question": {"score": 65.0, "confidence": 0.85, "explanation": "Clear mystery surrounding the discovery."},
                    "stakes": {"score": 55.0, "confidence": 0.85, "explanation": "Reputational risk if discovered."},
                    "emotional_intensity": {"score": 58.0, "confidence": 0.80, "explanation": "Moderate nervous anticipation."},
                    "character_consequence": {"score": 56.0, "confidence": 0.80, "explanation": "Could change standing with peers."},
                    "surprise": {"score": 58.0, "confidence": 0.75, "explanation": "Expected discovery of a clue."},
                    "urgency": {"score": 54.0, "confidence": 0.80, "explanation": "Approaching deadline."},
                    "causal_setup": {"score": 65.0, "confidence": 0.85, "explanation": "Follows logically from searching the premises."},
                    "information_gap": {"score": 62.0, "confidence": 0.75, "explanation": "Audience knows someone is outside the door."},
                    "originality": {"score": 52.0, "confidence": 0.75, "explanation": "Classic investigative trope."},
                },
                "taxonomy_classifications": [
                    {"type": "mystery", "confidence": 0.80, "rationale": "Unmarked item discovered."},
                    {"type": "threat", "confidence": 0.55, "rationale": "Voices approaching in hallway."},
                ],
                "evidence_quotes": [
                    {"quote": quote_sample, "relevance": 0.92, "location": "ending"},
                ],
                "open_questions": [
                    "What document is hidden inside the locked drawer?",
                    "Will the investigator conceal themselves before the guard enters?",
                ],
            }

    def analyze_multimodal(
        self,
        content_parts: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        schema: Optional[Type[BaseModel]] = None,
    ) -> Dict[str, Any]:
        text_content = " ".join([p.get("text", "") for p in content_parts if isinstance(p, dict)])
        return self.analyze_text(prompt=text_content, system_prompt=system_prompt, schema=schema)

    def generate_embedding(self, texts: List[str]) -> List[List[float]]:
        # Deterministic 16-dimensional pseudo-embeddings via hashing
        embeddings = []
        for text in texts:
            digest = hashlib.sha256(text.encode("utf-8")).digest()
            vec = [(b / 255.0) * 2.0 - 1.0 for b in digest[:16]]
            embeddings.append(vec)
        return embeddings

    def rerank_evidence(self, query: str, candidates: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        # Sort candidates deterministically by length and keyword overlap
        query_words = set(query.lower().split())
        scored = []
        for cand in candidates:
            cand_words = set(cand.lower().split())
            overlap = len(query_words.intersection(cand_words))
            score = 0.5 + 0.1 * min(overlap, 5)
            scored.append({"text": cand, "relevance_score": score})
        scored.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored[:top_k]

    def extract_document_content(self, file_bytes: bytes, mime_type: str) -> str:
        try:
            return file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return file_bytes.decode("latin-1", errors="replace")
