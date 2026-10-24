from promptshield.redactor import PromptShieldEngine
from promptshield.evaluate import evaluate_dataset

def test_round_trip_redaction_restoration():
    engine = PromptShieldEngine(seed=42)
    prompt = "Student Name: Rajesh Sharma, Roll No: 1005-26-701, PAN: ABCDE1234F"
    redacted = engine.redact(prompt)

    assert "Rajesh Sharma" not in redacted
    assert "1005-26-701" not in redacted
    assert "ABCDE1234F" not in redacted

    response = f"Processed details for {redacted}"
    restored = engine.restore(response)

    assert "Rajesh Sharma" in restored
    assert "1005-26-701" in restored
    assert "ABCDE1234F" in restored

def test_session_persistence(tmp_path):
    session_file = tmp_path / "session.json"
    engine1 = PromptShieldEngine(seed=42)
    text = "Student Name: Rajesh Sharma, PAN: ABCDE1234F"
    redacted1 = engine1.redact(text)
    engine1.save_session(str(session_file))

    engine2 = PromptShieldEngine(seed=999)
    engine2.load_session(str(session_file))
    redacted2 = engine2.redact(text)

    assert redacted1 == redacted2
    restored = engine2.restore(redacted2)
    assert "Rajesh Sharma" in restored

def test_education_context_preservation():
    engine = PromptShieldEngine(seed=42)
    text = (
        "University College of Engineering, Osmania University\n"
        "Student Name: Rajesh Sharma\n"
        "Course: M.E. Cyber Security\n"
        "B.Tech CGPA 8.85 / 10.0, GATE Score: 680"
    )
    redacted = engine.redact(text)
    assert "Osmania University" in redacted
    assert "M.E. Cyber Security" in redacted
    assert "B.Tech CGPA 8.85" in redacted
    assert "GATE Score: 680" in redacted
    assert "Rajesh Sharma" not in redacted

def test_evaluation_benchmark_50_samples():
    results = evaluate_dataset("data/education_eval_samples.json")
    overall = results["overall"]
    assert overall["tp"] >= 500
    assert overall["fn"] <= 40
    assert overall["precision"] > 95.0
    assert overall["recall"] > 90.0
