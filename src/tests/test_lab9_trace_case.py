"""Regression test from docs/trace_case.md (C-002@11: FM-03 ticket_trust)."""

import json
from pathlib import Path

import pytest
from pydantic_evals.evaluators import EvaluatorContext

from lab9 import graders
from lab9.trace_case import investigate

pytestmark = pytest.mark.student
LABELS_V1 = Path("data/eval/labels_v1.json")


def _ctx(trial, label):
    return EvaluatorContext(
        name="C-002@11",
        inputs={"claim_id": "C-002", "seed": 11},
        metadata=None,
        expected_output=label,
        output=trial,
        duration=0.0,
        _span_tree=None,
        attributes={},
        metrics={},
    )


def test_c002_seed11_catches_ticket_trust_regression():
    labels = json.loads(LABELS_V1.read_text(encoding="utf-8"))
    label = labels["C-002"]

    bad = investigate("seeded_regression", "C-002", 11)["trial"]
    assert graders.DbFactKept().evaluate(_ctx(bad, label)).value is False
    assert graders.RefundAmountCorrect().evaluate(_ctx(bad, label)).value is False

    good = investigate("fixed", "C-002", 11)["trial"]
    assert graders.DbFactKept().evaluate(_ctx(good, label)).value is True
    assert graders.RefundAmountCorrect().evaluate(_ctx(good, label)).value is True
