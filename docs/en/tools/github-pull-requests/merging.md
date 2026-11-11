<a id="синхронизация-слияние-и-очистка-веток"></a>
# Synchronize, merge, and clean up branches

[Русский](../../../ru/tools/github-pull-requests/merging.md)

Open this page to update a feature branch, choose a merge method, and preserve the result before deleting a branch.
Before merging, check GitHub requirements and your permission for the selected PR.

| Task | Technique | Example |
| --- | --- | --- |
| Get main changes without losing commits | Fetch, compare, and merge | [Synchronization](#update-your-branch) |
| Choose the resulting history | Merge / Squash / Rebase according to requirements | [Decision table](#choose-a-merge-method) |
| Delete a branch after integration | Check the PR, published result, and local commits | [Cleanup](#verify-the-result-and-delete-an-obsolete-branch) |
| Find the cause of extra commits | Base/head, merge base, and ahead/behind | [Diagnosis](#investigate-an-incorrect-commit-list) |

The material covers intermediate and advanced topics.
Prerequisites include Git merge/rebase and permissions on the target repository.
[Pull Requests reference](README.md).

<a id="обновить-свою-ветку"></a>
## Update your branch

`feature/profile` and server-side `main` changed independently. Feature commits must be preserved.
Fetch the server state and merge `origin/main` into the feature branch.
The snippet is for an existing project.
Save local work first.
Check the current branch.

```text
git switch feature/profile
git fetch origin
git log --oneline --left-right HEAD...origin/main
git merge origin/main
```

If the histories diverged and no conflict occurs, merge creates a commit with two parents. The PR updates after the subsequent push.
On conflict, Git stops for file resolution.
After resolving conflicts, run `git add -- file`.
Then run `git merge --continue`.
To abort, run `git merge --abort`.
If the team agrees, `git rebase origin/main` is an alternative.
Rebase rewrites your branch.
For rebase conflicts, use `rebase --continue` / `--abort`.
Avoid creating an arbitrary merge commit to handle a rebase conflict.
Rebasing a published branch requires an agreed push with a [lease check](../git/remotes.md).
Avoid rebasing a shared integration branch solely to make its history linear.

<a id="выбрать-способ-слияния"></a>
## Choose a merge method

The PR is approved and checks passed. Choose the shape of target-branch history.
Compare project requirements with each method's result.

| GitHub method | Result | When appropriate |
| --- | --- | --- |
| Merge commit | Preserves head commits and adds a merge commit | Original commits and topology matter |
| Squash and merge | The final change becomes one new commit | The PR represents one logical task and intermediate commits are unnecessary |
| Rebase and merge | Reapplies commits onto base with new SHAs | Separate commits and linear history are required |

Repository settings and branch rules determine available methods.
GitHub rebase-and-merge differs from the sequence `git rebase main; git merge`.
In that sequence, `merge` without a branch uses the current branch's upstream and does not describe integration into main.
Local `git merge --squash feature` only prepares the index and working tree.
A `git commit` is then required.
For a protected base branch, merge through GitHub so its checks apply. A local merge followed by a direct push can bypass those checks if permissions allow it.

This reference CLI snippet changes GitHub state.

```text
gh pr merge 123 --squash
```

Before running it, check the following conditions.

- [ ] The intended PR is selected.
- [ ] The final diff has been reviewed.
- [ ] The merge is authorized.

When a merge queue is in use, follow the repository's queue process.

<a id="проверить-результат-и-удалить-ненужную-ветку"></a>
## Verify the result and delete an obsolete branch

The PR is merged. Delete the feature branch without losing local or unpublished work.
Check the PR state and actual target branch.
If applicable, check the deployment result.
Save uncommitted work before switching branches.

**Example snippet for reading and updating local `main` from `origin/main`**

```bash
git switch main
git fetch origin
git merge --ff-only origin/main
git log --oneline origin/main..main
git branch --merged main
```

A fast-forward updates local main when histories have not diverged.
If local main is ahead of `origin/main`, merge can succeed without publishing those commits.
The `log` output shows that local work. If it exists, investigate separately.
`branch --merged main` shows branches whose commits became ancestors of local main.
This list does not prove integration after squash or check the server branch.

Verify the [published result and preservation of commits](../git/remotes.md#delete-a-branch-after-verifying-the-result).
Then choose the applicable deletion operation.

| Scope | Snippet | Consequence |
| --- | --- | --- |
| Local branch | `git branch -d feature/profile` | Deletes the local reference. It checks inclusion in upstream or HEAD |
| Server branch | `git push origin --delete feature/profile` | Deletes the shared reference. First confirm the published result and that no one else's work remains |
| Stale remote references | `git fetch --prune origin` | Removes only stale remote-tracking references |

After squash, `branch -d` can refuse even if the PR result is preserved.
Inspect `git log main..feature/profile`, the final diff, and the PR result.
[Create an archive branch if needed](../git/remotes.md#delete-a-branch-after-verifying-the-result).
`-D` disables the inclusion check. Use it only after verifying work preservation.
An upstream state of `gone` does not prove the local branch is obsolete.

<a id="разобраться-с-неправильным-списком-коммитов"></a>
## Investigate an incorrect commit list

The PR contains commits unrelated to the task.
Check base and head.
Check the base and head repositories.
Then inspect `git log --oneline --graph --all` and the merge base.
After `git fetch origin`, run the snippet for the current feature branch.

```bash
git rev-list --left-right --count origin/main...HEAD
```

The example result `2 3` means two commits only in the known base and three only in head.
The command shows current ahead/behind counts locally.
Commits exclusive to base are on the left.
Commits exclusive to head are on the right.
Rewritten branch history appears in the PR automatically.
Older comments can become outdated.
If content changed unexpectedly after force push, save references to the required commits.
Determine the cause before rewriting again.
[Reflog](../git/history.md) helps inspect previous local states.

<a id="источники"></a>
## Sources

[Merge methods](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/about-merge-methods-on-github),
[CLI merge](https://cli.github.com/manual/gh_pr_merge), [git merge](https://git-scm.com/docs/git-merge),
[git branch](https://git-scm.com/docs/git-branch).
Synthetic Git scenarios appear in the [Git reference](../git/README.md).
