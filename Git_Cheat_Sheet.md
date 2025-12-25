# Git Cheat Sheet

## Основные команды

### Настройка
```bash
git config --global user.name "Имя"
git config --global user.email "email@example.com"
git config --global core.editor "nano"
git config --list  # Показать настройки
```

### Создание и клонирование
```bash
git init                      # Инициализировать репозиторий
git clone <url>               # Клонировать удаленный репозиторий
```

### Основной рабочий процесс
```bash
git status                    # Показать состояние файлов
git add <file>                # Добавить файл в staging
git add .                     # Добавить все изменения
git commit -m "Сообщение"     # Закоммитить изменения
git commit --amend            # Изменить последний коммит
```

### Ветвление
```bash
git branch                    # Показать ветки
git branch <name>             # Создать ветку
git checkout <branch>         # Переключиться на ветку
git checkout -b <branch>      # Создать и переключиться
git merge <branch>            # Влить ветку в текущую
git branch -d <branch>        # Удалить ветку
```

### Отслеживание изменений
```bash
git diff                      # Показать непроиндексированные изменения
git diff --staged             # Показать проиндексированные изменения
git log                       # Показать историю коммитов
git log --oneline             # Компактная история
git log --graph               # История с графиком ветвления
```

### Удаленные репозитории
```bash
git remote add origin <url>   # Добавить удаленный репозиторий
git push -u origin main       # Отправить изменения (первый раз)
git push                      # Отправить изменения
git pull                      # Загрузить изменения
git fetch                     # Загрузить без слияния
git remote -v                 # Показать удаленные репозитории
```

### Отмена изменений
```bash
git reset HEAD <file>         # Убрать файл из staging
git checkout -- <file>        # Отменить изменения в файле
git reset --soft HEAD~1       # Отменить коммит, сохранив изменения
git reset --hard HEAD~1       # Полностью удалить последний коммит
git revert <commit>           # Создать коммит, отменяющий изменения
```

### Сохранение временных изменений
```bash
git stash                     # Сохранить временные изменения
git stash pop                 # Восстановить последние stash
git stash list                # Показать stash список
git stash drop                # Удалить последний stash
```

## Полезные алиасы (добавить в ~/.gitconfig)
```ini
[alias]
    co = checkout
    ci = commit
    br = branch
    st = status
    lg = log --oneline --graph --all
    last = log -1 HEAD
    unstage = reset HEAD --
```

## Рабочие процессы

### Стандартный процесс
1. `git pull` - получить свежие изменения
2. Внести изменения в код
3. `git add <files>` - добавить изменения
4. `git commit -m "message"` - закоммитить
5. `git push` - отправить на сервер

### Работа с ветками
```bash
# Создать ветку для новой фичи
git checkout -b feature/new-feature

# Работать, коммитить...
git add .
git commit -m "Add new feature"

# Переключиться на main и обновить
git checkout main
git pull origin main

# Слить изменения
git merge feature/new-feature
git push origin main

# Удалить ветку
git branch -d feature/new-feature
```

## Частые проблемы и решения

### Обновить fork с оригинального репозитория
```bash
git remote add upstream <original-repo-url>
git fetch upstream
git merge upstream/main
```

### Исправить последний коммит
```bash
# Внести изменения в файлы
git add .
git commit --amend
# Затем принудительный push, если уже отправляли:
git push --force-with-lease
```

### Удалить файл из git, но оставить локально
```bash
git rm --cached <file>
```

## Полезные советы
- Всегда делайте `git pull` перед началом работы
- Пишите понятные сообщения коммитов
- Чаще коммитьте - маленькими порциями
- Используйте `.gitignore` для служебных файлов
- Перед мержем проверяйте изменения через `git diff`

---
