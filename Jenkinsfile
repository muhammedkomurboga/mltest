pipeline {
    agent any
    triggers { pollSCM('H/2 * * * *') }
    environment {
        IMAGE = "ml-api"
        CONTAINER = "ml-api"
    }
    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Setup') {
            steps {
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install -r requirements.txt ruff
                '''
            }
        }
        stage('Lint') {
            steps {
                sh '''
                . venv/bin/activate
                ruff check app tests validate_model.py
                '''
            }
        }
        stage('Test') {
            steps {
                sh '''
                . venv/bin/activate
                pytest -q
                '''
            }
        }
        stage('Validate model') {
            steps {
                sh '''
                . venv/bin/activate
                python validate_model.py
                '''
            }
        }
        stage('Build image') {
            steps { sh 'docker build -t $IMAGE:${BUILD_NUMBER} -t $IMAGE:latest .' }
        }
        stage('Deploy') {
            steps {
                sh '''
                docker rm -f $CONTAINER || true
                docker run -d --name $CONTAINER -p 8000:8000 $IMAGE:latest
                '''
            }
        }
        stage('Smoke test') {
            steps {
                sh '''
                sleep 5
                curl -f http://host.docker.internal:8000/health
                curl -f http://host.docker.internal:8000/metrics > /dev/null
                curl -f -X POST http://host.docker.internal:8000/predict \
                  -H "Content-Type: application/json" \
                  -d '{"features":[5.1,3.5,1.4,0.2]}'
                '''
            }
        }
    }
    post {
        success { echo "Pipeline geslaagd: model gedeployed" }
        failure { sh 'docker logs $CONTAINER || true' }
    }
}
