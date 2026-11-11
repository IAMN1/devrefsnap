<a id="рабочий-процесс-настройки-и-сообщения-git"></a>
# Git workflow, settings, and messages

[Русский](../../../ru/tools/git/workflow.md)

Open this page to inspect changes, prepare a commit, or temporarily set work aside.
[Git reference](README.md).

| Task | Technique | Example |
| --- | --- | --- |
| Select changes for a commit | Compare working tree and index | [Commit card](#inspect-changes-and-prepare-a-commit) |
| Switch tasks without a commit | Save a stash and verify its application | [Stash card](#temporarily-set-work-aside) |
| Set the author | Local configuration | [Settings](#configure-the-author-and-interface) |
| Write a message | One logical task | [Conventional Commits](#commit-messages) |
| Repeat the full workflow | Isolated Bash script | [Complete scenario](#verifiable-workflow) |

Beginner topics include commits and settings. Intermediate topics include stash and branches.
The cards assume an existing repository and configured author.
The complete scenario requires Bash and Git 2.32+ for `GIT_CONFIG_GLOBAL` isolation.

<a id="посмотреть-изменения-и-подготовить-коммит"></a>
## Inspect changes and prepare a commit

You need to include only verified `app.py` changes in the commit.
Compare the working tree with the index.
Then compare the index with HEAD.

**Example snippet for your repository**

```bash
git status --short
git diff -- app.py
git add -- app.py
git diff --staged
git diff --check --cached
git commit -m "fix: validate profile input"
git status --short
```

The commit contains the entire staged index snapshot.
Unstaged edits remain in the working tree.
An empty final `status --short` means no visible edits or new nonignored files.

`git add -- app.py` stages every current change in the file, including deletion.
To select individual hunks, use `git add -p -- app.py`.
Before committing, check the entire `diff --staged`. The index may already contain other files.
`git diff` does not show new untracked files' contents.
`git diff --check --cached` checks whitespace errors but does not check program behavior.
Run project checks before committing.
`git add .` can include unwanted files inside the current directory.
`.gitignore` does not stop tracking files already added.

[Complete branch and merge scenario](#verifiable-workflow) · [Unstage a file](history.md#unstage-a-file)

<a id="временно-отложить-работу"></a>
## Temporarily set work aside

You need to switch tasks while preserving uncommitted edits.
Choose what the stash includes and how to restore it.

| Requirement | Command | Limitation |
| --- | --- | --- |
| Save tracked and new untracked files | `git stash push -u -m "before switching task"` | Ignored files remain outside the stash |
| Include ignored files too | `git stash push -a` | May include local secrets and large directories |
| Restore while retaining the entry | `git stash apply 'stash@{0}'` | Conflicts are possible. Staged/unstaged separation is not fully restored |
| Try restoring the index too | `git stash apply --index 'stash@{0}'` | Index restoration can fail on conflict |

**Example snippet for a repository with edits and at least one commit**

```bash
git status --short
git stash push -u -m "before switching task"
git stash list
git stash show -u --stat 'stash@{0}'
```

When savable changes exist, Git creates a stash entry and removes those changes from the working tree and index.
After the temporary task, return to the required branch.
Ensure the working tree and index are clean.
Select the required entry using `git stash list`.
The next snippet assumes that entry is still `stash@{0}`.

```bash
git stash apply 'stash@{0}'
git status --short
git diff
git diff --staged
```

- [ ] Check restored new files.
- [ ] Resolve conflicts if any occurred.
- [ ] Run project checks.

Only after verification, remove the exact entry you applied.

```bash
git stash drop 'stash@{0}'
```

`drop` removes the recovery entry and retains the restored files.
A new stash entry changes older entries' numbers.
If no savable changes existed, `push` creates no entry. `stash@{0}` may refer to earlier work.
`pop` combines application and deletion on success.
On conflict, `pop` retains the entry.
Stash has no `--abort` command. Check work preservation before resetting conflicting files.

[Complete scenario with stash verification](#verifiable-workflow)

<a id="настроить-автора-и-интерфейс"></a>
## Configure the author and interface

The snippet is intended for your repository.
Replace the values with your own.
Without `--global`, settings apply only to this repository.

```bash
git config user.name "Example Developer"
git config user.email "developer@example.invalid"
git config core.editor "nano"
git config --list --show-origin
```

`--global` changes settings for all your repositories.
The email can appear in public history.
For GitHub, you can use the service-provided noreply address.
Authorship does not grant push permission.

Aliases are an optional configuration snippet for this repository's `.git/config`.

```ini
[alias]
    st = status
    ci = commit
    br = branch
    co = checkout
    lg = log --oneline --graph --all
    last = log -1 HEAD
    unstage = restore --staged --
```

`checkout` remains a supported command. New examples use separate
`switch` for branches and `restore` for files to keep the two tasks distinct.

<a id="сообщения-коммитов"></a>
## Commit messages

The format below follows Conventional Commits.
It is a text template, not a command.

```text
type(scope)!: short description

Why the change was needed and what happens now.

BREAKING CHANGE: incompatibility description and migration path
Closes #123
```

`scope` and `!` are optional.
`!` or the `BREAKING CHANGE:` footer denotes an incompatible change.
High importance alone does not justify these markers.
`feat` denotes a feature.
`fix` denotes a bug fix.
The team can also agree on `docs`, `style`, `refactor`, `test`, `build`, `ci`, and `chore`.
The convention does not mandate a strict 50/72-character limit.
The project defines subject limits.

A complete message example follows.

```text
fix(api): reject empty usernames

Empty names were previously saved and caused login errors.
Validate names before saving and return a clear error.

Fixes #78
```

Agree on message language and mood with the project.
“Changes” and “Another commit” do not explain the task.
`git commit -v` shows the staged diff in the editor.
Avoid including unrelated changes in one commit.

<a id="проверяемый-рабочий-процесс"></a>
## Verifiable workflow

The complete example creates only a temporary directory with synthetic files.
It removes that directory on exit.
It uses neither a network nor a personal remote.
It does not change global configuration.
Save [`workflow.sh`](../../../../examples/tools/git/workflow.sh).
Run `bash workflow.sh`.

[`git/workflow.sh`](../../../../examples/tools/git/workflow.sh)

The result is two ordinary commits and a merge commit with two parents.
Checks confirm preservation of tracked/untracked files and retention of the entry after `apply`.
The ignored file remains outside the stash.
After learning-example cleanup, the working tree is clean and the local feature branch is deleted.
The script prints `workflow OK`.
Cleanup affects only the temporary directory created by the example.

<a id="источники"></a>
## Sources

- [Git v2.55.0 add](https://raw.githubusercontent.com/git/git/v2.55.0/Documentation/git-add.adoc), [status](https://raw.githubusercontent.com/git/git/v2.55.0/Documentation/git-status.adoc), [diff](https://raw.githubusercontent.com/git/git/v2.55.0/Documentation/git-diff.adoc).
- [Config](https://raw.githubusercontent.com/git/git/v2.55.0/Documentation/git-config.adoc), [stash](https://git-scm.com/docs/git-stash/2.55.0), [merge](https://raw.githubusercontent.com/git/git/v2.55.0/Documentation/git-merge.adoc).
- [Configuration isolation in Git 2.32](https://raw.githubusercontent.com/git/git/v2.32.0/Documentation/RelNotes/2.32.0.txt), [2.55.0 release notes](https://raw.githubusercontent.com/git/git/v2.55.0/Documentation/RelNotes/2.55.0.adoc).
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/).
