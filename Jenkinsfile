#!groovy
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
        stage('Checkout source code and generate add user script') {
            steps {
                script {
                    // git credentialsId: 'xvt-product-registration1', url: 'git@github.com:XVTSolutions/ecs-auto-scale-lambda.git'
                    sh '''
#!/bin/sh
my_UID=$(id -u)
my_GID=$(id -g)
my_NAME=$(whoami)
cat <<EOF > add-user.sh
#!/bin/sh
if [ -f "/etc/alpine-release" ]; then
	addgroup -g $my_GID $my_NAME
	adduser -u $my_UID -g $my_GID -D -S $my_NAME
else
	groupadd -g $my_GID $my_NAME
	useradd -u $my_UID -g $my_GID $my_NAME
fi

mkdir -p /home/$my_NAME >/dev/null 2>&1
chown -R $my_NAME:$my_GID /home/$my_NAME
echo \\$WORKSPACE
# $WORKSPACE
EOF
'''
                    sh 'chmod +x add-user.sh'
                    sh 'cat add-user.sh'
                }
            }
        }
    
       stage('Build and Push to ECR') {
            steps {
                script {
                    docker.image('xvtsolutions/python3-aws-ansible:2.7.0').withRun('-u root --volumes-from xvt_jenkins') { c->
                        sh "docker exec --workdir ${WORKSPACE} ${c.id} bash ./add-user.sh"
                        sh "docker exec --user jenkins --workdir ${WORKSPACE} ${c.id} ./build.sh"
                    }    
                }
            }
        }
    }
}
