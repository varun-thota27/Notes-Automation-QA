pipeline {

    agent any

    environment {
        GRID_URL = 'http://host.docker.internal:4444'
    }

    stages {

        stage('Checkout Source Code') {

            steps {

                git branch: 'main',
                    url: 'https://github.com/varun-thota27/Notes-Automation-QA.git'
            }
        }


        stage('Verify Python Installation') {

            steps {

                sh 'python3 --version'
                sh 'pip3 --version'
            }
        }


        stage('Install Dependencies') {

            steps {

                sh '''
                pip3 install --break-system-packages -r requirements.txt
                '''
            }
        }


        stage('Create Report Directories') {

            steps {

                sh '''
                mkdir -p Reports
                mkdir -p Screenshots
                mkdir -p Logs
                mkdir -p allure-results
                '''
            }
        }


        stage('Start Selenium Grid') {

            steps {

                sh '''
                docker compose up -d

                echo "Waiting for Selenium Grid to initialize..."

                sleep 25

                docker ps
                '''
            }
        }


        stage('Run Parallel Tests') {

            steps {

                catchError(
                    buildResult: 'SUCCESS',
                    stageResult: 'FAILURE'
                ) {

                    sh '''
                    python3 -m pytest -n 2 \
                    --html=Reports/report.html \
                    --self-contained-html \
                    --alluredir=allure-results
                    '''
                }
            }
        }


        stage('Archive Reports') {

            steps {

                archiveArtifacts(
                    artifacts: 'Reports/*',
                    fingerprint: true,
                    allowEmptyArchive: true
                )

                archiveArtifacts(
                    artifacts: 'Screenshots/*',
                    fingerprint: true,
                    allowEmptyArchive: true
                )

                archiveArtifacts(
                    artifacts: 'Logs/*',
                    fingerprint: true,
                    allowEmptyArchive: true
                )

                archiveArtifacts(
                    artifacts: 'allure-results/*',
                    fingerprint: true,
                    allowEmptyArchive: true
                )
            }
        }


        stage('Generate Allure Report') {

            steps {

                allure([
                    includeProperties: false,
                    jdk: '',
                    results: [[path: 'allure-results']],
                    commandline: 'Allure'
                ])
            }
        }
    }


    post {

        always {

            publishHTML([

                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'Reports',
                reportFiles: 'report.html',
                reportName: 'Pytest HTML Report'
            ])


            sh '''
            docker compose down
            '''
        }
    }
}