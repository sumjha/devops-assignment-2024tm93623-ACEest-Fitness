# Implementing Automated CI/CD Pipelines for ACEest Fitness & Gym

The objective of this assignment is to demonstrate comprehensive, hands-on experience in modern DevOps methodologies. This demonstrate Version Control (GitHub), Containerization (Docker), and the orchestration of Continuous Integration and Continuous Delivery (CI/CD) pipelines using GitHub Actions and Jenkins.

Application: A Flask-based web application for managing gym client profiles, fitness programs, and nutrition plans for ACEest Functional Fitness.

## Submitted By:

Name:   **Sumit Jha**

RollNo: **2024TM93623**

Course: Introduction to DEVOPS (SEZG514)

Git Repo: https://github.com/sumjha/devops-assignment-2024tm93623-ACEest-Fitness/

## Required Deliverables

| Deliverable | link|
|-------|-------------|
|**Source Code:** All Flask application files (app.py, requirements.txt). | [app.py](app.py) |
|**Test Suite:** All Pytest script files.|[tests/test_app.py](tests/test_app.py)|
|**Infrastructure as Code:** A functional Dockerfile and the GitHub Actions YAML configuration.| [Dockerfile](Dockerfile) [.github/workflows/main.yml](.github/workflows/main.yml)  |
|**Documentation:** A professional README.md detailing:| [README.md](README.md)
|**Local setup and execution instructions.**| https://github.com/sumjha/devops-assignment-2024tm93623-ACEest-Fitness/tree/main#local-setup--execution |
|**Steps to run tests manually.**| https://github.com/sumjha/devops-assignment-2024tm93623-ACEest-Fitness/tree/main#running-tests-manually |
|**A high-level overview of the Jenkins and GitHub Actions integration logic.**| https://github.com/sumjha/devops-assignment-2024tm93623-ACEest-Fitness/tree/main#github-actions--cicd-pipeline|

## Project Structure

```
aceest-gym/
├── app.py                      # Flask application (routes + business logic)
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container definition
├── Jenkinsfile                 # Jenkins pipeline configuration
├── templates/
│   └── index.html              # Frontend UI
├── tests/
│   └── test_app.py             # Pytest test suite
└── .github/
    └── workflows/
        └── main.yml            # GitHub Actions CI/CD pipeline
```

---

## Local Setup & Execution

### Prerequisites
- Python 3.11+
- Docker 

### 1. Clone the repository

```bash
git clone https://github.com/sumjha/devops-assignment-2024tm93623-ACEest-Fitness.git
cd devops-assignment-2024tm93623-ACEest-Fitness
```

### 2. Create a virtual environment and install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the application

```bash
python app.py
```

Open `http://localhost:5000` in your browser.

### 4. Run with Docker

```bash
docker build -t aceest-gym .
docker run -p 5000:5000 aceest-gym
```

---

## Running Tests Manually

Make sure your virtual environment is active, then:

```bash
DB_PATH=":memory:" python -m pytest tests/ -v
```

All tests use an in-memory SQLite database so nothing is written to disk.

---

## GitHub Actions — CI/CD Pipeline

The workflow file at `.github/workflows/main.yml` runs on every **push** and **pull request**.

**Pipeline stages:**

1. **Build & Lint** — installs Python dependencies and runs `flake8` to catch syntax errors and undefined names.
2. **Docker Image Build** — builds the Docker image to confirm the container can be assembled cleanly.
3. **Automated Tests** — spins up the built container and runs the full `pytest` suite inside it.

Each stage only runs if the previous one passes, acting as a quality gate before the image is considered deployable.

<img width="1666" height="875" alt="image" src="https://github.com/user-attachments/assets/f72dd49d-7881-484c-bd29-5b97fc4cb982" />

---

## Jenkins Integration

A `Jenkinsfile` is included at the project root for use with a Jenkins pipeline project.

**How to configure:**

1. In Jenkins, create a new **Pipeline** job.
2. Under *Pipeline → Definition*, select **Pipeline script from SCM**.
3. Set SCM to **Git** and point it at this repository.
4. Jenkins will automatically discover the `Jenkinsfile` and execute the pipeline.

**Pipeline stages:**

| Stage | What it does |
|-------|-------------|
| Checkout | Pulls latest code from GitHub |
| Install Dependencies | Creates a venv and installs `requirements.txt` |
| Lint | Runs `flake8` to verify code quality |
| Unit Tests | Runs `pytest` against the full test suite |
| Docker Build | Builds the Docker image and tags it with the build number |

Jenkins serves as the **BUILD quality gate** — the job fails fast if linting or any test fails, preventing a broken image from being tagged.

**Jenkins Screenshots**

<img width="1666" height="875" alt="image" src="https://github.com/user-attachments/assets/a711e51d-972f-46af-82c3-2c3f99ea5897" />

<img width="1666" height="875" alt="image" src="https://github.com/user-attachments/assets/7f0344fd-e5ea-4923-afcd-f19769788766" />


