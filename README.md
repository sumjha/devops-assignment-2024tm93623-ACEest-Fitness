# [Assignment - 2] Implementing Automated CI/CD Pipelines for ACEest Fitness & Gym

The objective of this assignment is to demonstrate comprehensive, hands-on experience in modern DevOps methodologies. This includes version control (GitHub), containerization (Docker), CI/CD with GitHub Actions and Jenkins, **static analysis with SonarQube**, and **Kubernetes** deployment on Minikube (including optional advanced rollout patterns).

Application: A Flask-based web application for managing gym client profiles, fitness programs, and nutrition plans for ACEest Functional Fitness.

## Submitted By:

Name:   Sumit Jha  
RollNo: 2024TM93623  
Course: Introduction to DEVOPS (SEZG514)

**GitHub repository:** [https://github.com/sumjha/devops-assignment-2024tm93623-ACEest-Fitness](https://github.com/sumjha/devops-assignment-2024tm93623-ACEest-Fitness/)

## Required deliverables


| Deliverable                                                                                                        | Where it lives in this repository                                                                                                                  |
| ------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Project folder** (complete codebase)                                                                             | [Repository root](https://github.com/sumjha/devops-assignment-2024tm93623-ACEest-Fitness)                                                          |
| **Flask application** — integrated app and version history (*ACEest Fitness* iterations; primary file is `app.py`) | [app.py](app.py)                                                                                     |
| **Jenkins pipeline configuration**                                                                                 | [Jenkinsfile](Jenkinsfile)                                                                                                                      |
| **Dockerfile**                                                                                                     | [Dockerfile](Dockerfile)                                                                                                                         |
| **Kubernetes YAML manifests**                                                                                      | [k8s/aceest-gym.yaml](k8s/aceest-gym.yaml) · [k8s/deployment-strategies/](k8s/deployment-strategies/)                                          |
| **Pytest test cases**                                                                                              | [tests/test_app.py](tests/test_app.py)                                                                                                           |
| **SonarQube report**                                                                                               | [Sonar-report.pdf](Sonar-report.pdf)                                                                                                           |
| **Docker Hub**                                                                                               | https://hub.docker.com/repository/docker/sumjha/accest-devops-assignment/tags                                                                                                         |
| **GitHub repository link**                                                                                         | [https://github.com/sumjha/devops-assignment-2024tm93623-ACEest-Fitness/](https://github.com/sumjha/devops-assignment-2024tm93623-ACEest-Fitness/) |


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

<img width="1709" height="887" alt="image" src="https://github.com/user-attachments/assets/3fc6bba8-1e9d-4518-a6e3-cb694726438c" />


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

<img width="1709" height="517" alt="image" src="https://github.com/user-attachments/assets/d8bfa915-cf94-46b5-8f2f-e82d35ffc14d" />

<img width="1709" height="959" alt="image" src="https://github.com/user-attachments/assets/bc5f2d4c-e576-46b0-bcdd-efa77be568fd" />

---

## SonarQube — static analysis

[SonarQube](https://www.sonarqube.org/) performs static analysis (bugs, vulnerabilities, code smells, coverage when configured). Run a **SonarQube Server** (for example the official Docker image on port **9000**), create a project with key `**Aceest-gym-devops-assignment2`**, and under My Account → Security generate a token and pass it to the scanner as `**-Dsonar.token=`** or `**-Dsonar.login=**` (never commit the token to Git).

<img width="1709" height="959" alt="image" src="https://github.com/user-attachments/assets/b0e8fd5f-411d-4ded-8255-0d05d4a40961" />

### Jenkins agent requirements

1. `**sonar-scanner**` installed on the agent and available on `PATH`, *or* run the scanner from the official SonarScanner Docker image.
2. The Jenkins machine must reach `**SONAR_HOST_URL`** (for example `http://localhost:9000` only works if SonarQube runs on the *same host* as the agent; for a remote server use that URL instead).

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

## CI/CD architecture overview

End-to-end flow for this project:

1. **Source control** — Application and pipeline definitions live in **GitHub**; every push and pull request triggers automation.
2. **GitHub Actions** (`.github/workflows/main.yml`) — Cloud-side CI: install dependencies, **flake8** lint, build the **Docker** image, run **pytest** inside the container. Failing lint or tests blocks progression.
3. **Jenkins** (local, `http://localhost:8080`) — On-prem style CI/CD: checkout, Python venv, **flake8**, **pytest** (`DB_PATH=":memory:"`), Docker build/tag, optional **SonarQube** via `sonar-scanner`, then **Docker Hub** push using stored credentials.
4. **SonarQube** (local, `http://localhost:9000`) — Static analysis and quality gate for the same codebase Jenkins builds; `sonar.host.url` points at this instance when the scanner runs on the same machine.
5. **Kubernetes (Minikube)** — Optional deployment path using `k8s/aceest-gym.yaml` and advanced rollout examples under `k8s/deployment-strategies/`.

Together, **GitHub Actions** and **Jenkins** provide overlapping quality gates; **Docker** produces a portable runtime artifact; **SonarQube** adds maintainability and defect signals; **Kubernetes** manifests document how the container is scheduled and exposed in a cluster.

## Challenges faced and mitigation strategies


| Challenge                                          | Mitigation                                                                                                                                                                 |
| -------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Jenkins agent could not find `docker`**          | Extended `PATH` in the `Jenkinsfile` for common install locations (Homebrew, `/usr/local/bin`); documented checking the node’s environment under *Manage Jenkins → Nodes*. |
| **Secrets in pipelines**                           | Docker Hub and Sonar tokens are **not** committed to Git; Jenkins **Credentials** (`withCredentials`) supply them at runtime.                                              |
| **SQLite / tests in CI**                           | Tests use `DB_PATH=":memory:"` so pytest does not depend on a host file or conflict with parallel jobs.                                                                    |
| **SonarQube noise on generated or vendored paths** | `sonar.exclusions` for `venv`, `.git`, and the large `The code versions for DevOps Assignment/` folder.                                                                    |
| **Minikube image pull**                            | Build with `eval $(minikube docker-env)` and use `imagePullPolicy: Never` for local tags, or `minikube image load`.                                                        |
| **Ingress-based strategies (canary, shadow, A/B)** | Require **ingress-nginx** and correct **IngressClass**; hostnames must resolve to the Minikube IP (e.g. `/etc/hosts`).                                                     |


## Key automation outcomes

- **Repeatable builds** — Same `Dockerfile` and pipeline stages every run, reducing “works on my machine” drift.
- **Fast feedback** — Lint and unit tests fail the pipeline before a broken image is pushed or promoted.
- **Single artifact** — Docker image is the deployable unit for local run, registry, and Kubernetes.
- **Quality visibility** — SonarQube highlights bugs, vulnerabilities, and smells on a dashboard tied to the project key.
- **Documented deployment** — Kubernetes YAML encodes namespace, storage, probes, services, and optional ingress and rollout patterns for assignments and demos.

## Local Jenkins and SonarQube

**Jenkins** and **SonarQube** are installed and run **locally** on the development machine (same host as the Jenkins agent running `sonar-scanner`).


| Tool          | URL                                            |
| ------------- | ---------------------------------------------- |
| **Jenkins**   | [http://localhost:8080](http://localhost:8080) |
| **SonarQube** | [http://localhost:9000](http://localhost:9000) |


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

<img width="925" height="650" alt="image" src="https://github.com/user-attachments/assets/5a8510fa-0ff8-4a80-960c-9383d912bc07" />
<img width="925" height="89" alt="image" src="https://github.com/user-attachments/assets/41346889-a0ce-46d4-8a34-e37b442bfb8d" />
<img width="624" height="640" alt="image" src="https://github.com/user-attachments/assets/35f95b2d-feaa-4acd-8176-23c3d8a111ac" />
<img width="723" height="651" alt="image" src="https://github.com/user-attachments/assets/f8b7c791-a53c-4ecd-acd3-dd53f7fb1489" />


### Advanced deployment strategies (`k8s/deployment-strategies/`)

Separate example manifests in namespace `**aceest-gym-strategies`** (each file is self-contained):


| File                     | Strategy                                                                                       |
| ------------------------ | ---------------------------------------------------------------------------------------------- |
| `rolling-update.yaml`    | Rolling update with zero `maxUnavailable`; `**kubectl rollout undo`** for rollback             |
| `blue-green.yaml`        | Blue / green stacks; **rollback** by patching the active Service selector back to `slot: blue` |
| `canary-release.yaml`    | Weighted canary via **ingress-nginx** (`canary.aceest.local`)                                  |
| `shadow-deployment.yaml` | Request mirroring to a shadow service (`shadow.aceest.local`)                                  |
| `ab-testing.yaml`        | Header-based A/B (`X-Aceest-AB: b` → variant B, `ab.aceest.local`)                             |


These examples use `**emptyDir`** for SQLite so they can run alongside each other without sharing one RWO volume. Canary, shadow, and A/B require the **ingress-nginx** Minikube ingress addon and the **image tags** documented in each file’s header (tag copies of `aceest-gym:latest` in the Minikube Docker daemon).

Apply one strategy at a time (or adjust names/ports if you combine resources):

```bash
kubectl apply -f k8s/deployment-strategies/rolling-update.yaml
```

