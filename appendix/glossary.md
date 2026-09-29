# Glossary

[← Contents](../README.md)

Every term from the guide, in plain English. The chapter where it's explained is in brackets.

| Term | Plain-English meaning |
|------|----------------------|
| **Agent eval** | Testing an AI that takes actions (files, tools, apps), usually in a sandbox, graded on the end state. [1, 10] |
| **Ablation** | Turning one component off to see how much it matters. [11] |
| **Baseline** | A reference score to compare against: a previous version, or a dumb strategy like "always say no". [2, 8] |
| **Benchmark** | A published, standard eval many people use to compare models. [1, 12] |
| **Calibration (of a judge)** | Checking how often an LLM judge agrees with human graders. [7] |
| **Canary string** | A unique marker in benchmark files asking model builders not to train on them. [5] |
| **Case / sample / task** | One test item. [1] |
| **Confidence interval (CI)** | A range that probably contains the true score, e.g. "72% ± 6%". [2] |
| **Confusion matrix** | A table of true/false positives/negatives for yes/no tasks. [2] |
| **Contamination** | When test cases or answers were in the model's training data, so it can "remember" them. [5] |
| **Dataset** | A collection of samples. [4, 5] |
| **Dev set / test set** | Cases you tune against freely / cases you check only occasionally, to avoid overfitting. [5] |
| **Distractor** | An irrelevant tool, file or service included to see if the agent picks the right one. [10] |
| **Drift / injection / mutation** | Changing the environment mid-task to test whether the agent notices. [10] |
| **End-state grading** | Scoring an agent by inspecting what it left behind (files, tests, app state), not what it said. [7, 10] |
| **Epoch / rep / trial** | One attempt at one sample; evals often run several per sample. [1, 2] |
| **Error (harness error)** | A trial that failed for plumbing reasons (timeout, API error). Not a score. [9] |
| **Eval** | A repeatable test: cases + a way to score them. [1] |
| **Eval harness** | Software that runs evals: loads cases, gets answers, grades, reports. [1, 4] |
| **Exact match** | Grading by comparing normalised text to the target. [7] |
| **Few-shot** | Putting example question-answer pairs in the prompt. [6] |
| **Ground truth / gold / target** | The correct answer. [1] |
| **Grader / scorer** | The code (or model, or person) that turns an answer into a score. [7] |
| **Headroom** | How far today's score is from 100%: room to show improvement. [5] |
| **Hidden tests** | Tests the AI never sees, run only at grading time. [7, 10] |
| **Jitter** | Random wiggle added to retry waits so workers don't all retry at once. [9] |
| **JSONL** | JSON Lines: one JSON object per line. [3] |
| **LLM-as-judge** | Using a model to grade outputs against a rubric. [7] |
| **Metric** | A number summarising many scores (accuracy, pass@k...). [8] |
| **Mock service** | A fake version of a real app/API for agents to use safely. [10] |
| **Noise floor** | The smallest difference an eval can reliably detect, given its size. [2, 11] |
| **Normalisation** | Cleaning up text (case, punctuation, spaces) before comparing. [7] |
| **Null run** | Running the eval with empty answers; should score ~0%. [11] |
| **Offline / online eval** | Testing on a fixed dataset before shipping / measuring real traffic after. [1] |
| **Oracle run** | Running the eval with the known-correct answers; should score ~100%. [11] |
| **Overfitting** | Tuning so hard to specific test cases that improvements don't generalise. [5] |
| **Paired comparison** | Comparing two systems question-by-question on the same samples. [2, 8] |
| **Pairwise judging** | A judge picks the better of two answers. [7] |
| **pass@k** | Chance that at least one of k tries succeeds (capability). [2, 8] |
| **pass^k** | Chance that all k tries succeed (reliability). [2, 8] |
| **Pointwise judging** | A judge scores one answer against a rubric. [7] |
| **Precision / recall** | Of the alarms raised, how many were right / of the real positives, how many were caught. [2] |
| **Rate limit** | The API's cap on requests or tokens per minute (HTTP 429 when exceeded). [3, 9] |
| **Reference solution** | A known-good answer proving the case is solvable. [4, 11] |
| **Regression** | Something that used to work and now doesn't. [1] |
| **Resume** | Restarting a crashed run without redoing finished trials. [9] |
| **Reward hacking** | The AI passing the grader without really doing the task. [11] |
| **Rubric** | A list of criteria for grading open-ended answers. [7] |
| **Sandbox** | An isolated environment (folder, container, VM) where a trial runs. [10] |
| **Saturation** | When top systems score near 100%, so the eval can't tell them apart. [5] |
| **Solver** | The part that produces the AI's answer for a sample. [4, 6] |
| **Standard deviation (SD)** | How spread out a set of scores is. [2] |
| **Standard error (SE)** | How much the average would wobble with different samples: SD / √n. [2] |
| **Status** | A trial's outcome type: ok, truncated, refusal, step_limit. [6, 9] |
| **Structured outputs** | An API feature guaranteeing the reply matches a JSON schema. [6, 7] |
| **Transcript / trajectory / trace** | The full record of a trial: messages, tool calls, results. [6] |
| **Truncated** | An answer cut off by `max_tokens`. Shown, but excluded from averages. [6, 8] |
| **Vibe check** | Trying a few examples by hand. Not an eval! [1] |

[← Contents](../README.md)
