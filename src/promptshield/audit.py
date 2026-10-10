"""Transparency Panel and Audit logging for Prompt Shield PII substitution."""

import json
from typing import Dict, List, Any
from pathlib import Path


class TransparencyAudit:
    """Generates transparency and audit summaries for PII substitution."""

    def __init__(self, mapping: Dict[str, str], pii_metadata: Dict[str, str] = None):
        self.mapping = mapping
        self.pii_metadata = pii_metadata or {}

    def generate_text_summary(self, original_text: str, redacted_text: str) -> str:
        """Generate human-readable CLI audit report."""
        lines = [
            "=" * 70,
            " PROMPT SHIELD: TRANSPARENCY & AUDIT REPORT",
            "=" * 70,
            f"Total PII Entities Substituted: {len(self.mapping)}",
            "-" * 70,
            f"{'Original PII Value':<32} -> {'Format-Valid Surrogate':<32}",
            "-" * 70,
        ]
        for orig, surrogate in self.mapping.items():
            lines.append(f"{orig:<32} -> {surrogate:<32}")
        lines.append("=" * 70)
        return "\n".join(lines)

    def generate_html_report(
        self, original_text: str, redacted_text: str, output_path: str
    ) -> None:
        """Generate an interactive HTML audit panel showing highlighted PII."""
        highlighted_orig = original_text
        highlighted_redacted = redacted_text

        # Highlight original PII in red and surrogates in green
        for orig, surrogate in self.mapping.items():
            highlighted_orig = highlighted_orig.replace(
                orig, f'<span class="pii-orig" title="Substituted PII">{orig}</span>'
            )
            highlighted_redacted = highlighted_redacted.replace(
                surrogate, f'<span class="pii-surr" title="Surrogate">{surrogate}</span>'
            )

        rows_html = "".join(
            f"<tr><td><code>{orig}</code></td><td><code>{surr}</code></td><td><span class='badge'>Protected</span></td></tr>"
            for orig, surr in self.mapping.items()
        )

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Prompt Shield - Transparency Audit Panel</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 24px; }}
  .container {{ max-width: 1100px; margin: 0 auto; }}
  h1 {{ color: #38bdf8; font-size: 24px; margin-bottom: 8px; }}
  .subtitle {{ color: #94a3b8; margin-bottom: 24px; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }}
  .card {{ background: #1e293b; border-radius: 8px; padding: 16px; border: 1px solid #334155; }}
  .card h3 {{ margin-top: 0; font-size: 16px; color: #cbd5e1; border-bottom: 1px solid #334155; padding-bottom: 8px; }}
  pre {{ white-space: pre-wrap; word-break: break-word; font-size: 13px; line-height: 1.5; color: #e2e8f0; }}
  .pii-orig {{ background: rgba(239, 68, 68, 0.25); color: #f87171; border-bottom: 2px solid #ef4444; padding: 2px 4px; border-radius: 4px; }}
  .pii-surr {{ background: rgba(34, 197, 94, 0.25); color: #4ade80; border-bottom: 2px solid #22c55e; padding: 2px 4px; border-radius: 4px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid #334155; }}
  th {{ background: #0f172a; color: #94a3b8; font-weight: 600; }}
  code {{ font-family: monospace; font-size: 13px; }}
  .badge {{ background: #0369a1; color: #e0f2fe; padding: 2px 8px; border-radius: 12px; font-size: 11px; }}
  .footer {{ color: #64748b; font-size: 12px; text-align: center; margin-top: 32px; }}
</style>
</head>
<body>
<div class="container">
  <h1>🛡️ Prompt Shield: Local Transparency Panel</h1>
  <div class="subtitle">100% on-device sanitization. Zero sensitive identifiers sent to LLM endpoints.</div>

  <div class="card" style="margin-bottom: 20px;">
    <h3>Substitution Vault Mapping ({len(self.mapping)} Entities)</h3>
    <table>
      <thead>
        <tr><th>Original Sensitive Value (Redacted)</th><th>Format-Valid Surrogate (Sent to LLM)</th><th>Status</th></tr>
      </thead>
      <tbody>
        {rows_html}
      </tbody>
    </table>
  </div>

  <div class="grid">
    <div class="card">
      <h3>Original Document (Local Client View)</h3>
      <pre>{highlighted_orig}</pre>
    </div>
    <div class="card">
      <h3>Sanitized Payload (Transmitted to LLM)</h3>
      <pre>{highlighted_redacted}</pre>
    </div>
  </div>

  <div class="footer">Prompt Shield · Pragya Cyber × OU CCoE AI Security Sprint · On-Device Verification</div>
</div>
</body>
</html>
"""
        Path(output_path).write_text(html_content, encoding="utf-8")
