Demo Guide

Starting the Backend:
    - cd backend
    - python -m uvicorn app.main:app --reload

Starting the Frontend:
    - cd frontend 
    - npm run dev

Patient Workflow*
    1.) Login
    2.) View Dashboard
    3.) Open Messages
    4.) Read Knowledge Base
- For first time users, create account with name, email address, and password; agree to terms and conditions after logging in with newly created credentials

Current Known Limitations
    - Sign out functionality has not yet been implemented. (Medium Severity)
    - Chat responses currently return a placeholder message indicating backend integration is pending. (Medium Severity)
    - Newly created conversations are not displayed in the chat history. (Medium Severity)

Environment Status
    - Backend successfully starts and runs without errors.
    - Frontend successfully builds and runs without errors.
    - User authentication and application navigation are operational.