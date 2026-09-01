pipeline {
    agent any

    options {
        disableConcurrentBuilds()
        timestamps()
    }

    triggers {
        pollSCM('H/2 * * * *')
    }

    environment {
        IMAGE_REPO = 'ghcr.io/seokkt/ec2-gitops-app'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Set Version') {
            steps {
                script {
                    env.IMAGE_TAG = sh(
                        script: 'git rev-parse --short=7 HEAD',
                        returnStdout: true
                    ).trim()

                    echo "IMAGE_TAG=${env.IMAGE_TAG}"
                }
            }
        }

        stage('Test') {
            steps {
                sh '''
                    docker build \
                      --target test \
                      -t demo-api-test:$BUILD_NUMBER \
                      .

                    docker run --rm \
                      demo-api-test:$BUILD_NUMBER
                '''
            }
        }

        stage('Build') {
            steps {
                sh '''
                    docker build \
                      --target runtime \
                      -t $IMAGE_REPO:$IMAGE_TAG \
                      .
                '''
            }
        }

        stage('Push') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'ghcr-credential',
                        usernameVariable: 'GHCR_USER',
                        passwordVariable: 'GHCR_TOKEN'
                    )
                ]) {
                    sh '''
                        set +x

                        echo "$GHCR_TOKEN" \
                        | docker login ghcr.io \
                          -u "$GHCR_USER" \
                          --password-stdin

                        docker push \
                          "$IMAGE_REPO:$IMAGE_TAG"

                        docker logout ghcr.io
                    '''
                }
            }
        }

        stage('Cleanup') {
            steps {
                sh '''
                    docker image rm \
                      demo-api-test:$BUILD_NUMBER \
                      || true
                '''
            }
        }
    }

    post {
        success {
            echo "CI SUCCESS: ${IMAGE_REPO}:${IMAGE_TAG}"
        }

        failure {
            echo 'CI FAILED'
        }
    }
}