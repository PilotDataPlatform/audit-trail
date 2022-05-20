pipeline {
    agent { label 'small' }
    environment {
      imagename_dev = "ghcr.io/pilotdataplatform/audit-trail"
      imagename_staging = "ghcr.io/pilotdataplatform/audit-trail"
      commit = sh(returnStdout: true, script: 'git describe --always').trim()
      registryCredential = 'pilot-ghcr'
      registryURL = 'https://github.com/PilotDataPlatform/audit-trail.git'
      registryURLBase = 'https://ghcr.io'
      dockerImage = ''
    }

    stages {

    stage('Git clone for dev') {
        when {branch "develop"}
        steps{
          script {
          git branch: "develop",
              url: "$registryURL",
              credentialsId: 'lzhao'
            }
        }
    }

    stage('DEV unit test') {
        when {branch "develop"}
        steps{
          withCredentials([
            string(credentialsId:'VAULT_TOKEN', variable: 'VAULT_TOKEN'),
            string(credentialsId:'VAULT_URL', variable: 'VAULT_URL'),
            file(credentialsId:'VAULT_CRT', variable: 'VAULT_CRT')
          ]) {
            sh """
            export VAULT_TOKEN=${VAULT_TOKEN}
            export VAULT_URL=${VAULT_URL}
            export VAULT_CRT=${VAULT_CRT}
            pip install --user poetry==1.1.12
            ${HOME}/.local/bin/poetry config virtualenvs.in-project true
            ${HOME}/.local/bin/poetry config http-basic.pilot 
            ${HOME}/.local/bin/poetry install --no-root --no-interaction
            ${HOME}/.local/bin/poetry run pytest --verbose -c tests/pytest.ini
            """
          }
        }
    }

    stage('DEV Build and push image') {
      when {branch "develop"}
      steps{
        script {
            docker.withRegistry("$registryURLBase", registryCredential) {
                customImage = docker.build("$imagename_dev:$commit", ".")
                customImage.push()
            }    
        }
      }
    }
    stage('DEV Remove image') {
      when {branch "develop"}
      steps{
        sh "docker rmi $imagename_dev:$commit"
      }
    }

    stage('DEV Deploy') {
      when {branch "develop"}
      steps{
        build(job: "/VRE-IaC/UpdateAppVersion", parameters: [
          [$class: 'StringParameterValue', name: 'TF_TARGET_ENV', value: 'dev' ],
          [$class: 'StringParameterValue', name: 'TARGET_RELEASE', value: 'provenance' ],
          [$class: 'StringParameterValue', name: 'NEW_APP_VERSION', value: "$commit" ]
        ])
      }
    }
  }
  post {
      failure {
        slackSend color: '#FF0000', message: "Build Failed! - ${env.JOB_NAME} $commit  (<${env.BUILD_URL}|Open>)", channel: 'jenkins-dev-staging-monitor'
      }
  }

}
 
