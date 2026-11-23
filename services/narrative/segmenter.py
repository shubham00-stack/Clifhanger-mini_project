"""Narrative scene segmentation, character tracking, and rewrite services."""

import re
from typing import List, Tuple, Dict, Any, Optional
from packages.schemas.enums import LocationType


class NarrativeSegmenter:
    """Segments raw story manuscripts into distinct scenes and identifies ending segments."""

    SCENE_HEADER_REGEX = re.compile(
        r"^(?:(?:INT|EXT|INT\./EXT|INT/EXT)\.?\s+[A-Z0-9_\-\.\s]+|SCENE\s+\d+[\:\.\-]?|CHAPTER\s+[0-9IVXLCDM]+|ACT\s+[0-9IVXLCDM]+)",
        re.IGNORECASE | re.MULTILINE,
    )

    CHARACTER_CUE_REGEX = re.compile(
        r"^[A-Z0-9\s\.\-\'\(\)]{3,30}$"
    )

    def segment_scenes(self, text: str) -> List[Tuple[str, str, LocationType]]:
        """
        Splits text into (heading, content, location_type).
        Falls back to paragraph blocks if no formal screenplay headers exist.
        """
        if not text or not text.strip():
            return [("ENDING CUTOFF", "", LocationType.OTHER)]

        lines = text.strip().split("\n")
        scenes: List[Tuple[str, List[str], LocationType]] = []
        current_heading = "SCENE 1"
        current_lines: List[str] = []
        current_loc = LocationType.OTHER

        for line in lines:
            stripped = line.strip()
            match = self.SCENE_HEADER_REGEX.match(stripped)
            if match:
                if current_lines:
                    scenes.append((current_heading, current_lines, current_loc))
                    current_lines = []
                current_heading = stripped
                upper = stripped.upper()
                if upper.startswith("INT"):
                    current_loc = LocationType.INT
                elif upper.startswith("EXT"):
                    current_loc = LocationType.EXT
                else:
                    current_loc = LocationType.OTHER
            else:
                current_lines.append(line)

        if current_lines or not scenes:
            scenes.append((current_heading, current_lines, current_loc))

        # Format output
        results = []
        for heading, scene_lines, loc in scenes:
            content = "\n".join(scene_lines).strip()
            if content:
                results.append((heading, content, loc))

        if not results:
            results.append(("ENDING CUTOFF", text.strip(), LocationType.OTHER))

        return results

    def segment_scenes_with_provenance(self, text: str) -> List[Dict[str, Any]]:
        """Structured scene segmentation returning detailed provenance dictionaries."""
        tuples = self.segment_scenes(text)
        scenes = []
        for idx, (heading, content, loc) in enumerate(tuples, start=1):
            scenes.append({
                "scene_index": idx,
                "heading": heading,
                "content": content,
                "location_type": loc.value if hasattr(loc, "value") else str(loc),
                "word_count": len(content.split()),
                "char_count": len(content),
                "is_ending_segment": (idx == len(tuples)),
            })
        return scenes

    def set_ending_boundary(
        self,
        scenes: List[Dict[str, Any]],
        boundary_scene_index: Optional[int] = None,
        boundary_marker: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Allows manual ending boundary selection via scene index or textual snippet."""
        target_idx = None

        if boundary_scene_index is not None:
            target_idx = boundary_scene_index
        elif boundary_marker:
            marker_clean = boundary_marker.lower().strip()
            for s in scenes:
                if marker_clean in s["content"].lower() or marker_clean in s["heading"].lower():
                    target_idx = s["scene_index"]
                    break

        if target_idx is not None:
            for s in scenes:
                s["is_ending_segment"] = (s["scene_index"] == target_idx)
        else:
            # Fallback to last scene
            for i, s in enumerate(scenes):
                s["is_ending_segment"] = (i == len(scenes) - 1)

        return scenes

    def extract_dialogue_and_action_boundaries(self, scene_content: str) -> Dict[str, Any]:
        """Separates character dialogue blocks from descriptive action lines."""
        lines = scene_content.split("\n")
        dialogues = []
        actions = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            if self.CHARACTER_CUE_REGEX.match(line) and i + 1 < len(lines):
                speaker = line
                dialogue_text = []
                i += 1
                while i < len(lines) and lines[i].strip() and not self.CHARACTER_CUE_REGEX.match(lines[i].strip()):
                    dialogue_text.append(lines[i].strip())
                    i += 1
                dialogues.append({
                    "speaker": speaker,
                    "dialogue": " ".join(dialogue_text),
                })
            else:
                actions.append(line)
                i += 1

        return {
            "dialogues": dialogues,
            "actions": actions,
            "dialogue_count": len(dialogues),
            "action_count": len(actions),
        }

    def extract_ending_segment(self, text: str, max_words: int = 250) -> str:
        """Extracts the final narrative segment up to the cutoff boundary."""
        if not text or not text.strip():
            return ""
        words = text.strip().split()
        if len(words) <= max_words:
            return text.strip()
        return " ".join(words[-max_words:])
