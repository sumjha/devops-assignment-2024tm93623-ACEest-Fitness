# [Assignment - 2] Implementing Automated CI/CD Pipelines for ACEest Fitness & Gym

The objective of this assignment is to demonstrate comprehensive, hands-on experience in modern DevOps methodologies. This includes version control (GitHub), containerization (Docker), CI/CD with GitHub Actions and Jenkins, **static analysis with SonarQube**, and **Kubernetes** deployment on Minikube (including optional advanced rollout patterns).

Application: A Flask-based web application for managing gym client profiles, fitness programs, and nutrition plans for ACEest Functional Fitness.

## Submitted By:

Name:   Sumit Jha  
RollNo: 2024TM93623  
Course: Introduction to DEVOPS (SEZG514)

## Project Structure

```
aceest-gym/
├── app.py                      # Flask application (routes + business logic)
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container definition
├── Jenkinsfile                 # Jenkins pipeline configuration
├── k8s/
│   ├── aceest-gym.yaml         # Single-file Kubernetes manifest (Minikube)
│   └── deployment-strategies/  # Advanced rollout patterns (see Kubernetes section)
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

---

## Jenkins Integration

A `Jenkinsfile` is included at the project root for use with a Jenkins pipeline project.

**How to configure:**

1. In Jenkins, create a new **Pipeline** job.
2. Under *Pipeline → Definition*, select **Pipeline script from SCM**.
3. Set SCM to **Git** and point it at this repository.
4. Jenkins will automatically discover the `Jenkinsfile` and execute the pipeline.

**Pipeline stages:**


| Stage                | What it does                                                      |
| -------------------- | ----------------------------------------------------------------- |
| Checkout             | Pulls latest code from GitHub                                     |
| Install Dependencies | Creates a venv and installs `requirements.txt`                    |
| Lint                 | Runs `flake8` to verify code quality                              |
| Unit Tests           | Runs `pytest` against the full test suite                         |
| Docker Build         | Builds the Docker image and tags it with the build number         |
| Docker Push          | Tags the image for Docker Hub and pushes with Jenkins credentials |


Jenkins serves as the **BUILD quality gate** — the job fails fast if linting or any test fails, preventing a broken image from being tagged.

---

## SonarQube — static analysis

[SonarQube](https://www.sonarqube.org/) performs static analysis (bugs, vulnerabilities, code smells, coverage when configured). Run a **SonarQube Server** (for example the official Docker image on port 9000), create a project with key `**Aceest-gym-devops-assignment2`**, and under **My Account → Security** generate a **token** and pass it to the scanner as `**-Dsonar.token=`** or `**-Dsonar.login=**` (never commit the token to Git).

### Jenkins agent requirements

1. `**sonar-scanner**` installed on the agent and available on `PATH`, *or* run the scanner from the official SonarScanner Docker image.
2. The Jenkins machine must reach `**SONAR_HOST_URL*`* (for example `http://localhost:9000` only works if SonarQube runs on the *same host* as the agent; for a remote server use that URL instead).

### Recommended Jenkins stage (token via credential)

Store the token as a Jenkins **Secret text** credential (example ID: `sonar-token-aceest`). Then add a stage **after** dependencies are installed (so Python sources are present):

```groovy
stage('Static Analysis - SonarQube') {
    steps {
        withCredentials([string(credentialsId: 'sonar-token-aceest', variable: 'SONAR_TOKEN')]) {
            sh '''
                sonar-scanner \
                  -Dsonar.projectKey=Aceest-gym-devops-assignment2 \
                  -Dsonar.sources=. \
                  -Dsonar.host.url=http://localhost:9000 \
                  -Dsonar.token=$SONAR_TOKEN \
                  -Dsonar.exclusions=**/venv/**,**/.git/**,**/The code versions for DevOps Assignment/**
            '''
        }
    }
}
```

Notes:

