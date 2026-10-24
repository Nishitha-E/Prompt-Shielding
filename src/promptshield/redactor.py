import json
from typing import Dict, Tuple, Optional
from promptshield.detectors import PIIDetector
from promptshield.normalizer import normalize_clinical_text

class PromptShieldEngine:
    def __init__(self, seed: Optional[int] = 42):
        self.detector = PIIDetector(seed=seed if seed is not None else 42)
        self.mapping: Dict[str, str] = {}
        self.reverse_mapping: Dict[str, str] = {}

    def redact(self, text: str, normalize: bool = True) -> str:
        if normalize:
            text = normalize_clinical_text(text)
        matches = self.detector.detect_all(text)
        if not matches:
            return text

        matches.sort(key=lambda m: m.start, reverse=True)
        result_chars = list(text)

        for match in matches:
            orig = match.original
            if orig not in self.mapping:
                surrogate = self.detector.generate_surrogate(match.pii_type, orig)
                while surrogate in self.reverse_mapping:
                    surrogate = self.detector.generate_surrogate(match.pii_type, orig)
                self.mapping[orig] = surrogate
                self.reverse_mapping[surrogate] = orig
            else:
                surrogate = self.mapping[orig]

            result_chars[match.start : match.end] = list(surrogate)

        return "".join(result_chars)

    def restore(self, text: str) -> str:
        restored = text
        for surrogate, original in sorted(
            self.reverse_mapping.items(), key=lambda item: len(item[0]), reverse=True
        ):
            restored = restored.replace(surrogate, original)
        return restored

    def export_session(self) -> Dict[str, str]:
        return dict(self.mapping)

    def save_session(self, filepath: str) -> None:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({"mapping": self.mapping, "reverse_mapping": self.reverse_mapping}, f, indent=2)

    def load_session(self, filepath: str) -> None:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.mapping = data.get("mapping", {})
            self.reverse_mapping = data.get("reverse_mapping", {})
