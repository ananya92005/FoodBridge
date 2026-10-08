# FoodBridge Backend

FoodBridge is a Django REST API.

## Run locally on macOS

From the repository root, create a virtual environment and install dependencies:

```sh
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export USE_SQLITE_DEV=1 USE_INMEMORY_CHANNELS=1 CELERY_TASK_ALWAYS_EAGER=1
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

The API runs on port `8000`. The virtual environment only needs to be created and the dependencies installed once.

For a mobile device on the same Wi-Fi, set the app's API base URL to `http://<computer-LAN-IP>:8000`. `localhost` on the phone points to the phone itself. Use your emulator's host address when running in an emulator.

The local server listens on the LAN for development; don't expose it to the public internet.

Login at `POST /api/auth/login/` with `email` and `password`. Use the returned access token on protected requests as `Authorization: Bearer <access-token>`. Refresh it with `POST /api/auth/refresh/` and the `refresh` token.

## API routes

Open `http://localhost:8000/` or `http://localhost:8000/api/` for the exact endpoints and HTTP methods. For example, food listings are at `/api/food/listings/`, and login is `POST /api/auth/login/`.

Most endpoints require a bearer token from login. Send it as `Authorization: Bearer <access-token>`.

## Check the APIs

From the `backend` directory, run:

```sh
env USE_SQLITE_DEV=1 USE_INMEMORY_CHANNELS=1 CELERY_TASK_ALWAYS_EAGER=1 python manage.py test test_api
```
# FoodBridge
