<a id="проверить-модель-и-сериализовать-данные"></a>
# Validate a model and serialize data

[Русский](../../../../ru/python/validation/pydantic/models.md)

Use this page to validate input, check related fields, and produce public JSON.
The complete files expand the [Pydantic quick reference](README.md).

| Task | Technique | Example or details |
| --- | --- | --- |
| Validate a dictionary and output JSON | `BaseModel`, aliases, validators | [Models and tests](#models-validation-and-json) |
| Keep a password out of public output | Separate output model | [UserInput and PublicUser](#models-validation-and-json) |
| Read attributes and constrain types | `from_attributes`, strict, frozen | [Types and tests](#attributes-configuration-and-types) |

[Reference](README.md) · [Advanced tasks](advanced.md)

The level is basic to intermediate.
Prerequisites include classes, types, Decimal, and JSON.
Place all files below in one practice directory.
Use Python 3.14.
Run `python -m pip install 'pydantic[email]==2.14.3' 'email-validator==2.3.0' 'pytest==9.2.0'`.

<a id="модели-валидация-и-json"></a>
## Models, validation, and JSON

The complete `demo_models.py` uses separate models for user input and public output.
It leaves the password out of the response.

[`pydantic/demo_models.py`](../../../../../examples/python/validation/pydantic/demo_models.py)

Run `python demo_models.py`.
The result contains user JSON without a password.
The product's `final_price` is `"0"`.
`model_dump()` preserves Decimal.
`mode="json"` produces its JSON-compatible string representation.
Use `include`, `exclude`, `exclude_unset`, or `exclude_none` for selective output.
Input rules remain the same.
Serialized output that omits required fields may fail validation by the original input model.

The `created_at` field uses `AwareDatetime` to require a time zone.
The model rejects a value without an offset.
It serializes `2026-11-06T12:00:00+03:00` as `2026-11-06T09:00:00Z`.
The conversion is independent of the machine's local time zone.
Output has second precision.

Complete `test_models.py` follows.

[`pydantic/test_models.py`](../../../../../examples/python/validation/pydantic/test_models.py)

<a id="атрибуты-конфигурация-и-типы"></a>
## Attributes, configuration, and types

The complete `demo_types.py` reads ORM-like objects without a database connection.
For SQLAlchemy, see its [recipes](../../databases/sqlalchemy/README.md).

[`pydantic/demo_types.py`](../../../../../examples/python/validation/pydantic/demo_types.py)

Complete `test_types.py` follows.

[`pydantic/test_types.py`](../../../../../examples/python/validation/pydantic/test_types.py)

Run all tests on this page with `python -m pytest -q test_models.py test_types.py`.
Expect successful validation of valid values and rejection of the listed invalid values.
You can constrain a phone number with `Field(pattern=r'^\+?[1-9][0-9]{1,14}$')`.
This pattern checks syntax. Verify the existence of a number separately.
After installing `pydantic-extra-types`, import `PaymentCardNumber` from `pydantic_extra_types.payment` in new examples.
Keep payment data out of logs when validating its type.

See [validators](https://pydantic.dev/docs/validation/latest/concepts/validators/), [serializers](https://pydantic.dev/docs/validation/latest/concepts/serialization/), [ConfigDict](https://pydantic.dev/docs/validation/latest/api/pydantic/config/), [standard types](https://pydantic.dev/docs/validation/latest/api/pydantic/standard_library_types/), and [PaymentCardNumber](https://pydantic.dev/docs/validation/latest/api/pydantic-extra-types/pydantic_extra_types_payment/).