- `**-Dsonar.token=**` is preferred on newer SonarQube versions; `**-Dsonar.login=**` with the token string still works on many setups (replace the placeholder below with your token or `$SONAR_TOKEN`).
- Adjust `**-Dsonar.host.url**` to your real SonarQube base URL.
- Add `**-Dsonar.python.version=3.11**` if you want explicit Python analysis configuration.

### Minimal stage (token supplied manually — not for production)

```groovy
stage('Static Analysis - SonarQube') {
    steps {
        sh '''
            sonar-scanner \
              -Dsonar.projectKey=Aceest-gym-devops-assignment2 \
              -Dsonar.sources=. \
              -Dsonar.host.url=http://localhost:9000 \
              -Dsonar.login=YOUR_SONAR_TOKEN_HERE
        '''
    }
}
```

Replace `**YOUR_SONAR_TOKEN_HERE**` with a user token from the SonarQube UI, or switch to the `withCredentials` example above.

### `sonar-scanner` invocation

Equivalent to the course template; replace `**LoginID**` with your SonarQube user token (same value you would pass to `-Dsonar.login=` in the UI docs):

```groovy
stage('Static Analysis - SonarQube') {
    steps {
        sh '''
            sonar-scanner \
              -Dsonar.projectKey=Aceest-gym-devops-assignment2 \
              -Dsonar.sources=. \
              -Dsonar.host.url=http://localhost:9000 \
              -Dsonar.login=LoginID
        '''
    }
}
```

Use a Jenkins **Secret text** credential and `-Dsonar.login=$SONAR_TOKEN` (or `-Dsonar.token=$SONAR_TOKEN`) instead of hard-coding the token in the `Jenkinsfile`.

---

## Kubernetes (Minikube)

The application is containerised with **Gunicorn** on port **5000**. Manifests live under `**k8s/`**.

### Base deployment (`k8s/aceest-gym.yaml`)

Single manifest containing: **Namespace**, **PVC** (SQLite on a volume), **Deployment**, **Service** (`NodePort` **30080**), and optional **Ingress** (`aceest.local`).

1. **Build the image inside Minikube’s Docker** (so `imagePullPolicy: Never` can resolve `aceest-gym:latest`):
  ```bash
   minikube start
   eval $(minikube docker-env)
   docker build -t aceest-gym:latest .
  ```
2. **Apply**:
  ```bash
   kubectl apply -f k8s/aceest-gym.yaml
  ```
3. **Open the app**
  - NodePort: `http://$(minikube ip):30080` or `minikube service aceest-gym -n aceest-gym --url`
  - Ingress: `minikube addons enable ingress`, add `$(minikube ip) aceest.local` to `/etc/hosts`, then browse `http://aceest.local`

### Advanced deployment strategies (`k8s/deployment-strategies/`)

Separate example manifests in namespace `**aceest-gym-strategies`** (each file is self-contained):


| File                     | Strategy                                                                                       |
| ------------------------ | ---------------------------------------------------------------------------------------------- |
| `rolling-update.yaml`    | Rolling update with zero `maxUnavailable`; `**kubectl rollout undo**` for rollback             |
| `blue-green.yaml`        | Blue / green stacks; **rollback** by patching the active Service selector back to `slot: blue` |
| `canary-release.yaml`    | Weighted canary via **ingress-nginx** (`canary.aceest.local`)                                  |
| `shadow-deployment.yaml` | Request mirroring to a shadow service (`shadow.aceest.local`)                                  |
| `ab-testing.yaml`        | Header-based A/B (`X-Aceest-AB: b` → variant B, `ab.aceest.local`)                             |


These examples use `**emptyDir`** for SQLite so they can run alongside each other without sharing one RWO volume. Canary, shadow, and A/B require the **ingress-nginx** Minikube ingress addon and the **image tags** documented in each file’s header (tag copies of `aceest-gym:latest` in the Minikube Docker daemon).

Apply one strategy at a time (or adjust names/ports if you combine resources):

```bash
kubectl apply -f k8s/deployment-strategies/rolling-update.yaml
```

