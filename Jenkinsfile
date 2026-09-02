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
                      --build-arg APP_VERSION=$IMAGE_TAG \
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

        stage('Update GitOps Repository') {
            steps {
                withCredentials([
                    gitUsernamePassword(
                        credentialsId: 'github-gitops-token',
                        gitToolName: 'Default'
                    )
                ]) {
                    sh '''
                        set -eu

                        GITOPS_DIR="$(mktemp -d)"
                        trap 'rm -rf "$GITOPS_DIR"' EXIT

                        git clone \
                          --branch main \
                          --single-branch \
                          https://github.com/seokkt/ec2-gitops-platform.git \
                          "$GITOPS_DIR"

                        KUSTOMIZATION="$GITOPS_DIR/kubernetes/apps/demo-api/kustomization.yaml"

                        sed -i -E \
                          "s|^([[:space:]]*newTag:)[[:space:]]*.*$|\\1 $IMAGE_TAG|" \
                          "$KUSTOMIZATION"

                        test "$(grep -Ec "^[[:space:]]*newTag:[[:space:]]*$IMAGE_TAG$" "$KUSTOMIZATION")" -eq 1

                        git -C "$GITOPS_DIR" config user.name "Jenkins"
                        git -C "$GITOPS_DIR" config user.email "jenkins@localhost"
                        git -C "$GITOPS_DIR" add \
                          kubernetes/apps/demo-api/kustomization.yaml

                        if git -C "$GITOPS_DIR" diff --cached --quiet; then
                          echo "GitOps repository already references $IMAGE_TAG"
                        else
                          git -C "$GITOPS_DIR" commit \
                            -m "ci: deploy demo-api $IMAGE_TAG"
                          git -C "$GITOPS_DIR" push origin HEAD:main
                        fi
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
