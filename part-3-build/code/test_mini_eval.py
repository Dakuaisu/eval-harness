"""
Tests for the eval harness itself. An eval harness is software, and it needs tests like any other.
No API key needed: a fake client stands in for the model.

    pytest test_mini_eval.py -q
"""

import json
import math
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

import mini_eval as me


# ---------------------------------------------------------------------------
# Graders: check them on known-right, known-wrong, and "right but messy" answers
# ---------------------------------------------------------------------------
def test_extract_answer_uses_last_answer_line():
    assert me.extract_answer("ANSWER: 3\nwait, no\nANSWER: 4") == "4"
    assert me.extract_answer("just 4") == "just 4"


@pytest.mark.parametrize("output", ["ANSWER: Canberra", "ANSWER: canberra.", "ANSWER: **Canberra**", "Canberra"])
def test_exact_accepts_equivalent_forms(output):
    assert me.grade_exact({"target": "Canberra"}, {"output": output})["score"] == 1.0


def test_exact_rejects_wrong_answer():
    assert me.grade_exact({"target": "Canberra"}, {"output": "ANSWER: Sydney"})["score"] == 0.0


@pytest.mark.parametrize("output,expected", [
    ("ANSWER: 6.80", 1.0), ("ANSWER: $6.8", 1.0), ("ANSWER: 1,234", 0.0), ("ANSWER: 7", 0.0), ("no idea", 0.0)])
def test_numeric(output, expected):
    assert me.grade_numeric({"target": 6.8, "tolerance": 0.001}, {"output": output})["score"] == expected


def test_python_tests_grader_passes_good_code_and_fails_bad_code():
    sample = {"tests": "from solution import add\nassert add(2, 3) == 5\n"}
    good = {"output": "```python\ndef add(a, b):\n    return a + b\n```"}
    bad = {"output": "```python\ndef add(a, b):\n    return a - b\n```"}
    assert me.grade_python_tests(sample, good)["score"] == 1.0
    assert me.grade_python_tests(sample, bad)["score"] == 0.0


def test_judge_is_not_called_for_empty_output():
    result = me.grade_llm_judge({"input": "x", "rubric": ["a"]}, {"output": "   "})
    assert result["score"] == 0.0


# ---------------------------------------------------------------------------
# Statistics: compare with values worked out by hand
# ---------------------------------------------------------------------------
def test_pass_at_k_matches_hand_calculation():
    # 5 tries, 2 successes. pass@1 = 2/5. pass@2 = 1 - C(3,2)/C(5,2) = 1 - 3/10.
    assert me.pass_at_k(5, 2, 1) == pytest.approx(0.4)
    assert me.pass_at_k(5, 2, 2) == pytest.approx(0.7)
    assert me.pass_at_k(5, 0, 3) == 0.0
    assert me.pass_at_k(5, 4, 2) == 1.0


def test_pass_hat_k_matches_hand_calculation():
    # 5 tries, 4 successes. pass^2 = C(4,2)/C(5,2) = 6/10.
    assert me.pass_hat_k(5, 4, 2) == pytest.approx(0.6)
    assert me.pass_hat_k(5, 5, 5) == 1.0


def test_mean_and_ci():
    m, h = me.mean_and_ci([1, 0, 1, 0])
    assert m == 0.5
    assert h == pytest.approx(1.96 * math.sqrt(1 / 3) / 2)


def test_truncated_answers_are_left_out_of_scores():
    rows = [{"id": "a", "score": 1.0, "status": "ok"}, {"id": "a", "score": 0.0, "status": "truncated"}]
    assert me.per_sample_scores(rows) == {"a": [1.0]}


# ---------------------------------------------------------------------------
# End to end with a fake model
# ---------------------------------------------------------------------------
def text_block(t):
    return NS(type="text", text=t)


def fake_response(content, stop_reason="end_turn", model="claude-opus-5-5"):
    return NS(content=content, stop_reason=stop_reason, model=model,
              usage=NS(input_tokens=100, output_tokens=20, cache_read_input_tokens=0))


class FakeClient:
    """Plays back a list of canned responses, one per API call."""
    def __init__(self, responses):
        self.responses, self.calls = list(responses), []
        self.messages = self

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self.responses.pop(0)


def make_args(tmp_path, dataset, **overrides):
    args = dict(dataset=str(dataset), solver="chat", model="claude-opus-5-5", effort="medium",
                judge_model="claude-sonnet-5-5", reps=1, workers=1, max_tokens=1000, max_steps=5,
                case_timeout=60, out=str(tmp_path / "runs"), name="test")
    args.update(overrides)
    return NS(**args)


def write_dataset(tmp_path, rows):
    path = tmp_path / "data.jsonl"
    path.write_text("\n".join(json.dumps(r) for r in rows))
    return path


