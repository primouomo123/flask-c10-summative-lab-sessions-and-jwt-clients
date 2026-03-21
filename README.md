# Flask Expense Tracker API

## Project Description
A RESTful API for managing user accounts and personal expenses, built with Flask, SQLAlchemy, Flask-JWT-Extended, and Marshmallow. The API supports user registration, authentication (JWT), and CRUD operations for expense tracking. It is designed for use of JWT-based client application.

## Installation Instructions
1. **Clone the repository**
2. **Install dependencies and enter the virtual environment:**
   ```bash
   pipenv install
   pipenv shell
   ```
3. **Environment variables:**
   - The .env file should not be in GitHub because it contains sensitive information, however, it's here for being a school project.

4. **Run database migrations:**
   ```bash
   cd server
   flask db upgrade
   ```
5. **Seed the database:**
   From the `/server` directory run:
   ```bash
   python seed.py
   ```

## Run Instructions
From the `/server` directory, start the Flask server:
```bash
python app.py
```

The API will be available at `http://localhost:5555/`.

## API Endpoints

### Auth & User
- `POST /signup` — Register a new user. Requires `username` and `password` in JSON body. Returns JWT token and user info.
- `POST /login` — Authenticate user. Requires `username` and `password` in JSON body. Returns JWT token and user info.
- `GET /me` — Get current user info (requires JWT in Authorization header).

### Expenses
- `GET /expenses` — List current user's expenses (paginated). Query params: `page`, `per_page`.
- `POST /expenses` — Create a new expense. Requires `amount`, `description`, `category` in JSON body.
- `GET /expenses/<id>` — Get a specific expense by ID (must belong to current user).
- `PATCH /expenses/<id>` — Update an expense (fields: `amount`, `description`, `category`) (must belong to current user).
- `DELETE /expenses/<id>` — Delete an expense by ID (must belong to current user).

#### Expense Fields
- `amount` (float, required, >0)
- `description` (string, required, min 5 chars)
- `category` (string, one of: Food, Transportation, Entertainment, Utilities, Other)

All endpoints (except `/signup` and `/login`) require a valid JWT in the `Authorization: Bearer <token>` header.

## Curl Examples to Test the API:
1. **Sign Up a New User:**
    ```bash
    curl -X POST http://localhost:5555/signup \
    -H "Content-Type: application/json" \
    -d '{"username": "testuser", "password": "TestPassword123"}'
    ```

2. **Log In and Get a JWT Token:**
    ```bash
    curl -X POST http://localhost:5555/login \
    -H "Content-Type: application/json" \
    -d '{"username": "testuser", "password": "TestPassword123"}'
    ```

3. **Get the current user Info (replace <TOKEN> with your JWT):**
    ```bash
    curl -X GET http://localhost:5555/me \
    -H "Authorization: Bearer <TOKEN>"
    ```

4. **Create a New Expense (replace <TOKEN> with your JWT):**
    ```bash
    curl -X POST http://localhost:5555/expenses \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer <TOKEN>" \
    -d '{"amount": 25.50, "description": "Test expense", "category": "Food"}'
    ```

5. **Get All Expenses (replace <TOKEN> with your JWT):**
    curl -X GET http://localhost:5555/expenses \
    -H "Authorization: Bearer <TOKEN>"

6. **Get All Expenses using the pagination parameters (replace <PAGE_NUMBER> with the actual page number, replace <ITEMS_PER_PAGE> with the desired number of items per page, and replace <TOKEN> with your JWT):**
    curl -X GET "http://localhost:5555/expenses?page=<PAGE_NUMBER>&per_page=<ITEMS_PER_PAGE>" \
    -H "Authorization: Bearer <TOKEN>"

Please keep the quotes in the url above, so it works (because of the pagination special characters)

6. **Get a Specific Expense (replace <EXPENSE_ID> with the actual expense id> and replace <TOKEN> with your JWT):**:
    ```bash
    curl -X GET http://localhost:5555/expenses/<EXPENSE_ID> \
    -H "Authorization: Bearer <TOKEN>"
    ```

7. **Update a Specific Expense (replace <EXPENSE_ID> with the actual expense id> and replace <TOKEN> with your JWT):**
    ``bash
    curl -X PATCH http://localhost:5555/expenses/<EXPENSE_ID> \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer <TOKEN>" \
    -d '{"amount": 42.00, "description": "Updated expense", "category": "Utilities"}'
    ```

8. **Delete a Specific Expense (DELETE) (replace <EXPENSE_ID> with the actual expense id> and replace <TOKEN> with your JWT):**
    ```bash
    curl -X DELETE http://127.0.0.1:5555/expenses/<EXPENSE_ID> \
    -H "Authorization: Bearer <TOKEN>"
    ```
    