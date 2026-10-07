"""Redactor and Session Vault engine for PII replacement and exact restoration."""

import json
from typing import Dict, Tuple, Optional
from promptshield.detectors import PIIDetector


class PromptShieldEngine:
    """Manages session-consistent PII substitution and exact reverse restoration."""

    def __init__(self, seed: Optional[int] = 42):
        self.detector = PIIDetector(seed=seed if seed is not None else 42)
        # Session mapping tables
        self.mapping: Dict[str, str] = {}  # original -> surrogate
        self.reverse_mapping: Dict[str, str] = {}  # surrogate -> original

    def redact(self, text: str) -> str:
        """Detect PII in text, replace with surrogates, and update session mapping."""
        matches = self.detector.detect_all(text)
        if not matches:
            return text

        # Sort matches backwards by start index to replace cleanly without index shifting
        matches.sort(key=lambda m: m.start, reverse=True)
        result_chars = list(text)

        for match in matches:
            orig = match.original
            if orig not in self.mapping:
                surrogate = self.detector.generate_surrogate(match.pii_type, orig)
                # Ensure surrogate is unique in reverse_mapping
                while surrogate in self.reverse_mapping:
                    surrogate = self.detector.generate_surrogate(match.pii_type, orig)
                self.mapping[orig] = surrogate
                self.reverse_mapping[surrogate] = orig
            else:
                surrogate = self.mapping[orig]

            result_chars[match.start : match.end] = list(surrogate)

        return "".join(result_chars)

    def restore(self, text: str) -> str:
        """Silently restore original PII values into model output."""
        restored = text
        # Sort surrogates by length descending to prevent partial key substring replacements
        for surrogate, original in sorted(
            self.reverse_mapping.items(), key=lambda item: len(item[0]), reverse=True
        ):
            restored = restored.replace(surrogate, original)
        return restored

    def export_session(self) -> Dict[str, str]:
        """Export current session mapping."""
        return dict(self.mapping)

    def save_session(self, filepath: str) -> None:
        """Save session mapping to JSON file."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({"mapping": self.mapping, "reverse_mapping": self.reverse_mapping}, f, indent=2)

    def load_session(self, filepath: str) -> None:
        """Load session mapping from JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.mapping = data.get("mapping", {})
            self.reverse_mapping = data.get("reverse_mapping", {})
