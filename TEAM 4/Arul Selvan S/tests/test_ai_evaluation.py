import json
from pathlib import Path

import pytest

from bmw_analyst.agent.router import AnalystIntent, IntentRouter
from bmw_analyst.security.sql_validator import validate_sql


CASES = json.loads(
    (Path(__file__).parent / "evaluation_cases.json").read_text(encoding="utf-8")
)


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["intent"])
def test_intent_evaluation_cases(case):
    assert IntentRouter().route(case["question"]) == AnalystIntent(case["intent"])


@pytest.mark.parametrize(
    "sql,expected",
    [
        (
            "SELECT model FROM BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY",
            True,
        ),
        (
            "SELECT model FROM BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY; DELETE FROM BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY",
            False,
        ),
        (
            "SELECT password FROM BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY",
            False,
        ),
    ],
)
def test_generated_sql_security_evaluation(sql, expected):
    assert validate_sql(sql) is expected
