pipeline {
    agent any
    triggers { pollSCM('H/2 * * * *') }
    parameters {
        string(name: 'ROLLBACK_VERSION', defaultValue: '',
               description: 'Buildnummer om naar terug te rollen (leeg = normale build)')
    }
    environment {
        IMAGE = "ml-api"
        CONTAINER = "ml-api"
    }
    stages {
        stage('CI/CD') {
            when { expression { !params.ROLLBACK_VERSION } }
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
                    steps {
                        sh 'docker build --build-arg MODEL_VERSION=${BUILD_NUMBER} -t $IMAGE:${BUILD_NUMBER} -t $IMAGE:latest .'
                    }
                }
                stage('Deploy') {
                    steps {
                        sh '''
                        docker rm -f $CONTAINER || true
                        docker run -d --name $CONTAINER -p 8000:8000 $IMAGE:${BUILD_NUMBER}
                        '''
                    }
                }
                stage('Smoke test') {
                    steps {
                        sh '''
                        sleep 5
                        curl -f http://host.docker.internal:8000/health
                        curl -f http://host.docker.internal:8000/version
                        curl -f http://host.docker.internal:8000/metrics > /dev/null
                        curl -f -X POST http://host.docker.internal:8000/predict \
                          -H "Content-Type: application/json" \
                          -d '{"features":[5.1,3.5,1.4,0.2]}'
                        '''
                    }
                    post {
                        success {
                            sh 'docker tag $IMAGE:${BUILD_NUMBER} $IMAGE:stable'
                        }
                        failure {
                            sh '''
                            docker logs $CONTAINER || true
                            docker rm -f $CONTAINER || true
                            if docker image inspect $IMAGE:stable > /dev/null 2>&1; then
                                docker run -d --name $CONTAINER -p 8000:8000 $IMAGE:stable
                                echo "AUTOMATISCHE ROLLBACK naar $IMAGE:stable"
                            else
                                echo "Geen stable image om naar terug te rollen"
                            fi
                            '''
                        }
                    }
                }
            }
        }
        stage('Rollback') {
            when { expression { params.ROLLBACK_VERSION } }
            steps {
                sh '''
                docker image inspect $IMAGE:$ROLLBACK_VERSION > /dev/null
                docker rm -f $CONTAINER || true
                docker run -d --name $CONTAINER -p 8000:8000 $IMAGE:$ROLLBACK_VERSION
                sleep 5
                curl -f http://host.docker.internal:8000/health
                curl -f http://host.docker.internal:8000/version
                docker tag $IMAGE:$ROLLBACK_VERSION $IMAGE:stable
                echo "Rollback naar versie $ROLLBACK_VERSION geslaagd"
                '''
            }
        }
    }
    post {
        success { echo "Pipeline geslaagd" }
    }
}
