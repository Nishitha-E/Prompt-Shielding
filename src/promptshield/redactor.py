import json
import re
from promptshield.detectors import PIIDetector

class PromptShieldEngine:
    def __init__(self, seed=42):
        self.detector = PIIDetector(seed=seed)
        self.mapping = {}
        self.reverse_mapping = {}

    def normalize(self, text):
        text = text.replace("\u00ad", "")
        text = re.sub(r'(\b\d{4})[ \t]*\n[ \t]*(\d{4})[ \t]*\n[ \t]*(\d{4}\b)', r'\1 \2 \3', text)
        text = re.sub(r'(\b\d{5})[ \t]*\n[ \t]*(\d{5}\b)', r'\1\2', text)
        return text

    def redact(self, text, normalize=True):
        if normalize:
            text = self.normalize(text)
        matches = self.detector.detect_all(text)
        if not matches:
            return text

        matches.sort(key=lambda m: m.start, reverse=True)
        chars = list(text)

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

            chars[match.start:match.end] = list(surrogate)

        return "".join(chars)

    def restore(self, text):
        res = text
        for surrogate, original in sorted(self.reverse_mapping.items(), key=lambda item: len(item[0]), reverse=True):
            res = res.replace(surrogate, original)
        return res

    def save_session(self, filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({"mapping": self.mapping, "reverse_mapping": self.reverse_mapping}, f, indent=2)

    def load_session(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.mapping = data.get("mapping", {})
            self.reverse_mapping = data.get("reverse_mapping", {})
