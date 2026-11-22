<a id="проверить-пароль-и-защитить-маршрут-jwt"></a>
# Verify a password and protect a route with JWT

[Русский](../../../../ru/python/web/fastapi/authentication.md)

Use this page to reproduce local password verification, JWT issuance, and protected-route rejection.
The recipe targets one practice service and a trusted password-flow client.

| Task | Technique | Example / details |
| --- | --- | --- |
| Prepare the key and packages | Random key in the environment | [Setup](#setup) |
| Issue and verify a JWT | Argon2, `OAuth2PasswordBearer`, `jwt.decode` | [Complete application](#complete-example) |
| Check access and rejection | POST `/token`, GET `/users/me` | [Result](#run-and-inspect-the-result) · [Tests](testing.md#authentication) |
| Assess the recipe's scope | Keys, HTTPS, revocation, roles | [Limitations](#limitations-and-next-tasks) |

[Quick reference](README.md) · [Access-rejection tests](testing.md#authentication)

| Parameter | Value |
| --- | --- |
| Level | Advanced |
| Prerequisites | HTTP Authorization, dependencies, environment variables, hashing basics, and JWT |

The practice scenario follows login/password form → Argon2 hash verification → short-lived JWT → JWT and user verification on a protected route.
This is a minimal local demonstration.
OAuth2 password flow requires a trusted client.
An external login provider for arbitrary applications requires a separate solution.

<a id="подготовка"></a>
## Setup

Use Python 3.14.

Run the following in a separate virtual environment.

```bash
python -m pip install 'fastapi==0.165.0' 'uvicorn[standard]==0.54.0' python-multipart PyJWT 'pwdlib[argon2]'
export JWT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
```

The key is generated locally for the practice run.
Keep the key out of source code.
Use the same key in all processes of one application.
A new key after restart invalidates earlier tokens.

<a id="полный-пример"></a>
## Complete example

Save the complete example in `auth_app.py`.
The practice user is `alice`.
The practice password is `training-password-123`.
The password is shown openly only to make the example reproducible.
The dictionary stores the password hash.

[`auth_app.py`](../../../../../examples/python/web/fastapi/auth_app.py)

Password hashing consumes CPU time.
The example therefore uses synchronous functions.
FastAPI runs the `def` handler and `def` dependency in a thread pool.
The dummy hash keeps hash-verification work for an unknown username.
This technique does not promise identical HTTP response times.

<a id="запуск-и-результат"></a>
## Run and inspect the result

```bash
uvicorn auth_app:app --reload
```

Use another terminal for the following commands.

```bash
curl -i -X POST http://127.0.0.1:8000/token -d 'username=alice&password=training-password-123'
curl -i http://127.0.0.1:8000/users/me
```

The first request returns `200`, `access_token`, and `token_type=bearer`.
The second request returns `401`.
In curl, pass the issued token in the `Authorization: Bearer <token>` header.
The `/users/me` route returns `{"username":"alice"}`.
In Swagger UI at `/docs`, click **Authorize**.
Enter the practice username and password.
The UI obtains a token from `/token`.
The UI then supplies the header.
An incorrect password returns `401`.
A corrupted or expired token returns `401`.
A missing required `exp` returns `401`.
An unknown user returns `401`.
The [tests](testing.md#authentication) check these cases without starting an HTTP server.

<a id="ограничения-и-следующие-задачи"></a>
## Limitations and next tasks

- JWT signing leaves the token payload readable. Keep passwords and other secrets out of the payload. The server sets the algorithm. The server must not choose an algorithm from an unverified token header.
- The demo dictionary and hash are created at import time for one known user. Real hashes belong in a database. The client never receives `password_hash`.
- Production requires HTTPS, password-guessing limits, key management, token revocation/refresh policies, and permission checks. With multiple consumers or issuers, configure `aud` and `iss` as well. This example has one application, so it omits `aud` and `iss`.
- Registration, password recovery, refresh tokens, and complete external OAuth/OIDC provider integration are outside the recipe's scope. Adding them requires a separate threat model and requirements.

Sources include [FastAPI passwords, hashing, and JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/), [PyJWT exp verification and required claims](https://pyjwt.readthedocs.io/en/stable/usage.html), [PyJWT decode and algorithms](https://pyjwt.readthedocs.io/en/stable/api.html#jwt.decode), and [pwdlib basic API](https://frankie567.github.io/pwdlib/guide/).
