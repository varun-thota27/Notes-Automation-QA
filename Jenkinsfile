pipeline {
    agent any

    stages {

        stage('Checkout Source Code') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/varun-thota27/Notes-Automation-QA.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'pip install -r requirements.txt'
            }
        }

        stage('Create Report Directories') {
            steps {
                bat '''
                if not exist Reports mkdir Reports
                if not exist Screenshots mkdir Screenshots
                if not exist Logs mkdir Logs
                '''
            }
        }

        // stage('Run Parallel Tests') {
        //     steps {
        //         bat '''
        //         pytest -n 4 --html=Reports/report.html --self-contained-html
        //         exit 0
        //         '''
        //     }
        // }
        // stage('Run Parallel Tests') {
        //     steps {
        //         bat 'pytest -n 2 --html=Reports/report.html --self-contained-html'
        //     }
        // }
        stage('Run Parallel Tests') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    bat 'pytest -n 2 --html=Reports/report.html --self-contained-html'
                }
            }
        }

        // stage('Archive Reports') {
        //     steps {
        //         archiveArtifacts artifacts: 'Reports/*', fingerprint: true
        //         archiveArtifacts artifacts: 'Screenshots/*', fingerprint: true
        //         archiveArtifacts artifacts: 'Logs/*', fingerprint: true
        //     }
        // }
        stage('Archive Reports') {
            steps {
                archiveArtifacts artifacts: 'Reports/*',
                                fingerprint: true,
                                allowEmptyArchive: true

                archiveArtifacts artifacts: 'Screenshots/*',
                                fingerprint: true,
                                allowEmptyArchive: true

                archiveArtifacts artifacts: 'Logs/*',
                                fingerprint: true,
                                allowEmptyArchive: true
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