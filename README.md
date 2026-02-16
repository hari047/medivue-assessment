# MediVue Task Management API
A robust, asynchronous REST API for managing tasks, built with FastAPI and PostgreSQL.

## 🚀 Quick Start
#### Prerequisites
Docker and Docker Compose

#### Execution
Clone the repository.

#### Run the application:

```
#Bash
docker-compose up --build
```
Access the API documentation (Swagger UI) at: http://localhost:8000/docs

## 🛠 Design Decisions
##### 1. Many-to-Many Tagging Logic
I implemented tagging using a Join Table (task_tags) rather than a simple array. This ensures data integrity and allows for efficient querying, such as finding all tasks associated with a specific tag without scanning entire text blocks.

##### 2. Soft Deletion Strategy
Instead of permanently deleting data, I implemented a is_deleted flag. In a healthcare/MedTech context, maintaining data audit trails is critical; soft deletes allow for data recovery and historical analysis while keeping the active API responses clean.

##### 3. Asynchronous Architecture
The entire backend uses SQLAlchemy 2.0's AsyncSession. This allows the API to handle a high volume of concurrent requests without blocking the event loop, ensuring the application remains responsive under load.

## ✅ Production Readiness
To move this from a technical assessment to a production environment, I would implement:

##### Alembic Migrations: 
To manage database schema changes safely over time.

##### Authentication: 
OAuth2 with JWT tokens to secure user data.

##### CI/CD Pipeline: 
GitHub Actions to run the existing pytest suite automatically on every pull request.
