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
