# Home budgeting app

This is a simple FastAPI app tracking spending's and income

---

## 🔧 Features

- Oauth2 authentication with JWT tokens
- CRUD operations for expenses and categories
- Statistics endpoint to get stats in date range

---

## 🚀 Running the App

1. **Install dependencies**:

```bash
pip install -r requirements.txt
```

2. **Run the FastAPI app**:

```bash
uvicorn home_budget.main:app --reload
```

3. **Access the API**:

- Open your browser and go to `http://localhost:8000/docs` to see the API documentation and test the endpoints.

4. **DB setup**:
   to set up the database, you can run:

```bash
 docker compose up -d
```

5.**Database Migrations**:

- If you are using Alembic for migrations, you can run:

```bash
alembic revision --autogenerate -m "Initial migration"
```

- To apply the migrations, run:

```bash
alembic upgrade head
```

   