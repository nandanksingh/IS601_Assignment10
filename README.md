# **Assignment 10 – Secure User Model, Pydantic Validation, and Docker Testing**

**Author:** Nandan Kumar  
**Date:** November 10, 2025


---

## **Project Overview**

This project builds upon earlier FastAPI assignments by developing a **Secure User Model** integrated with **SQLAlchemy ORM**, **Pydantic Validation**, and **PostgreSQL**, fully containerized through **Docker Compose** and continuously validated via **GitHub Actions CI/CD**.

The objective was to simulate a production-grade backend service ensuring **data integrity**, **security**, and **automation** — combining development, testing, and deployment workflows in one unified pipeline.

The stack includes:

* **FastAPI** – Asynchronous RESTful backend
* **PostgreSQL** – Relational database engine
* **pgAdmin 4** – Web-based database management tool

---

## **Environment Setup**

### **Docker Compose Services**

| Service     | Description                 | Port |
| ----------- | --------------------------- | ---- |
| **app**     | FastAPI backend application | 8000 |
| **db**      | PostgreSQL database         | 5432 |
| **pgadmin** | GUI for database management | 5050 |

**Start the stack**

```bash
docker compose up --build
```

**Access points**

* FastAPI → [http://localhost:8000](http://localhost:8000)
* pgAdmin → [http://localhost:5050](http://localhost:5050)

**Stop containers**

```bash
docker compose down
```

---

## **GitHub CI/CD Pipeline**

Automated testing, image scanning, and deployment are managed through **GitHub Actions** using `.github/workflows/test.yml`.

### **Workflow Stages**

1. **Test Phase** – Spins up a PostgreSQL container and runs unit/integration tests with ≥ 90% coverage.
2. **Security Phase** – Performs a **Trivy vulnerability scan** on the built Docker image.
3. **Deploy Phase** – Pushes the verified image to **Docker Hub** if all checks pass.

**Manual local run:**

```bash
pytest --cov=app --cov-report=term-missing -v --disable-warnings
```

**GitHub workflow output:**
Each push to `main` automatically triggers testing → scan → deploy, ensuring secure, reproducible builds.

---

## **Docker Image & Deployment**

Once CI tests pass successfully, the verified image is automatically pushed to Docker Hub.

**Build & Push manually:**

```bash
docker build -t nandanksingh/module10_user_model:m10 .
docker push nandanksingh/module10_user_model:m10
```

**Docker Hub Repository:**
🔗 [https://hub.docker.com/r/nandanksingh/module10_user_model](https://hub.docker.com/r/nandanksingh/module10_user_model)

**Pull and Run:**

```bash
docker pull nandanksingh/module10_user_model:m10
docker run -d -p 8000:8000 nandanksingh/module10_user_model:m10
```

This container encapsulates the full backend system — FastAPI + PostgreSQL + pgAdmin — ideal for testing or demonstration purposes.

---

## **Database Configuration**

**pgAdmin Login:**

* Email → `admin@local.com`
* Password → `admin`

**Database Connection:**

* Host → `db`
* User → `ps_user`
* Password → `ps_password`
* Database → `fastapi_user_db`

---

## **Local Setup Instructions**

### **1. Clone Repository and Activate Virtual Environment**

```bash
git clone https://github.com/nandanksingh/IS601_Assignment10.git
cd IS601_Assignment10
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **2. Run Locally without Docker**

```bash
uvicorn main:app --reload
```

Then open: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## **Key Features**

* Secure **User Model** with hashed passwords
* **Pydantic** schemas for validation (UserCreate / UserRead)
* **SQLAlchemy ORM** for robust data persistence
* Environment-based config via `.env` and `config.py`
* Automatic **PostgreSQL → SQLite fallback** in tests
* 100% test coverage on database modules
* Fully containerized development stack
* Automated **CI/CD** with GitHub Actions + **Trivy scan**

---

## **Common Issues & Fixes**

| Issue                                  | Cause                                                | Solution                                         |
| -------------------------------------- | ---------------------------------------------------- | ------------------------------------------------ |
| `Database authentication failed`       | Env mismatch between `.env` and `docker-compose.yml` | Ensure both use `ps_user` / `ps_password`        |
| `Port 8000 already in use`             | Previous FastAPI process active                      | Kill process via `fuser -k 8000/tcp`             |
| `pytest import errors`                 | Bytecode cache conflicts                             | `find . -name "__pycache__" -exec rm -rf {} +`   |
| `pgAdmin not loading`                  | DB service not yet healthy                           | Add `depends_on: db: condition: service_healthy` |
| `Connection refused on localhost:5432` | DB credentials mismatch or service down              | Check `.env` vars before building Docker image   |

---

## **Reflection (≈ 130 words)**

This assignment deepened my understanding of how **secure backend architectures** combine with **DevOps automation**.
Implementing a Pydantic-based User Model strengthened my grasp of input validation and password hashing best practices.
Working with **Docker Compose** made me appreciate how containerized multi-service environments simplify deployment.
Troubleshooting PostgreSQL connectivity, `.env` variables, and GitHub pipeline errors improved my debugging workflow.
Integrating **pytest**, **Trivy**, and **GitHub Actions** offered hands-on exposure to real-world continuous integration, testing, and deployment processes.
By the end, I not only achieved full test coverage but also built a reusable, production-ready container that showcases secure, validated, and automated API development.

---

## **Technology Stack**

| Category             | Tools / Frameworks      |
| :------------------- | :---------------------- |
| **Language**         | Python 3.12             |
| **Framework**        | FastAPI                 |
| **ORM / DB**         | SQLAlchemy + PostgreSQL |
| **Validation**       | Pydantic                |
| **Testing**          | Pytest, Faker, Coverage |
| **Containerization** | Docker, Docker Compose  |
| **Database GUI**     | pgAdmin 4               |
| **CI/CD**            | GitHub Actions + Trivy  |
| **Image Tag**        | `m10`                   |

---

### **Final Summary**

This project demonstrates how a **secure, production-ready FastAPI service** can be **tested, containerized, and deployed automatically** using modern DevOps tools.
It bridges **Python application design** with **CI/CD automation**, reflecting industry best practices for building reliable, scalable backend systems.
