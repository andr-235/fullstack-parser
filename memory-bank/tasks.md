# Task List

## VAN-01: Stabilize and Complete Frontend UI Refactor (Strategy: Revert to pnpm)

- [x] **Phase 1: Fix Frontend Build by Reverting to pnpm**
  - [x] **Step 1.1: Update docker-compose.yml**
    - [x] Remove the volume mount for .bun from the frontend service, as it is related to the Bun package manager.
  - [x] **Step 1.2: Restore pnpm-lock.yaml**
    - [x] **User Action:** Run pnpm install in the frontend/ directory. This is necessary to regenerate the pnpm-lock.yaml file based on the latest changes in package.json. Without this file, the Docker build will fail.
  - [x] **Step 1.3: Verify Docker Build**
    - [x] Run docker-compose up --build to confirm the frontend service builds and starts correctly.
- [x] **Phase 2: Fix API Endpoints 404 Errors**
  - [x] **Step 2.1: Diagnose API connectivity issues**
    - [x] Identified FastAPI requires trailing slash in endpoints
    - [x] Found VK access token is not configured
  - [x] **Step 2.2: Fix API client endpoints**
    - [x] Added trailing slash to all API endpoints (groups/, keywords/, etc.)
    - [x] Verified backend services are running correctly
  - [x] **Step 2.3: Test API connectivity**
    - [x] Confirmed GET requests work after trailing slash fix
    - [x] Verified frontend can load without 404 errors
- [ ] **Phase 3: Configure VK API Integration**
  - [ ] **Step 3.1: Set up VK API credentials**
    - [ ] Update .env file with valid VK_ACCESS_TOKEN
    - [ ] Provide instructions for obtaining VK access token
  - [ ] **Step 3.2: Test VK group addition**
    - [ ] Attempt to add test group https://vk.com/livebir
    - [ ] Verify group data is fetched and stored correctly
- [ ] **Phase 4: Complete UI Functionality Testing**
  - [ ] Test all pages for correct data loading
  - [ ] Verify statistics display correctly
  - [ ] Test keywords management functionality
  - [ ] Test comments display and filtering
