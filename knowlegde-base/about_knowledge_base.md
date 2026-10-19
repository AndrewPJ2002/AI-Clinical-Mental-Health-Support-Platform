# Knowledge Base Content Overview

## Purpose
The Knowledge Base provides structured educational content used throughout Milestone 2.  
It consists of five Markdown files, each covering a core mental‑health topic:
- Anxiety & Coping  
- Stress Management  
- Sleep & Wellness  
- Healthy Relationships  
- Crisis Resources  

These documents allow the system to display meaningful, realistic information during demos, testing, and UI walkthroughs — without requiring a real database or external content source.

All content is fully synthetic and created specifically for academic demonstration.

---

## File Location in the Repository

All Knowledge Base files are stored in:   
Example structure:
    knowledge_base/
    anxiety.md
    stress_management.md
    sleep_wellness.md
    healthy_relationships.md
    crisis_resources.md


This location keeps the content close to the backend logic that loads and serves it.
---
## How the Backend Uses the Files

The backend exposes each Markdown file through a dedicated API endpoint.  
This allows the frontend to request content dynamically, just like it would with a real database or CMS.

### Example Backend Flow

1. The frontend sends a request such as:
    GET knowledge-base/anxiety

2. FastAPI loads the corresponding Markdown file:
```python
with open(f"backend/knowledge_base/{topic}.md") as f:
    content = f.read()
3. The backend returns the raw Markdown text.
This keeps the architecture clean and ensures the frontend always receives content through an API layer.

The React frontend does not import the Markdown files directly, but it fetches them from the backend and renders them using a Markdown component.
useEffect(() => {
  fetch("/api/knowledge-base/anxiety")
    .then(res => res.text())
    .then(md => setContent(md));
}, []);

The frontend then displays the content using a Markdown renderer such as:
    <ReactMarkdown>{content}</ReactMarkdown>
This allows the UI to show Educational panels, Knowledge base tabs, Pop‑ups or modal content, Demo walkthrough information, and All without hardcoding text inside React components.

