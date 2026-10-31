// This file relates to internal XMOS infrastructure and should be ignored by external users

@Library('xmos_jenkins_shared_library@v0.52.0') _

getApproval()
pipeline {
    agent none

    options {
        skipDefaultCheckout()
        timestamps()
        buildDiscarder(xmosDiscardBuildSettings(onlyArtifacts = false))
    }

    stages {
        stage('Validate skills and documentation') {
            agent {
                label 'x86_64 && linux && documentation'
            }

            stages {
                stage('Checkout') {
                    steps {
                        script {
                            def (server, user, repo) = extractFromScmUrl()
                            env.REPO_NAME = repo
                        }
                        dir(REPO_NAME) {
                            checkoutScmShallow()
                        }
                    }
                }

                stage('Test') {
                    steps {
                        dir("${REPO_NAME}/tests") {
                            createVenv(reqFile: 'requirements.txt')
                            withVenv {
                                runPytest('-n=1')
                            }
                        }
                    }
                }
            }

            post {
                cleanup {
                    deleteDir()
                }
            }
        }
    }
}
