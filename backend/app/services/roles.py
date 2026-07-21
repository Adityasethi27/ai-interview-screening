"""Role registry. Each role maps to a knowledge-base directory (collection)
and a set of default evaluation topics used as a fallback / seed for context
construction.
"""
from __future__ import annotations

ROLES: dict[str, dict] = {
    "ai_ml_engineer": {
        "label": "AI/ML Engineer",
        "description": "Machine learning fundamentals, model training, evaluation and deployment.",
        "seed_topics": [
            "supervised learning",
            "bias-variance tradeoff",
            "overfitting and regularization",
            "gradient descent and optimization",
            "model evaluation metrics",
            "neural networks",
        ],
    },
    "backend_engineer": {
        "label": "Backend Engineer",
        "description": "API design, databases, system design, scalability and reliability.",
        "seed_topics": [
            "REST API design",
            "relational database indexing",
            "caching strategies",
            "concurrency and async",
            "system scalability",
            "authentication and security",
        ],
    },
    "data_science": {
        "label": "Data Scientist",
        "description": "Applied ML, statistics, feature engineering and experimentation.",
        "seed_topics": [
            "feature engineering",
            "cross validation",
            "statistical hypothesis testing",
            "dimensionality reduction",
            "ensemble methods",
            "handling imbalanced data",
        ],
    },
}


def get_role(role_id: str) -> dict:
    if role_id not in ROLES:
        raise KeyError(role_id)
    return ROLES[role_id]


def list_roles() -> list[dict]:
    return [
        {"id": rid, "label": r["label"], "description": r["description"]}
        for rid, r in ROLES.items()
    ]
