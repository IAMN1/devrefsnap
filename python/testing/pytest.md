# Pytest Шпаргалка 🚀

## Содержание
- [Основы](#основы)
- [Структура тестов](#структура-тестов)
- [Фикстуры](#фикстуры)
- [Параметризация](#параметризация)
- [Маркеры](#маркеры)
- [Проверки (Assertions)](#проверки-assertions)
- [Моки и стабы](#моки-и-стабы)
- [Плагины](#плагины)
- [Примеры](#примеры)
- [Полезные команды](#полезные-команды)

---

## Основы

### Установка
```bash
pip install pytest
pip install pytest-cov pytest-xdist pytest-mock pytest-asyncio
```

### Простейший тест
```python
# test_example.py
def test_addition():
    assert 1 + 1 == 2

def test_list_contains():
    fruits = ["apple", "banana", "orange"]
    assert "apple" in fruits
```

### Запуск тестов
```bash
# Все тесты в директории
pytest

# Конкретный файл
pytest test_file.py

# Конкретный тест
pytest test_file.py::TestClass::test_method

# С выводом подробной информации
pytest -v

# С выводом print() из тестов
pytest -s

# Остановка после первого упавшего теста
pytest -x

# Запуск только упавших тестов
pytest --lf
```

---

## Структура тестов

### Именование
- Файлы: `test_*.py` или `*_test.py`
- Функции: `test_*`
- Классы: `Test*`

### Организация тестов
```python
# Простая функция
def test_function():
    ...

# Класс с тестами
class TestFeature:
    def test_method(self):
        ...
    
    def test_another_method(self):
        ...
    
    # Тест с ожидаемым исключением
    def test_exception(self):
        with pytest.raises(ValueError):
            function_that_raises()
    
    # Тест с сообщением об ошибке
    def test_with_message(self):
        result = calculate()
        assert result == expected, f"Expected {expected}, got {result}"
```

### conftest.py
Файл для общих фикстур (автоматически обнаруживается pytest):
```python
# conftest.py
import pytest

@pytest.fixture
def shared_resource():
    return SomeResource()
```

---

## Фикстуры

### Базовые фикстуры
```python
import pytest

@pytest.fixture
def database_connection():
    # Setup
    conn = create_connection()
    yield conn  # Возвращаем значение тесту
    # Teardown
    conn.close()

def test_query(database_connection):
    result = database_connection.query("SELECT 1")
    assert result == 1
```

### Фикстуры с параметрами
```python
@pytest.fixture(params=["mysql", "postgres", "sqlite"])
def database(request):
    return create_db(request.param)

def test_database(database):
    assert database.is_connected()
```

### Автоиспользование фикстур
```python
@pytest.fixture(autouse=True)
def setup_teardown():
    print("\nSetup")
    yield
    print("\nTeardown")
```

### Область видимости фикстур
```python
@pytest.fixture(scope="function")   # По умолчанию - для каждой функции
@pytest.fixture(scope="class")      # Один раз для класса
@pytest.fixture(scope="module")     # Один раз для модуля
@pytest.fixture(scope="session")    # Один раз для сессии
```

### Встроенные фикстуры
```python
def test_temp_dir(tmp_path):
    # tmp_path - временная директория
    file = tmp_path / "test.txt"
    file.write_text("Hello")
    assert file.read_text() == "Hello"

def test_capsys(capsys):
    print("Hello World")
    captured = capsys.readouterr()
    assert captured.out == "Hello World\n"
```

---

## Параметризация

### Параметризация тестов
```python
import pytest

@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_multiply_by_two(input, expected):
    assert input * 2 == expected

# Несколько параметров
@pytest.mark.parametrize("a", [1, 2])
@pytest.mark.parametrize("b", [3, 4])
def test_multiple_params(a, b):
    assert a + b == a + b
```

### Параметризация через фикстуры
```python
@pytest.fixture(params=[0, 1, 2])
def number(request):
    return request.param

def test_number(number):
    assert number >= 0
```

---

## Маркеры

### Создание и использование маркеров
```python
# conftest.py
import pytest

def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )

# test_file.py
@pytest.mark.slow
def test_expensive_operation():
    ...

@pytest.mark.integration
def test_integration():
    ...

@pytest.mark.skip(reason="Not implemented yet")
def test_unimplemented():
    ...

@pytest.mark.skipif(sys.version_info < (3, 8), 
                    reason="Requires Python 3.8+")
def test_python38_feature():
    ...

@pytest.mark.xfail(reason="Known bug #123")
def test_buggy_feature():
    ...
```

### Запуск по маркерам
```bash
# Только быстрые тесты
pytest -m "not slow"

# Только интеграционные
pytest -m integration

# Пропущенные тесты
pytest -rs  # показать reason для skipped
```

---

## Проверки (Assertions)

### Базовые утверждения
```python
assert condition
assert expression == expected
assert value in collection
assert value not in collection
assert collection1 == collection2
```

### Сравнение с плавающей точкой
```python
import math

# Без учета погрешности
assert 0.1 + 0.2 == 0.3  # Может упасть!

# С учетом погрешности
assert math.isclose(0.1 + 0.2, 0.3)
assert 0.1 + 0.2 == pytest.approx(0.3)
assert 0.1 + 0.2 == pytest.approx(0.3, rel=1e-9)
```

### Проверка исключений
```python
import pytest

# Проверка типа исключения
with pytest.raises(ValueError):
    int("not a number")

# Проверка сообщения об ошибке
with pytest.raises(ValueError, match="invalid literal"):
    int("abc")

# Получение объекта исключения
with pytest.raises(ValueError) as exc_info:
    int("abc")
assert "invalid literal" in str(exc_info.value)
```

### Проверка предупреждений
```python
import warnings
import pytest

def test_warning():
    with pytest.warns(UserWarning, match="deprecated"):
        warnings.warn("This is deprecated", UserWarning)
```

---

## Моки и стабы

### Использование pytest-mock
```python
import pytest

def test_with_mock(mocker):
    # Мок функции
    mock_func = mocker.Mock(return_value=42)
    assert mock_func() == 42
    
    # Проверка вызовов
    mock_func.assert_called_once()
    
    # Мок объекта
    obj = mocker.Mock()
    obj.method.return_value = "mocked"
    assert obj.method() == "mocked"
    
    # Мок патч
    mocker.patch("module.function", return_value=100)
```

### Примеры использования
```python
def test_api_call(mocker):
    # Мокаем HTTP-запрос
    mock_get = mocker.patch("requests.get")
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"key": "value"}
    mock_response.status_code = 200
    mock_get.return_value = mock_response
    
    # Вызываем тестируемую функцию
    result = make_api_call()
    
    # Проверяем
    assert result == {"key": "value"}
    mock_get.assert_called_once_with("https://api.example.com")
```

---

## Плагины

### Популярные плагины
```bash
# Покрытие кода
pip install pytest-cov
pytest --cov=my_module --cov-report=html

# Параллельный запуск
pip install pytest-xdist
pytest -n 4  # 4 процесса

# Интерактивный дебаг
pip install pytest-ipdb

# Порядок выполнения
pip install pytest-order

# Параметризация из файлов
pip install pytest-cases
```

### Настройка через pytest.ini
```ini
[pytest]
# Настройки маркеров
markers =
    slow: marks tests as slow
    integration: integration tests
    unit: unit tests
    
# Пути к тестам
testpaths = tests

# Сопоставление имен файлов
python_files = test_*.py *_test.py

# Минимальная версия Python
minversion = 6.0

# Опции по умолчанию
addopts = -v --tb=short

# Игнорируемые директории
norecursedirs = .git __pycache__ build dist

# Покрытие кода
filterwarnings =
    ignore::DeprecationWarning
```

---

## Примеры

### Полный пример теста
```python
import pytest

# Фикстура
@pytest.fixture
def sample_data():
    return {"key": "value"}

# Маркер
@pytest.mark.integration
# Параметризация
@pytest.mark.parametrize("input_val,expected", [
    (1, 2),
    (5, 10),
])
def test_example(sample_data, input_val, expected):
    """Тест с фикстурой, параметрами и маркером."""
    
    # Arrange
    calculator = Calculator()
    
    # Act
    result = calculator.multiply_by_two(input_val)
    
    # Assert
    assert result == expected
    assert sample_data["key"] == "value"
    
    # Проверка исключения
    with pytest.raises(ValueError):
        calculator.multiply_by_two(None)
```

### Тестирование Django/Flask
```python
# Django
@pytest.fixture
def client():
    from django.test import Client
    return Client()

def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200

# Flask
@pytest.fixture
def app():
    from myapp import create_app
    app = create_app()
    app.config["TESTING"] = True
    return app

def test_api(client):
    response = client.get("/api/data")
    assert response.json == {"status": "ok"}
```

### Асинхронные тесты
```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == expected
```

---

## Полезные команды

### Запуск и отладка
```bash
# Запуск с отчетом
pytest --tb=auto      # автоматический формат
pytest --tb=short     # короткий формат
pytest --tb=line      # только одна строка на тест
pytest --tb=no        # без traceback

# Покрытие кода
pytest --cov=myapp --cov-report=term-missing
pytest --cov=myapp --cov-report=html

# Профилирование
pytest --durations=10  # 10 самых медленных тестов

# Параллельный запуск
pytest -n auto  # автоматическое определение числа ядер

# Фильтрация тестов
pytest -k "test_add"      # тесты с "add" в имени
pytest -k "not slow"      # исключить медленные
```

### Полезные флаги
```bash
--collect-only           # Показать какие тесты будут запущены
--lf, --last-failed      # Запустить только упавшие
--ff, --failed-first     # Сначала упавшие
--sw, --stepwise         # Остановка на первом упавшем тесте
--pdb                    # Запуск pdb при падении теста
--trace                  # Войти в pdb в начале каждого теста
```

### Интеграция с CI/CD
```bash
# Генерация JUnit отчета
pytest --junitxml=report.xml

# Генерация JSON отчета
pytest --json=report.json

# Минимальный вывод для CI
pytest -q --tb=no
```

---

## Советы и лучшие практики

### 1. **Один assert на тест**
```python
# Хорошо
def test_user_creation():
    user = create_user("test")
    assert user.username == "test"
    assert user.is_active == True
    assert user.created_at is not None

# Еще лучше (разделить на несколько тестов)
def test_user_username():
    user = create_user("test")
    assert user.username == "test"

def test_user_active_by_default():
    user = create_user("test")
    assert user.is_active == True
```

### 2. **Именование тестов**
```python
# Плохо
def test1():
    ...

# Хорошо
def test_create_user_with_valid_data():
    ...

def test_login_fails_with_wrong_password():
    ...

# Отличное
def test_given_valid_credentials_when_login_then_success():
    # given - подготовка
    # when - действие
    # then - проверка
    ...
```

### 3. **Тестируйте поведение, а не реализацию**
```python
# Плохо (тестирует реализацию)
def test_calls_database():
    mock_db = Mock()
    service = Service(mock_db)
    service.process()
    assert mock_db.query.call_count == 3  # Хрупкий тест!

# Хорошо (тестирует поведение)
def test_returns_expected_data():
    service = Service()
    result = service.process()
    assert result == expected_data
```

### 4. **Используйте фабрики**
```python
# Фабрика для тестовых данных
@pytest.fixture
def user_factory():
    def create_user(**overrides):
        defaults = {
            "username": "testuser",
            "email": "test@example.com",
            "is_active": True,
        }
        defaults.update(overrides)
        return User(**defaults)
    return create_user

def test_user_creation(user_factory):
    user = user_factory(username="alice")
    assert user.username == "alice"
```

### 5. **Чистые тесты**
```python
# Каждый тест должен быть независимым
# Не полагайтесь на порядок выполнения
# Не изменяйте глобальное состояние
```

---

## Шаблон проекта
```
project/
├── src/
│   └── myapp/
│       ├── __init__.py
│       ├── module1.py
│       └── module2.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_module1.py
│   ├── test_module2.py
│   └── integration/
│       └── test_api.py
├── pytest.ini
└── requirements.txt
```

## Ресурсы
- [Официальная документация](https://docs.pytest.org/)
- [Pytest with plugins](https://github.com/pytest-dev/pytest/)
- [Awesome Pytest](https://github.com/augustogoulart/awesome-pytest)

---