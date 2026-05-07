pipeline {
    agent any

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
                sh 'pip3 install -r requirements.txt'
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

        stage('Run Parallel Tests') {
            steps {

                catchError(
                    buildResult: 'SUCCESS',
                    stageResult: 'FAILURE'
                ) {

                    sh '''
                    pytest -n 2 \
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
        }
    }
}