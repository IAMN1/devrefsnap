<a id="linux-терминал-и-повседневные-задачи"></a>
# Linux terminal and everyday tasks

[Русский](../../../ru/systems/linux/README.md)

This reference covers basic file, permission, process, and network operations.
Use it to diagnose your Linux system and review commands before running them.
Separate recipes cover services and packages.
Linux is a kernel. The distribution, libc, shell, and installed utilities determine which commands are available.

<a id="быстрый-поиск"></a>
## Quick lookup

Each table entry is a separate operation on your own system.

| Task | Command | Details |
| --- | --- | --- |
| Check the directory or environment | `pwd`, `command -v bash`, `uname -s` | [Shell](shell-and-files.md) |
| Inspect files | `ls -la`, `find . -type f -name '*.log'` | [Files](shell-and-files.md) |
| Search lines | `grep -n 'ERROR' app.log` | [Search](shell-and-files.md#text-streams-and-exit-codes) |
| Copy or compare files | `cp source destination`, `cmp source destination` | [Practice script](shell-and-files.md#safe-practice-example) |
| Check the user or permissions | `id`, `ls -ld path`, `umask` | [Permissions](permissions-and-processes.md) |
| Take a process snapshot | `ps -ef`, `ps -p PID -o pid,ppid,stat,args` | [Processes](permissions-and-processes.md#processes-and-signals) |
| Inspect Linux IP addresses and routes | `ip -brief address`, `ip route` | [Networking](network-and-services.md) |
| Find the process listening on TCP port 8000 | `ss -lntp 'sport = :8000'` | [Command and PID](process-by-port.md#find-a-tcp-listener) · [Permissions](process-by-port.md#when-the-pid-is-missing) · [Namespaces](process-by-port.md#when-the-process-is-in-another-namespace) |
| Inspect a Linux systemd service | `systemctl status NAME.service` | [Services](network-and-services.md#systemd-services) |
| Read systemd logs | `journalctl -u NAME.service -n 50 --no-pager` | [Services](network-and-services.md#systemd-services) |

| Requirement | Value |
| --- | --- |
| Target environment | GNU/Linux, with Bash explicitly selected for shell examples |
| Prerequisites | An ordinary user account and terminal. Practice administrative operations on a separate training system |

<a id="навигация"></a>
## Navigation

- [Quick lookup](#quick-lookup)
- [Find your way around the shell](#find-your-way-around-the-shell)
- [Combine tools and check results](#combine-tools-and-check-results)
- [Diagnose the system layer by layer](#diagnose-the-system-layer-by-layer)
- [Common mistakes](#common-mistakes)
- [Sources](#sources)
- [Shell, files, and search](shell-and-files.md)
- [Permissions and processes](permissions-and-processes.md)
- [Networking, services, and packages](network-and-services.md)
- [Find a process by port](process-by-port.md)

<a id="базовый-уровень"></a>

<a id="ориентироваться-в-shell"></a>
## Find your way around the shell

`pwd` displays the current directory. `cd` changes it in the current shell.
Relative paths depend on that directory. `/` is the file system root, and `~` is the user's home directory.
`.` and `..` mean the current and parent directories.
Check the context before writing or deleting files. File names are not shell commands.

Bash, Zsh, and POSIX sh differ.
The complete script here starts with `#!/usr/bin/env bash`. Run it with `bash file.sh`.
Having `sh` available does not guarantee Bash. PowerShell and cmd.exe commands differ.
The [example](shell-and-files.md#safe-practice-example) creates files only in a new temporary directory.

<a id="средний-уровень"></a>

<a id="соединять-инструменты-и-проверять-результат"></a>
## Combine tools and check results

`"$variable"` preserves spaces and prevents another glob expansion.
Single quotes preserve literal text. Double quotes allow `$var` and `$(command)` substitutions.
A pipe passes stdout. Redirect stderr separately and check each command's exit status.
For example, grep returns 1 when it finds no matches. That outcome does not always mean the task failed.

[Permissions and processes](permissions-and-processes.md) explains `rwx`, umask, PIDs, signals, and waiting for a child process.
Avoid broad fixes such as assigning `777`, recursively changing ownership, or signaling every process with a matching name.

<a id="продвинутый-уровень"></a>

<a id="диагностировать-систему-по-слоям"></a>
## Diagnose the system layer by layer

Identify the operating system and utility versions first.
Then check the process, listener, route and DNS, and HTTP response in order.
For service problems, distinguish stopped, failed, enabled, and started states.
Package managers and init systems depend on the distribution. Some containers and Linux installations do not use systemd.
[Networking and operations](network-and-services.md) distinguishes inspection from changes.

macOS uses BSD variants of many utilities and launchd for service management.
Check GNU extensions such as `find -printf`, `stat -c`, `date -d`, and `readlink -f` when moving between operating systems.
Also check differences in `sed -i`.
Portable shell syntax does not make GNU flags and Linux services work on macOS.

<a id="частые-ошибки"></a>
## Common mistakes

| Symptom | Check |
| --- | --- |
| A file name with spaces became two arguments | Quotes around the path or variable |
| Permission denied after chmod | Directory traversal permissions, UID/GID, ACLs, SELinux/AppArmor, and mount flags |
| A command works in a terminal but fails in cron or a service | Shell, PATH, working directory, environment, and permissions |
| The port is open but HTTP does not respond | Process, bind address, protocol, firewall, proxy, and application logs |
| A service is enabled but not running | Enable configures startup dependencies or boot activation and need not start it now |
| `systemctl` fails inside a container | The container may not use systemd as its service manager |

<a id="источники"></a>
## Sources

- [GNU Bash](https://www.gnu.org/software/bash/manual/bash.html), [Coreutils](https://www.gnu.org/software/coreutils/manual/coreutils.html).
- [Findutils](https://www.gnu.org/software/findutils/manual/html_node/index.html), [Grep](https://www.gnu.org/software/grep/manual/grep.html).
- [Linux ps](https://man7.org/linux/man-pages/man1/ps.1.html), [ip](https://man7.org/linux/man-pages/man8/ip.8.html), [ss](https://man7.org/linux/man-pages/man8/ss.8.html).
- [systemctl](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html), [journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html).

[Operating systems catalog](../README.md)
