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
- [x] **Phase 3: Configure VK API Integration**
  - [x] **Step 3.1: Set up VK API credentials**
    - [x] Update .env file with test VK_ACCESS_TOKEN
    - [x] Created documentation for obtaining VK access token
  - [x] **Step 3.2: Test VK group addition**
    - [x] Attempted to add test groups
    - [x] Identified invalid token error: "User authorization failed: invalid access_token (4)"
- [ ] **Phase 4: Fix VK API Token Authentication**
  - [ ] **Step 4.1: Generate valid VK API token**
    - [ ] Follow documentation in docs/VK_API_SETUP.md to create valid token
    - [ ] Update .env with correct token format and permissions
  - [ ] **Step 4.2: Test VK API connectivity**
    - [ ] Test adding popular VK group
    - [ ] Verify posts and comments parsing
- [ ] **Phase 5: Complete UI Functionality Testing**
  - [ ] Test all pages for correct data loading
  - [ ] Verify statistics display correctly
  - [ ] Test keywords management functionality
  - [ ] Test comments display and filtering
