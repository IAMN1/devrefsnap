# Django

[Русский](../../../../ru/python/web/django/README.md)

Django maps Python models to database tables and provides a built-in admin interface for managing records. In this example, you add a sample book to a local SQLite database and verify the workflow with tests.

| Task | Tool | Example |
| --- | --- | --- |
| Define a book and create its table | `models.Model`, `migrate` | [Model and migration](#model-and-migration) |
| Add a book in the browser | `admin.site.register`, `createsuperuser` | [Admin interface](#admin-interface) |
| Verify access and storage | `TestCase`, `manage.py test` | [Tests](#tests) |

## Setup

Use Python 3.14 and Django 5.2.19 from the 5.2 LTS series for the [example project](../../../../../examples/python/web/django/manage.py). SQLite is available through Python's `sqlite3` module.

On macOS or Linux, open a terminal in the repository root. Change to the example directory, create and activate a virtual environment, and install the dependencies.

```bash
cd examples/python/web/django
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Run the remaining commands from this directory with the virtual environment active.

## Model and migration

The [`Book` model](../../../../../examples/python/web/django/catalog/models.py) defines a book with a `title` field. The [initial migration](../../../../../examples/python/web/django/catalog/migrations/0001_initial.py) describes how to create the table for this model. The [project settings](../../../../../examples/python/web/django/config/settings.py) enable the `catalog` app and set `db.sqlite3` as the database file.

Apply the migrations provided with the example. Then check the migration status for the `catalog` app.

```bash
python manage.py migrate
python manage.py showmigrations catalog
```

On the first run, `migrate` creates `db.sqlite3` and its tables, including the user and book tables. The `showmigrations` output should include `[X] 0001_initial`.

If you change the model, create a new migration.

```bash
python manage.py makemigrations catalog
```

Open the generated migration and review its operations. If the migration removes a field, applying it drops the column and its stored values. Apply the reviewed migration to the practice database.

```bash
python manage.py migrate
```

## Admin interface

[Registering `Book`](../../../../../examples/python/web/django/catalog/admin.py) adds a book form and list to the built-in admin interface. The [project URL configuration](../../../../../examples/python/web/django/config/urls.py) mounts the admin interface at `/admin/`.

Create a superuser for this example. Enter a username and password for the example when prompted. You can leave the email address blank.

```bash
python manage.py createsuperuser
```

Start the development server on the loopback address. Use these settings and `runserver` only for local development with sample data.

```bash
python manage.py runserver 127.0.0.1:8000
```

1. Open the [admin interface](http://127.0.0.1:8000/admin/) and sign in with the account you created.
2. Open `Books` and click `Add book`.
3. Enter `Demo Book` in the `Title` field.
4. Click `Save`. `Demo Book` appears in the list.

Press `Ctrl+C` to stop the server.

## Tests

Check for model changes that need migrations. Then run the [admin tests](../../../../../examples/python/web/django/catalog/tests.py).

```bash
python manage.py makemigrations --check --dry-run
python manage.py test catalog
```

The first command prints `No changes detected`. The second command runs two tests and ends with `OK`.

The first test checks that an anonymous visitor who opens the add form is redirected to the login page. The second test submits the form as a superuser and checks that the book is saved. `force_login()` creates a superuser session without checking a password.

Django runs the tests without `runserver` and creates a separate in-memory SQLite database. The book you added manually remains in `db.sqlite3`.

## Sources

- [Django 5.2 models, migrations, and admin tutorial](https://docs.djangoproject.com/en/5.2/intro/tutorial02/)
- [Django 5.2 `manage.py` commands](https://docs.djangoproject.com/en/5.2/ref/django-admin/)
- [Django 5.2 test runner and test database](https://docs.djangoproject.com/en/5.2/topics/testing/overview/)
- [Django 5.2 test client and `force_login()`](https://docs.djangoproject.com/en/5.2/topics/testing/tools/#the-test-client)
- [Django 5.2.19 release notes](https://docs.djangoproject.com/en/5.2/releases/5.2.19/)
