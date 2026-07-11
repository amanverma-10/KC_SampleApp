# KC_SampleApp
Sample app for Keycloak Capabilities

This project demonstrates a full-stack integration with **Keycloak** for authentication and authorization. It consists of a React frontend (built with Vite) and a Python FastAPI backend. 

The frontend acts as a **Public Client** logging users in via Keycloak, and securely forwards the JWT Access Token (Bearer) to the backend. The backend acts as a **Resource Server**, fetching the Keycloak Realm's public keys to validate incoming tokens before granting access to protected endpoints.

## Tech Stack
* **Frontend:** React, TypeScript, Vite, `keycloak-js`, Axios
* **Backend:** Python, FastAPI, Uvicorn, `python-jose` (for JWT validation)
* **Auth:** Keycloak (running locally)

---

## Prerequisites

1. **Keycloak Server**: 
   You must have a local Keycloak instance running on `http://localhost:8080`.
2. **Keycloak Configuration**:
   * **Realm Name:** `SampleApp`
   * **Client ID:** `SampleClient`
   * **Client Authentication:** Off / Access Type: Public
   * **Valid Redirect URIs:** `http://localhost:5173/*`
   * **Web Origins:** `+` (or `http://localhost:5173`)
   * Ensure you have at least one test User created in this Realm with a password.

---

## How to Run

### Method 1: Using the provided bash script (Local)
Ensure you have `npm` and `python3` installed.

1. Make the script executable (if it isn't already):
   ```bash
   chmod +x start.sh
   ```
2. Run the script:
   ```bash
   ./start.sh
   ```
This will install dependencies for both the frontend and backend, and start them concurrently. 
* Frontend will be accessible at: `http://localhost:5173`
* Backend will be accessible at: `http://localhost:8000`

### Method 2: Using Docker Compose
Ensure you have Docker and Docker Compose installed.

1. Build and run the containers:
   ```bash
   docker compose up --build
   ```
* The frontend is served via an Nginx container on port `5173`.
* The backend is served on port `8000`.
* The backend container uses `host.docker.internal` to successfully communicate with Keycloak running on your host machine.

---

## Testing the Application

1. Open `http://localhost:5173` in your browser.
2. Click **Call Public API**. This will hit the FastAPI public endpoint and succeed immediately.
3. Click **Call Private API**. This will be blocked by the frontend, instructing you to log in.
4. Click **Login with Keycloak**. You will be redirected to your Keycloak server. Log in with your test user credentials.
5. After being redirected back, your user profile will be displayed.
6. Click **Call Private API** again. The React app will attach your active JWT token to the request, the FastAPI server will validate the signature, and you will receive a successful response!

---

## CI/CD Pipeline (Jenkins)

This repository includes a `Jenkinsfile` at the root directory to support automated integration pipelines.

### Pipeline Stages
1. **Setup Dependencies**: Installs node modules for the React frontend and sets up a Python virtual environment with test dependencies for the backend.
2. **Lint Frontend**: Runs ESLint validation on the frontend React codebase.
3. **Test Backend**: Executes pytest unit tests and exports test results as JUnit XML reports.
4. **Build Frontend**: Builds the production bundle of the React frontend to verify compiling correctness.
5. **Docker Compose Build Verification**: Verifies the syntax and integrity of all `Dockerfile`s in the docker-compose setup.

### Running Jenkins Locally using Docker

A custom Jenkins Docker image setup is provided under the `ci-cd/` directory. It installs the Docker CLI and useful pipeline plugins (Blue Ocean, Docker Workflow).

1. **Build the Custom Jenkins Image**:
   ```bash
   cd ci-cd
   docker build -t myjenkins-blueocean:2.568.1-1 .
   ```

2. **Run Jenkins Container**:
   Run the container configured for Docker-in-Docker (DinD) integration (stopping and removing any existing container first):
   ```bash
   docker stop jenkins-blueocean || true
   docker rm jenkins-blueocean || true
   docker run \
     --name jenkins-blueocean \
     --restart=on-failure \
     --detach \
     --network jenkins \
     --env DOCKER_HOST=tcp://docker:2376 \
     --env DOCKER_CERT_PATH=/certs/client \
     --env DOCKER_TLS_VERIFY=1 \
     --publish 8080:8080 \
     --publish 50000:50000 \
     --volume jenkins-data:/var/jenkins_home \
     --volume jenkins-docker-certs:/certs/client:ro \
     myjenkins-blueocean:2.568.1-1
   ```

3. **Setup Pipeline in Jenkins**:
   * Access Jenkins at `http://localhost:8080`.
   * Create a **Pipeline** job.
   * Set SCM to Git, point it to this repository, and configure the script path to target the `Jenkinsfile` at the root.
