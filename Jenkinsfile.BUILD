pipeline {
    environment {
        DOCKER_TLS_VERIFY=true
        DOCKER_TLS=true
        DOCKER_HOST="tcp://docker-host.xvt.internal:2376"
        DOCKER_CA_PATH="/var/jenkins_home/.docker"
        DOCKER_CERT_PATH="/var/jenkins_home/.docker"
     }
    agent { label 'master' }
    options { timestamps() }
    stages {
        stage('Parse GIT_REVISION') {
            steps {
                script {
                GIT_REVISION = sh(returnStdout: true, script: """###@echo off
                    git rev-parse --short HEAD"""
                ).trim()
                echo "Check out REVISION: $GIT_REVISION"
                }
            }
        }

        stage('Load ansible-common') {
            steps {
                script {
                  checkout changelog: false, poll: false, scm: [$class: 'GitSCM', branches: [[name: '*/${BRANCH}']], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'RelativeTargetDirectory', relativeTargetDir: 'ansible-common']], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'xvt-product-registration1', url: 'git@github.com:XVTSolutions/ansible-common.git']]]
                  utils = load("${WORKSPACE}/ansible-common/jenkins-lib/deployment-helper.groovy")
                }//script
            }//steps
        }//stage

        stage('Generate scripts') {
            steps {
                script {
                  utils.generate_add_user_script()
                  sh '''cat <<EOF > build.sh
#!/bin/sh -e
rm -f ecs_auto_scale*.zip
rm -rf build
mkdir build
cp -a src/* build
(cd build; zip -r ../ecs_auto_scale.${GIT_REVISION}.zip *)
ls -l ecs_auto_scale.${GIT_REVISION}.zip
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

            withAWS(credentials: 'xvt_aws') {
                s3Upload acl: 'Private', bucket: 'xvt-public-repo', cacheControl: '', file: "ecs_auto_scale.${GIT_REVISION}.zip", metadatas: [''], path: 'pub/devops', sseAlgorithm: '', workingDir: ''
                sh '''
                echo "Current number artifacts stored is displayed below. If too many get there and clean it up manually"
                aws s3 ls s3://xvt-public-repo/pub/devops | grep ecs_auto_scale
                '''
            }//withAWS
        }//stage

    }//stages
}
