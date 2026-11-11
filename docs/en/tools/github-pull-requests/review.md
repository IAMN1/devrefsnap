<a id="описание-ревью-и-проверки-pr"></a>
# PR description, review, and checks

[Русский](../../../ru/tools/github-pull-requests/review.md)

Open this page to describe a change's result and check whether a PR is ready for a decision.
Commands that create a PR or change its Draft status modify the selected GitHub repository's state.

| Task | Technique | Example |
| --- | --- | --- |
| Explain an observable change | Input → previous result → new result | [Description](#prepare-a-clear-proposal) |
| Create a draft and verify the target | Explicit base/head and a description file | [GitHub CLI](#create-and-view-through-the-cli) |
| Address feedback | Author and reviewer responsibilities | [Review](#author-and-reviewer-actions) |
| Check merge readiness | Diff, approvals, and required checks | [Before merging](#before-merging) |

The material covers beginner and intermediate topics.
Prerequisites include a branch with changes and an understanding of the task and project rules.
[Pull Requests reference](README.md).

<a id="подготовить-понятное-предложение"></a>
## Prepare a clear proposal

The API previously saved an empty name. It should now return `422` before writing data.
State a specific input and observable behavior so a reviewer can verify the task without reading prior correspondence.
Check your diff first.

- [ ] Check for secrets.
- [ ] Check for debug edits.
- [ ] Check for unrelated changes.

A PR should give enough context to someone who did not read the prior correspondence.
One coherent result is easier to review.
GitHub does not require a fixed limit of 400 lines.

Adapt the description template to the specific repository's template.

```markdown
## Задача и результат
Что происходило раньше, при каком условии и что теперь меняется.

## Изменения
- Существенные изменения и причина выбранного решения.

## Проверка
- Что выполнено и какой получен результат.
- Что не проверялось и почему это существенно.

## Риски и совместимость
Миграции, несовместимость, ограничения; при необходимости план отката.

## Связанные задачи
Closes #123
```

**Short PR description excerpt**

```text
POST /profiles with {"name":" "} previously saved an empty name.
The API now returns 422 before saving the profile.
Verification: pytest tests/test_profiles.py — the success and empty-name cases pass.
```

The verification line illustrates the format. Replace it with the command you actually ran and its result.
The reviewer understands which request to check and which data should stay unchanged.
For UI changes, add comparable before/after screenshots.
For behavioral changes, state a specific input and result.
Report checks you actually performed.
“Tests pass” without a command and context provides little help to the reviewer.
Conventional Commits for the title is a [project convention](../git/workflow.md#commit-messages).

<a id="создать-и-посмотреть-через-cli"></a>
## Create and view through the CLI

The `feature/profile` branch is ready for early discussion and targets `main`.
Create a draft with explicit branches and a prepared description in `pr-body.md`.

The reference snippets assume authenticated `gh` in the correct repository.
The first commands push the branch and create a GitHub object.

```text
git push -u origin feature/profile
gh pr create --draft --base main --head feature/profile --title "feat: add profile" --body-file pr-body.md
gh pr view 123 --web
gh pr list
```

The `pr-body.md` file must contain the actual description.
Before creating, check `git remote -v`.
Check base/head in the interface.
`gh pr create` creates a draft PR and prints its URL.
In subsequent commands, replace `123` with the created PR number.
`gh pr view` opens an existing PR. `gh pr list` displays a list.
Creation requires network access and permissions. CI success and merge readiness are separate checks.

<a id="действия-автора-и-ревьюера"></a>
## Author and reviewer actions

The PR received feedback. Identify the required fixes and suggestions for discussion.
Compare each comment with the project goal, behavior, and constraints.

| Author | Reviewer |
| --- | --- |
| Explain the problem and solution boundaries | Check the change against the goal and constraints |
| Check your own diff | Check correctness, edge cases, security, and compatibility |
| Add appropriate reviewers | Make specific comments on code and behavior |
| Respond to feedback. Explain disagreements | Distinguish a required fix from a suggestion |
| Push fixes to the same branch | Recheck significant edits |

A review can end with Comment, Approve, or Request changes.
Depending on protections, new commits can require renewed approval.
The team defines response time and reviewer count.
There is no universal 24-hour or 2+ rule.

<a id="перед-слиянием"></a>
## Before merging

- [ ] Check base/head selection.
- [ ] Inspect the final diff.
- [ ] Run required checks.
- [ ] Verify required CI checks apply to the intended branch state.
- [ ] Obtain required approvals.
- [ ] Address blocking conversations.
- [ ] Check for unresolved conflicts.
- [ ] Verify the PR is ready for review.
- [ ] Verify repository requirements are met.
- [ ] Choose the agreed merge strategy.
- [ ] Define follow-up actions.

`gh pr checks 123` shows checks.
`gh pr ready 123` changes Draft to ready for review.
A passing local test does not replace a required server-side check.

<a id="источники"></a>
## Sources

[GitHub PR quickstart](https://docs.github.com/en/pull-requests/get-started/pull-request-quickstart),
[CLI create](https://cli.github.com/manual/gh_pr_create), [CLI checks](https://cli.github.com/manual/gh_pr_checks).
