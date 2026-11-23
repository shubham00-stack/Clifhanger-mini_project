"""Narrative scene segmentation, character tracking, and rewrite services."""

import re
from typing import List, Tuple
from packages.schemas.enums import LocationType


class NarrativeSegmenter:
    """Segments raw story manuscripts into distinct scenes and identifies ending segments."""

    SCENE_HEADER_REGEX = re.compile(
        r"^(?:(?:INT|EXT|INT\./EXT|INT/EXT)\.?\s+[A-Z0-9_\-\.\s]+|SCENE\s+\d+|CHAPTER\s+\d+)",
        re.IGNORECASE | re.MULTILINE,
    )

    def segment_scenes(self, text: str) -> List[Tuple[str, str, LocationType]]:
        """
        Splits text into (heading, content, location_type).
        Falls back to paragraph blocks if no formal screenplay headers exist.
        """
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

    def extract_ending_segment(self, text: str, max_words: int = 250) -> str:
        """Extracts the final narrative segment up to the cutoff boundary."""
        words = text.strip().split()
        if len(words) <= max_words:
            return text.strip()
        return " ".join(words[-max_words:])
