# Synthetic Demo Data Overview

## Purpose
The synthetic demo data file (`Paul_M2_Synthetic_Demo_Data.json`) provides all sample records used during Milestone 2 demonstrations and testing. It contains fictional patients, therapists, an admin user, role assignments, and conversation histories. This dataset ensures the system can display meaningful content even before real database integration is completed.

The file is designed to support:
- Functional testing
- UI rendering in the React frontend
- Demo walkthroughs
- Website documentation screenshots
- Role-based behavior validation

All data is fully synthetic and safe for academic use.

---

## File Location in the Repository

The demo data file is stored in: backend/Paul_M2_Synthetic_Demo_Data.json


This location keeps the dataset close to the backend code that will load it while maintaining a clean separation from the frontend.

---

## How the Backend Uses the File

The Python FastAPI backend reads the JSON file and exposes its contents through an API endpoint. This allows the frontend to fetch demo data dynamically rather than embedding it directly.

### Example Backend Flow

1. FastAPI receives a request at: GET /api/Paul_M2_Synthetic_Demo_Data

2. The backend will load the JSON file:
```python
with open("backend/Paul_M2_Synthetic_Demo_Data.json") as f:
    data = json.load(f)

3. The backend returns the data as a JSON response.
This approach keeps the architecture clean and avoids hardcoding demo content inside the frontend.

The React frontend does not import the JSON file directly.
Instead, it fetches the data from the backend API.

useEffect(() => {
  fetch("/api/demo-data")
    .then(res => res.json())
    .then(data => setDemoData(data));
}, []);

Once loaded, the frontend uses the data to populate:

- Patient dashboard
- Therapist dashboard
- Admin dashboard
- Conversation views
- Assignment lists

This ensures the UI displays realistic content during demos and testing.

