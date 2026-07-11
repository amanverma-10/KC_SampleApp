pipeline {
    agent any

    environment {
        CI = 'true'
    }

    stages {
        stage('Setup Dependencies') {
            steps {
                echo 'Installing Backend and Frontend dependencies...'
                sh '''
                    cd backend
                    python3 -m venv venv
                    ./venv/bin/pip install --upgrade pip
                    ./venv/bin/pip install -r requirements-test.txt
                '''
                sh '''
                    cd frontend
                    npm ci || npm install
                '''
            }
        }

        stage('Lint Frontend') {
            steps {
                echo 'Running ESLint on the frontend codebase...'
                sh '''
                    cd frontend
                    npm run lint
                '''
            }
        }

        stage('Test Backend') {
            steps {
                echo 'Running pytest suite on the backend codebase...'
                sh '''
                    cd backend
                    mkdir -p test-reports
                    ./venv/bin/pytest tests --junitxml=test-reports/results.xml
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'backend/test-reports/results.xml'
                }
            }
        }

        stage('Build Frontend') {
            steps {
                echo 'Compiling React production build...'
                sh '''
                    cd frontend
                    npm run build
                '''
            }
        }

        stage('Docker Compose Build Verification') {
            steps {
                echo 'Verifying Docker Compose configurations and building images...'
                sh 'docker compose build'
            }
        }
    }

    post {
        always {
            echo 'Pipeline execution complete.'
        }
        success {
            echo 'Build and tests passed successfully!'
        }
        failure {
            echo 'Pipeline failed. Please review the console output and test results.'
        }
    }
}
