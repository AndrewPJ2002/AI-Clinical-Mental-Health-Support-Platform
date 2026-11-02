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

Therapist Workflow
    1.) Login
    2.) Assigned patients, including patients with flagged conversation(s)
    3.) Click on a patient, and the therapist can see the conversations from the patient.
    4.) Clicking on a flagged conversation has the option for the therapist to mark the conversation as reviewed.

Admin Workflow
    1.) Login
    2.) Check dashboard to see the total number of users, including how many therapists and patients have registered.
    3.) Click a hyperlink on the dashboard to see the directory of all the accounts for the website, including details like name, email, role, and date of account creation.
    4.) The admin can check and even re-assign a therapist to a particular patient.