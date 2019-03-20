pipeline {
    environment {
        DOCKER_TLS_VERIFY=true
        DOCKER_TLS=true
        DOCKER_HOST="tcp://docker-host.xvt.internal:2376"
        DOCKER_CA_PATH="/var/jenkins_home/.docker"
        DOCKER_CERT_PATH="/var/jenkins_home/.docker"
     }
    agent { label 'master' }
    stages {
        stage('Parse GIT_REVISION') {
            steps {
                script {
                env.GIT_REVISION = sh(returnStdout: true, script: """###@echo off
                    git rev-parse --short HEAD"""
                ).trim()
                echo "Check out REVISION: $GIT_REVISION"
                VERSION_PREFIX = "v1.${BUILD_NUMBER}."
                env.BUILD_VERSION = VersionNumber projectStartDate: '2018-11-07', versionNumberString: "${GIT_REVISION}", versionPrefix: "${VERSION_PREFIX}", worstResultForIncrement: 'SUCCESS'
                sh 'git clean -fdx'
                }
            }
        }

        stage('Load ansible-common') {
            steps {
                script {
                  checkout changelog: false, poll: false, scm: [$class: 'GitSCM', branches: [[name: '*/jenkins']], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'RelativeTargetDirectory', relativeTargetDir: 'ansible-common']], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'xvt-product-registration1', url: 'git@github.com:XVTSolutions/ansible-common.git']]]
                  utils = load("${WORKSPACE}/ansible-common/jenkins-lib/deployment-helper.groovy")
                }//script
            }//steps
        }//stage

        stage('Generate scripts') {
            steps {
                script {
                  utils.generate_add_user_script()
                  env.PROFILE = 'xvt_aws' // Used to list artifacts upload in the bucket
                  utils.generate_aws_environment()
                  sh '''cat <<EOF > build.sh
#!/bin/bash -e
mkdir build
cp -a src/* build
(cd build; zip -r ../ecs_auto_scale-${BUILD_VERSION}.zip *)

echo "Current number artifacts stored is displayed below. If too many get there and clean it up manually"

( aws s3 ls s3://xvt-public-repo/pub/devops/ --profile xvt_aws --region ap-southeast-2 | grep ecs_auto_scale ) || true
EOF
'''
                    sh 'chmod +x build.sh'
                    sh 'cat build.sh'
                }//script
            }//steps
        }//stage

        stage('Run Build Script') {
            steps {
                script {
                    utils.run_build_script()
                }//script
            }//steps
        }//stage

        stage('Push artifact to S3 bucket') {
            when {
                expression {
                    return ( ['jenkins', 'develop', 'master'].contains(env.BRANCH_NAME) ||
                      env.BRANCH_NAME ==~ /release\-[\d\-\.]+/
                    )
                }//expression
            }//when
            steps {
                withAWS(credentials: 'xvt_aws') {
                    s3Upload acl: 'Private', bucket: 'xvt-public-repo', cacheControl: '', file: "ecs_auto_scale-${BUILD_VERSION}.zip", metadatas: [''], path: 'pub/devops/', sseAlgorithm: '', workingDir: ''
                }//withAWS
            }//steps
        }//stage

    }//stages

    post {
        always {
            script {
                if ( env.BRANCH_NAME ==~ /release.*/ ) {
                   properties([buildDiscarder(logRotator(artifactDaysToKeepStr: '', artifactNumToKeepStr: '', daysToKeepStr: '', numToKeepStr: ''))])
                }
                else if (env.BRANCH_NAME == "develop" || env.BRANCH_NAME == 'master') {
                   properties([buildDiscarder(logRotator(artifactDaysToKeepStr: '', artifactNumToKeepStr: '7', daysToKeepStr: '', numToKeepStr: ''))])
                }
                else {
                   properties([buildDiscarder(logRotator(artifactDaysToKeepStr: '', artifactNumToKeepStr: '1', daysToKeepStr: '', numToKeepStr: ''))])
                }

              currentBuild.description = """VERSION: ${BUILD_VERSION}"""
            }
        }
        success {
            script {
                sh 'rm -f artifact_data.yml'
                writeYaml file: 'artifact_data.yml', data: [
                        build_number: "${BUILD_NUMBER}",
                        branch_name: "${BRANCH_NAME}",
                        revision: "${GIT_REVISION}",
                        upstream_build_url: "${BUILD_URL}",
                        upstream_job_name: "${JOB_NAME}",
                        upstream_job_base_name: "${JOB_BASE_NAME}",
                        artifact_version: "${BUILD_VERSION}"
                    ]
                archiveArtifacts allowEmptyArchive: true, artifacts: 'artifact_data.yml', fingerprint: true, onlyIfSuccessful: true
                cleanWs cleanWhenFailure: false, cleanWhenNotBuilt: false, cleanWhenUnstable: false, deleteDirs: true, disableDeferredWipeout: true, notFailBuild: true, patterns: [[pattern: 'PerformanceTesting', type: 'INCLUDE'], [pattern: '*', type: 'INCLUDE']]
            }//script
        }
        failure {
            script {
                slackSend baseUrl: 'https://xvt.slack.com/services/hooks/jenkins-ci/', botUser: true, channel: '#devops', message: "@here CRITICAL - ${JOB_NAME} (${BUILD_URL})", teamDomain: 'xvt', tokenCredentialId: 'jenkins-ci-integration-token', color: "danger"
            }
        }
    }

}
