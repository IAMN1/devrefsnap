# Shell, файлы и поиск

Уровень: базовый и средний. Предпосылки: Bash, стандартные файловые утилиты, доступный temp-каталог.
[К справочнику Linux](README.md).

## Основные операции

Это отдельные справочные фрагменты, пути заменяй своими после проверки `pwd`:

| Задача | Фрагмент | Последствие |
| --- | --- | --- |
| Создать каталог | `mkdir -p project/data` | Создаёт недостающие каталоги |
| Записать текст | `printf '%s\n' 'hello' > note.txt` | `>` создаёт или перезаписывает файл |
| Дописать | `printf '%s\n' 'next' >> note.txt` | Дописывает в конец |
| Скопировать | `cp -i source.txt copy.txt` | `-i` спрашивает перед перезаписью в интерактивной shell |
| Переместить | `mv -i copy.txt archive.txt` | Меняет имя/расположение, может перезаписать адресат |
| Удалить файл | `rm -i -- archive.txt` | Удаляет имя файла; shell-корзины обычно нет |
| Удалить пустой каталог | `rmdir empty-dir` | Отказывает для непустого каталога |
| Посмотреть содержимое | `less note.txt`, `head -n 10 note.txt`, `tail -n 20 note.txt` | Чтение; `tail -f` продолжает ожидать новые строки |

Осторожно с glob: `rm *.log` расширяется shell до запуска rm. Для пути, начинающегося с дефиса,
используй `./-name` или поддерживаемый командой `--` перед операндами.
`ln -s TARGET LINK` создаёт символическую ссылку, а не копию; относительный TARGET вычисляется от каталога LINK.
Перед удалением/архивированием выясняй, как команда обрабатывает symlink.

## Безопасный практический пример

Полный скрипт: синтетические логи, путь с пробелом, поиск, архив и сравнение восстановленного файла.
Запуск: `bash example.sh`. Удаление ограничено каталогом, созданным `mktemp -d`.

<!-- example: linux/example.sh -->
```bash
#!/usr/bin/env bash
set -euo pipefail
task_dir=$(mktemp -d "${TMPDIR:-/tmp}/linux-files.XXXXXX")
trap 'rm -rf -- "$task_dir"' EXIT
mkdir "$task_dir/source" "$task_dir/restored"
printf 'INFO started\nERROR missing\nINFO done\n' > "$task_dir/source/app log.txt"
cp "$task_dir/source/app log.txt" "$task_dir/source/copy.txt"
cmp "$task_dir/source/app log.txt" "$task_dir/source/copy.txt"
mv "$task_dir/source/copy.txt" "$task_dir/source/renamed.txt"
test "$(grep -c '^INFO' "$task_dir/source/app log.txt")" -eq 2
test "$(awk '$1 == "ERROR" {print $2}' "$task_dir/source/app log.txt")" = missing
find "$task_dir/source" -type f -name '*.txt' -exec wc -l {} +
tar -cf "$task_dir/logs.tar" -C "$task_dir" source
tar -xf "$task_dir/logs.tar" -C "$task_dir/restored"
cmp "$task_dir/source/app log.txt" "$task_dir/restored/source/app log.txt"
gzip -c "$task_dir/source/app log.txt" > "$task_dir/log.txt.gz"
gzip -cd "$task_dir/log.txt.gz" | cmp "$task_dir/source/app log.txt" -
chmod u=rw,go= "$task_dir/source/app log.txt"
printf 'files OK\n'
```

Ожидается `files OK`; строки `wc` зависят от случайного temp-пути. Проверено на macOS с BSD-утилитами;
это переносимое подмножество, а не проверка GNU/Linux. Не распаковывай недоверенный архив
в важный каталог: сначала просмотри `tar -tf archive.tar`, оцени пути/ссылки и выбери изолированный каталог.

## Текст, потоки и коды выхода

Фрагменты: читают указанный файл и формируют вывод; `2>` перезапишет лог ошибок.

```bash
grep -n -E 'ERROR|WARN' app.log
sed -n '1,20p' app.log
awk '{print $1}' app.log | sort | uniq -c
grep 'ERROR' app.log > output.txt 2> error.txt
```

Последняя строка сохраняет найденные строки и диагностику отдельно; предполагается существующий `app.log`.
`2>&1` направляет stderr в текущее назначение stdout; порядок `>file 2>&1` имеет значение.
Пайп `cmd | tee output.txt` обычно сообщает статус последней команды; в Bash `set -o pipefail`
учитывает неуспех любой команды пайпа. `set -e` имеет исключения и не заменяет явную обработку ожидаемых статусов.

GNU grep: 0 — совпадение, 1 — нет совпадения, 2 — ошибка; другие реализации могут иметь дополнительные коды ошибки.
Для ожидаемого отсутствия строки используй `if grep ...; then ...; else ...; fi`, различая код 1 и ошибку.
`grep -q` может завершиться рано: producer в большом пайпе способен получить SIGPIPE.

## Поиск файлов с необычными именами

`find . -type f -name '*.log' -print` выбирает имена; кавычки не дают shell раскрыть wildcard заранее.
Не разбирай вывод `ls` и не передавай newline-список в `for file in $(...)`.
Для обработки аргументами предпочтительнее `find ... -exec command {} +`; альтернативно
совместимая пара `-print0` / `xargs -0` сохраняет пробелы и переводы строк в именах.
Сначала выведи выбранные пути, затем отдельно принимай решение об изменении/удалении.

| Задача | GNU/Linux | BSD/macOS |
| --- | --- | --- |
| Метаданные файла | `stat -c '%a %n' file` | `stat -f '%Lp %N' file` |
| Дата относительно текущей | GNU `date -d 'yesterday'` | BSD `date -v-1d` |
| In-place sed | `sed -i 's/old/new/g' file` | `sed -i '' 's/old/new/g' file` |
| Форматированный find | GNU `find ... -printf ...` | Обычно нет `-printf` |

Это различия реализаций, не переносимые команды; Linux-only/GNU варианты здесь не выполнялись.
Для переносимого преобразования проще записать новый файл, проверить его и только затем заменить исходный.

## Источники

[GNU Bash quoting/status](https://www.gnu.org/software/bash/manual/bash.html),
[Coreutils mktemp/cp/chmod](https://www.gnu.org/software/coreutils/manual/coreutils.html),
[Findutils](https://www.gnu.org/software/findutils/manual/html_mono/find.html),
[Grep exit status](https://www.gnu.org/s/grep/manual/html_node/Exit-Status.html).
Сверка: 2026-11-06. Выполнен только полный temp-скрипт на macOS; GNU/BSD различия приведены справочно.
