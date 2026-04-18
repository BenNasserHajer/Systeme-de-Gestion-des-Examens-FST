# 🚀 Full Stack PFA Project (Next.js + FastAPI + PostgreSQL)

This project is a full-stack web application built with:
- Frontend: Next.js (React)
- Backend: FastAPI (Python)
- ORM: SQLAlchemy
- Database: PostgreSQL

---

# ⚡ Quick Start (For Developers)

## 1. Clone repository
## 2. Database Setup (PostgreSQL)

Create database:

CREATE DATABASE mydb;

Create server/.env file:

DATABASE_URL=postgresql://postgres:password@localhost:5432/mydb

---

## 3. Server Setup (FastAPI)

cd server

Activate virtual environment:

venv\Scripts\activate   # Windows
source venv/bin/activate   # Mac/Linux

Install dependencies:

pip install -r requirements.txt

Run server:

uvicorn app.main:app --reload

Server URL:
http://127.0.0.1:8000

API Docs:
http://127.0.0.1:8000/docs

---

## 4. Client Setup (Next.js)

cd client

Install dependencies:

npm install

Run frontend:

npm run dev

Client URL:
http://localhost:3000

---

# 🔄 Team Workflow 

## When a contributor adds a new dependency:

They must:

pip install package_name
pip freeze > requirements.txt
git add requirements.txt
git commit -m "update dependencies"
git push


## 📌 Before merging a Pull Request:

You must:

git pull origin main

Activate environment:

venv\Scripts\activate   # Windows
source venv/bin/activate   # Mac/Linux

Install dependencies:

pip install -r requirements.txt

Run server to test:

uvicorn app.main:app --reload


# 🧱 Server Architecture (FastAPI)

- routes → API endpoints (defines URL paths)
- controllers → request handlers (API logic layer, receives request & returns response)
- services → business logic (core application logic)
- models → database tables (SQLAlchemy models)
- schemas → validation (Pydantic request/response models)
- database → connection (SQLAlchemy engine & session)

- utils → helper functions (reusable functions like formatting, hashing, etc.)
- config → application configuration (env variables, settings)
- middleware → request/response interceptors (auth, logging, CORS, etc.)
- constants → global constants (static values used across the app)

# 📦 Requirements

All server dependencies are stored in:

requirements.txt

Install all dependencies:

pip install -r requirements.txt


# 🎯 Features

- FastAPI REST API
- PostgreSQL integration
- SQLAlchemy ORM
- Clean architecture (routes/controllers/services/models)
- Next.js frontend

# 🚀 Important Notes

- Always run environment activation before backend
- Always run pip install -r requirements.txt after pull
- Always update requirements.txt when adding dependencies
- Make sure PostgreSQL is running before starting server
- Server must be running before client API calls


# Obligatoire env variables
DATABASE_URL=postgresql://postgres:password@localhost:5432/mydb

# Optionnelles
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_ECHO=False
DATABASE_TIMEOUT=30



