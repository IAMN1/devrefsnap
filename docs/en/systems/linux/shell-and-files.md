<a id="shell-файлы-и-поиск"></a>
# Shell, files, and search

[Русский](../../../ru/systems/linux/shell-and-files.md)

Use this page to create files, find log lines, or handle names containing spaces.
Before changing data, select your own practice directory.

| Task | Approach | Example |
| --- | --- | --- |
| Create, copy, or delete a file | Explicit paths and overwrite consequences | [File operations](#basic-operations) |
| Find errors in a log | `grep` with separate stderr | [Text and status](#text-streams-and-exit-codes) |
| Pass names containing spaces | `find -exec` or a null delimiter | [Unusual names](#find-files-with-unusual-names) |
| Practice copying and restoring | Synthetic data in a temporary directory | [Complete script](#safe-practice-example) |

Basic and intermediate levels. Prerequisites include Bash, standard file utilities, and a writable temporary directory.
[Linux reference](README.md).

<a id="основные-операции"></a>
## Basic operations

To create a note and make a copy while preserving the source, choose the operation that produces the required change.
The table contains separate reference fragments. Check `pwd` first, then replace the paths with your own.

| Task | Fragment | Consequence |
| --- | --- | --- |
| Create a directory | `mkdir -p project/data` | Creates missing directories |
| Write text | `printf '%s\n' 'hello' > note.txt` | `>` creates or overwrites the file |
| Append | `printf '%s\n' 'next' >> note.txt` | Appends at the end |
| Copy | `cp -i source.txt copy.txt` | `-i` prompts before overwriting and reads the answer from stdin |
| Move | `mv -i copy.txt archive.txt` | Changes the name or location and may overwrite the destination |
| Delete a file | `rm -i -- archive.txt` | Removes the name, usually without a shell recycle bin |
| Delete an empty directory | `rmdir empty-dir` | Rejects a nonempty directory |
| View contents | `less note.txt`, `head -n 10 note.txt`, `tail -n 20 note.txt` | Reads the file, with `tail -f` waiting for new lines |

The shell expands the glob in `rm *.log` before rm starts.
For a path beginning with a dash, use `./-name` or the command's supported `--` operand separator.
`ln -s TARGET LINK` creates a symbolic link. A relative TARGET is resolved from LINK's directory.
Before deleting or archiving, check how the command handles symbolic links.

<a id="безопасный-практический-пример"></a>
## Safe practice example

The complete script uses synthetic logs and a path containing a space.
It searches, creates an archive, and compares a restored file.
Run `bash example.sh`. Deletion is restricted to the directory created by `mktemp -d`.

[`linux/example.sh`](../../../../examples/systems/linux/example.sh)

Expect `files OK`. The `wc` output depends on the random temporary path.
Before extracting an untrusted archive, inspect `tar -tf archive.tar`, including paths and links.
Choose an isolated extraction directory instead of an important data directory.

<a id="текст-потоки-и-коды-выхода"></a>
## Text, streams, and exit codes

Suppose an existing `app.log` contains `ERROR missing` and you need to save matching lines separately from command diagnostics.
Select lines with `grep` and redirect stdout and stderr to different files.
The fragments read the specified file and produce output. `2>` overwrites the error log.

```bash
grep -n -E 'ERROR|WARN' app.log
sed -n '1,20p' app.log
awk '{print $1}' app.log | sort | uniq -c
grep 'ERROR' app.log > output.txt 2> error.txt
```

The fragments assume that `app.log` exists.
The last line puts `ERROR missing` into `output.txt`, while `error.txt` contains only command diagnostics.
Each run overwrites both files.
`2>&1` sends stderr to stdout's current destination, so the order of `>file 2>&1` matters.
A pipeline such as `cmd | tee output.txt` usually reports the last command's status.
In Bash, `set -o pipefail` accounts for failure of any pipeline command.
`set -e` has exceptions and does not replace explicit handling of expected statuses.

GNU grep returns 0 for a match, 1 for no match, and 2 for an error.
Other implementations may have additional error codes.
If no match is expected, use `if grep ...; then ...; else ...; fi` and distinguish status 1 from an error.
`grep -q` can exit early. Its upstream producer in a large pipeline can then receive SIGPIPE.

<a id="поиск-файлов-с-необычными-именами"></a>
## Find files with unusual names

To count lines in `.log` files, including names such as `app log.txt`, pass the found paths as separate arguments.
Avoid parsing a text listing of names. The following fragment works on the current file tree.

```bash
find . -type f -name '*.log' -exec wc -l {} +
```

`wc` receives each complete file name, including spaces.
The traversal determines the output order.

`find . -type f -name '*.log' -print` selects names. Quotes prevent the shell from expanding the wildcard early.
Do not parse `ls` output or pass a newline-delimited list through `for file in $(...)`.
Prefer `find ... -exec command {} +` to pass names as arguments.
A matching `-print0` and `xargs -0` pair also preserves spaces and newlines in names.
Display the selected paths first, then decide separately whether to change or delete them.

| Task | GNU/Linux | BSD/macOS |
| --- | --- | --- |
| File metadata | `stat -c '%a %n' file` | `stat -f '%Lp %N' file` |
| Relative date | GNU `date -d 'yesterday'` | BSD `date -v-1d` |
| In-place sed | `sed -i 's/old/new/g' file` | `sed -i '' 's/old/new/g' file` |
| Formatted find | GNU `find ... -printf ...` | Usually no `-printf` |

These commands expose implementation differences and require verification when moving between operating systems.
For a portable transformation, write a new file, check it, and then replace the original.

<a id="источники"></a>
## Sources

[GNU Bash quoting/status](https://www.gnu.org/software/bash/manual/bash.html),
[Coreutils mktemp/cp/chmod](https://www.gnu.org/software/coreutils/manual/coreutils.html),
[Findutils](https://www.gnu.org/software/findutils/manual/html_node/index.html),
[Grep exit status](https://www.gnu.org/s/grep/manual/html_node/Exit-Status.html).
