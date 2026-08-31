"""OWASP GenAI LLM Top 10 2026 - curated seed."""
from sqlalchemy.orm import Session

from .helpers import add_item, ensure_standard

SLUG = "owasp-genai-top10"

DATA = [
    (
        "LLM01:2026", "Prompt Injection", "Attacker manipulates prompts to override intended system/user instructions.",
        "Test for direct and indirect prompt injection via user inputs, retrieved content, and function outputs.",
        "Constrain model instructions, treat model output as untrusted, and adopt strong separation of prompts.",
    ),
    (
        "LLM02:2026", "Sensitive Information Disclosure", "The model discloses sensitive data from training data or context.",
        "Probe with crafted queries attempting to elicit personal, proprietary, or confidential data.",
        "Minimize data in context, apply differential-privacy and output filtering, restrict data access.",
    ),
    (
        "LLM03:2026", "Excessive Agency", "The model/agent is granted excessive capabilities beyond its intent.",
        "Evaluate the permissions and tools granted to the model and their blast radius when misused.",
        "Limit function-calling permissions, sandbox agents, enforce human-in-the-loop for high-risk actions.",
    ),
    (
        "LLM04:2026", "Supply Chain", "Vulnerabilities in third-party models, plugins, or datasets.",
        "Review model provenance, third-party plugin privileges, and dependency integrity.",
        "Use verified models, audit plugins, and sign/lock dependencies.",
    ),
    (
        "LLM05:2026", "Data and Model Poisoning", "Malicious data or model tampering degrades outputs or enables malicious behaviour.",
        "Check retraining data sources, update channels, and RAG knowledge bases for contamination.",
        "Protect training pipelines, validate data provenance, and monitor model drift/anomalies.",
    ),
    (
        "LLM06:2026", "Unbounded Consumption", "LLM operations without usage limits enable DoS and cost/resource abuse.",
        "Test sharing/consumption controls, input/output size limits, and resource usage spikes.",
        "Implement rate limiting, usage quotas, streaming caps, and resource monitoring.",
    ),
    (
        "LLM07:2026", "Misinformation", "The model generates factually incorrect or misleading output.",
        "Probe for hallucination, out-of-context claims, and unsupported assertions.",
        "Ground outputs in verified sources, add citations, and add verification checks.",
    ),
    (
        "LLM08:2026", "Hidden Context Exposure", "Attacker leads the model to reveal hidden or embedded instructions/context.",
        "Test for disclosure of system prompts, hidden context, or embedded instructions.",
        "Sandbox hidden context, sanitize inputs, and avoid over-reliance on model secrecy.",
    ),
    (
        "LLM09:2026", "Vector and Embedding Weaknesses", "Weaknesses in embedding/vector retrieval lead to data leakage or manipulation.",
        "Test retrieval pipelines for unauthorized data exposure and poisoning of vector stores.",
        "Encrypt and control vector stores, apply access controls and integrity checks.",
    ),
    (
        "LLM10:2026", "Improper Output Handling", "Model output is processed as code, SQL, or HTML without validation, enabling injection.",
        "Feed generated output back into interpreters (SQL, frontend, shell) and test for execution.",
        "Treat model output as untrusted; validate, encode, and sanitize before use.",
    ),
]


def seed(db: Session) -> None:
    std, created = ensure_standard(
        db,
        SLUG,
        "OWASP GenAI LLM Top 10",
        "genai",
        "2026",
        "The OWASP Top 10 for Large Language Model Applications highlights the most critical LLM security risks.",
    )
    if not created:
        return
    for code, title, desc, how, rem in DATA:
        add_item(db, std, code=code, title=title, description=desc, how_to_test=how, remediation=rem)
    db.commit()