def test_chat_run_scores_and_resumes(tmp_path, monkeypatch):
    dataset = write_dataset(tmp_path, [
        {"id": "q1", "input": "1+1?", "grader": "numeric", "target": 2},
        {"id": "q2", "input": "capital of France?", "grader": "exact", "target": "Paris"}])
    fake = FakeClient([fake_response([text_block("ANSWER: 2")]), fake_response([text_block("ANSWER: Lyon")])])
    monkeypatch.setattr(me, "_client", fake)
    args = make_args(tmp_path, dataset)
    me.cmd_run(args)
    rows = me.read_jsonl(Path(args.out) / "test" / "results.jsonl")
    assert sorted(r["score"] for r in rows) == [0.0, 1.0]
    # Running again must not repeat finished work (and so must not call the model).
    me.cmd_run(args)
    assert len(fake.calls) == 2


def test_wrong_model_is_an_error_not_a_score(tmp_path, monkeypatch):
    dataset = write_dataset(tmp_path, [{"id": "q1", "input": "1+1?", "grader": "numeric", "target": 2}])
    monkeypatch.setattr(me, "_client", FakeClient([fake_response([text_block("ANSWER: 2")], model="other-model")]))
    args = make_args(tmp_path, dataset)
    me.cmd_run(args)
    run = Path(args.out) / "test"
    assert me.read_jsonl(run / "results.jsonl") == []
    assert me.read_jsonl(run / "errors.jsonl")[0]["class"] == "model_mismatch"


def test_truncated_answer_is_marked(tmp_path, monkeypatch):
    dataset = write_dataset(tmp_path, [{"id": "q1", "input": "1+1?", "grader": "numeric", "target": 2}])
    monkeypatch.setattr(me, "_client", FakeClient([fake_response([text_block("Let me think")], "max_tokens")]))
    args = make_args(tmp_path, dataset)
    me.cmd_run(args)
    assert me.read_jsonl(Path(args.out) / "test" / "results.jsonl")[0]["status"] == "truncated"


def test_agent_is_graded_on_end_state(tmp_path, monkeypatch):
    dataset = write_dataset(tmp_path, [{
        "id": "a1", "input": "make hello.txt", "grader": "workspace_tests",
        "tests": "assert open('hello.txt').read() == 'hi'\n"}])
    write = NS(type="tool_use", id="t1", name="write_file", input={"path": "hello.txt", "content": "hi"})
    monkeypatch.setattr(me, "_client", FakeClient([
        fake_response([write], "tool_use"), fake_response([text_block("Done!")])]))
    args = make_args(tmp_path, dataset, solver="agent")
    me.cmd_run(args)
    row = me.read_jsonl(Path(args.out) / "test" / "results.jsonl")[0]
    assert row["score"] == 1.0 and row["tool_calls"] == 1


def test_agent_that_only_claims_success_fails(tmp_path, monkeypatch):
    dataset = write_dataset(tmp_path, [{
        "id": "a1", "input": "make hello.txt", "grader": "workspace_tests",
        "tests": "assert open('hello.txt').read() == 'hi'\n"}])
    monkeypatch.setattr(me, "_client", FakeClient([fake_response([text_block("Done! I created hello.txt.")])]))
    args = make_args(tmp_path, dataset, solver="agent")
    me.cmd_run(args)
    assert me.read_jsonl(Path(args.out) / "test" / "results.jsonl")[0]["score"] == 0.0


def test_judge_scores_fraction_of_criteria(tmp_path, monkeypatch):
    dataset = write_dataset(tmp_path, [{"id": "w1", "input": "write", "grader": "llm_judge",
                                        "rubric": ["is polite", "mentions Friday"]}])
    verdict = {"criteria": [{"criterion": "is polite", "reasoning": "yes", "met": True},
                            {"criterion": "mentions Friday", "reasoning": "no", "met": False}]}
    fake = FakeClient([fake_response([text_block("Dear Sam, thank you.")]),
                       fake_response([text_block(json.dumps(verdict))], model="claude-sonnet-5-5")])
    monkeypatch.setattr(me, "_client", fake)
    args = make_args(tmp_path, dataset)
    me.cmd_run(args)
    row = me.read_jsonl(Path(args.out) / "test" / "results.jsonl")[0]
    assert row["score"] == 0.5
    assert fake.calls[1]["model"] == "claude-sonnet-5-5"     # the judge is a different model


@pytest.mark.parametrize("dataset", ["datasets/basics.jsonl", "datasets/agent_tasks.jsonl"])
def test_oracle_scores_100_and_null_scores_0(tmp_path, dataset):
    """The two most important sanity checks for any eval (Chapter 11)."""
    here = Path(__file__).parent
    for solver, expected in (("oracle", 1.0), ("null", 0.0)):
        args = make_args(tmp_path, here / dataset, solver=solver, name=solver, workers=4)
        me.cmd_run(args)
        rows = me.read_jsonl(Path(args.out) / solver / "results.jsonl")
        assert rows and all(r["score"] == expected for r in rows), [r["id"] for r in rows if r["score"] != expected]
