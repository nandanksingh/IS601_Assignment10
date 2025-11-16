# **Assignment 10 – Secure User Model, Pydantic Validation, and Docker Testing**

**Author:** Nandan Kumar   
**Date:** November 10, 2025

---

## **Introduction**

In this assignment, I extended my FastAPI project by creating a **secure user model** with SQLAlchemy, Pydantic validation, and password hashing. I also set up a complete development environment using **Docker Compose** and automated the entire testing and deployment workflow through **GitHub Actions**.

This project helped me understand how real-world backend systems are built, tested, and deployed using modern DevOps practices.

---

## **Project Structure and Tools**

The project includes three main services:

| Service     | Purpose                  | Port |
| ----------- | ------------------------ | ---- |
| **app**     | FastAPI backend          | 8000 |
| **db**      | PostgreSQL database      | 5432 |
| **pgadmin** | Web GUI for SQL database | 5050 |

I used the following technologies:

* **FastAPI** for building the API
* **SQLAlchemy** for database models
* **Pydantic** for input validation
* **Docker** and **Docker Compose**
* **GitHub Actions** for CI/CD
* **Trivy** for vulnerability scanning
* **PostgreSQL + pgAdmin** for data storage and management

---

## **Running the Project with Docker**

Start all services:

```bash
docker compose up --build
```

Access:

* FastAPI: [http://localhost:8000](http://localhost:8000)
* pgAdmin: [http://localhost:5050](http://localhost:5050)

Stop services:

```bash
docker compose down
```

---

## **CI/CD Pipeline (GitHub Actions)**

My GitHub workflow has three automated stages:

### **1. Test Stage**

* Runs unit and integration tests
* Starts a PostgreSQL service inside the workflow
* Requires **90% minimum coverage**

### **2. Security Scan**

* Builds the Docker image
* Scans it with **Trivy** for high/critical vulnerabilities

### **3. Deployment Stage**

* Pushes the final Docker image to Docker Hub

This ensures that only a **tested and secure** version of the image is deployed.

Run tests locally using:

```bash
pytest --cov=app -v
```

---

## **Docker Hub Deployment**

I published the verified Docker image here:

 **[https://hub.docker.com/r/nandanksingh/module10_user_model](https://hub.docker.com/r/nandanksingh/module10_user_model)**

Pull the image:

```bash
docker pull nandanksingh/module10_user_model:m10
```

Run it:

```bash
docker run -d -p 8000:8000 nandanksingh/module10_user_model:m10
```

---

## **Local Setup (Without Docker)**

```bash
git clone https://github.com/nandanksingh/IS601_Assignment10.git
cd IS601_Assignment10
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open the API docs:
[http://localhost:8000/docs](http://localhost:8000/docs)

---

## **Key Features Implemented**

* Secure SQLAlchemy **User Model**
* Password hashing and verification functions
* Pydantic **UserCreate** and **UserRead** schemas
* PostgreSQL database with uniqueness constraints
* Automatically seeded SQLite fallback for testing
* Complete CI/CD pipeline with test coverage and security scans
* Docker image ready for production-style testing

---

## **Common Problems and Fixes**

| Problem              | Reason                   | Fix                   |
| -------------------- | ------------------------ | --------------------- |
| DB connection failed | Wrong `.env ` values     | Sync credentials      |
| Port already in use  | Previous FastAPI running | Kill process          |
| Tests failing        | Cached files             | Remove `__pycache__`  |
| pgAdmin not loading  | DB not ready             | Add `service_healthy` |
| Import errors        | Mixed environments       | Reinstall venv        |

---

## **Reflection:**

This assignment really helped me understand how backend development and DevOps fit together. Creating a secure user model showed me why input validation and password hashing are essential for any real application. Using Docker Compose made it easier to manage multiple services like FastAPI, PostgreSQL, and pgAdmin in one environment.

I also learned how to write better tests and how GitHub Actions can automate the entire workflow—from running tests to scanning the image and finally deploying it to Docker Hub. Setting up the CI/CD pipeline was challenging at first, but it gave me valuable experience that reflects real industry practices. Overall, this project strengthened my confidence in building and deploying secure, well-tested backend applications.

---

## **Final Summary**

This assignment combines secure API development with database management, automated testing, containerization, and CI/CD. The final result is a fully tested, secure, and automatically deployed FastAPI application—similar to what modern software teams build in real-world production environments.

