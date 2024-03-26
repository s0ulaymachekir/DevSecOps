pipeline {
	agent any
    
	environment {
    	registry ='soulaymach/devsecops.project'
    	registryCredential = 'dockerhub_id'
    	IMAGE_NAME = 'flaskapp'
	}
   

	stages {
    	stage('Clean Workspace') {
        	steps {
            	deleteDir()
        	}  
    	}
    	stage('CLONE') {
        	steps {
            	git branch: 'main', url: 'https://github.com/s0ulaymachekir/DevSecOps.git'
        	}
    	}
    
    	stage('Build Docker Image') {
        	steps {
            	script {
                	sh 'docker build -t $IMAGE_NAME .'
            	}
        	}
    	}
   	 
    	stage('Build Docker compose') {
        	steps {
            	script {
               	docker.withRegistry( '', registryCredential ) {
                   	sh 'docker compose build'
                   	sh ' docker push soulaymach/flaskapp:flaskapp'
              	 
                  	 
               	}
            	}           	 
        	}
    	}
	}  
	post {
    	always {
        	script {
            	sh 'docker rmi $IMAGE_NAME || true'
        	}
    	}
	}
}

node {
  stage('SCM'){
    checkout scm
  }
  stage('SonarQube Analysis'){
    det scannerHome = tool 'SonnarScanner';
    withSonarQubeEnv(){
      sh "${scannerHome}/bin/sonar-scanner"
    }
  }
}
