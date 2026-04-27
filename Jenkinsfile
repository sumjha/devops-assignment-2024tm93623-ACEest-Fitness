pipeline {
    agent any

    environment {
        IMAGE_NAME            = "aceest-gym"
        IMAGE_TAG             = "build-${BUILD_NUMBER}"
        DOCKER_REGISTRY_IMAGE = "sumjha/accest-devops-assignment"
        GIT_REPO_URL          = "https://github.com/sumjha/devops-assignment-2024tm93623-ACEest-Fitness"
        GIT_BRANCH   = "main"
        // Jenkins often runs with a stripped PATH; Docker CLI lives under these on macOS/Linux.
        PATH         = "/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:${env.PATH}"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Pulling latest code from ${GIT_REPO_URL} (branch: ${GIT_BRANCH})..."
                git branch: "${GIT_BRANCH}", url: "${GIT_REPO_URL}"
            }
        }

        stage('Install Dependencies') {
            steps {
                echo "Setting up Python environment..."
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install flake8
                '''
            }
        }

        stage('Lint') {
            steps {
                echo "Running flake8 lint check..."
                sh '''
                    . venv/bin/activate
                    flake8 app.py --count --select=E9,F63,F7,F82 --show-source --statistics
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                echo "Running pytest suite..."
                sh '''
                    . venv/bin/activate
                    DB_PATH=":memory:" python -m pytest tests/ -v --tb=short
                '''
            }
        }

        stage('Docker Build') {
            steps {
                echo "Building Docker image: ${IMAGE_NAME}:${IMAGE_TAG}"
                sh """
                    export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:\${PATH}"
                    if ! command -v docker >/dev/null 2>&1; then
                        echo "docker not found. Install Docker Desktop (or Docker Engine) and ensure the CLI is available."
                        echo "If it works in Terminal but not here, set PATH for the Jenkins process (see Jenkins system logs) or add Environment PATH under Manage Jenkins → Nodes → your agent → Environment variables."
                        echo "PATH=\${PATH}"
                        exit 1
                    fi
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                """
            }
        }

        stage('Docker Push') {
            steps {
                echo "Pushing to Docker Hub: ${DOCKER_REGISTRY_IMAGE}:${IMAGE_TAG} (and latest)"
                // Add a "Username with password" credential in Jenkins with this ID (Docker Hub access token recommended).
                withCredentials([
                    usernamePassword(
                        credentialsId: 'docker-hub-accest-devops',
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {
                    sh """
                        export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:\${PATH}"
                        echo \$DOCKER_PASSWORD | docker login -u \$DOCKER_USERNAME --password-stdin
                        docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${DOCKER_REGISTRY_IMAGE}:${IMAGE_TAG}
                        docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${DOCKER_REGISTRY_IMAGE}:latest
                        docker push ${DOCKER_REGISTRY_IMAGE}:${IMAGE_TAG}
                        docker push ${DOCKER_REGISTRY_IMAGE}:latest
                    """
                }
            }
        }
    }

    post {
        success {
            echo "BUILD SUCCESSFUL — ${DOCKER_REGISTRY_IMAGE}:${IMAGE_TAG} pushed (local tag ${IMAGE_NAME}:${IMAGE_TAG})."
        }
        failure {
            echo "BUILD FAILED — check the logs above for details."
        }
        always {
            echo "Pipeline completed. Build #${BUILD_NUMBER}"
        }
    }
}
