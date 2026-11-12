# AnchoredSupport
### AI-Powered Clinical Mental Health Support Platform

**Project Type:** Collaborative Software Engineering Project  
**Project Status:** Functional Prototype  
**Deployment:** Cloud Hosted

---

## 1. Project Overview

AnchoredSupport is an AI-powered mental health support platform designed to provide users with an accessible, conversational support experience while offering therapists and administrators tools to oversee and manage the platform.

The system combines conversational artificial intelligence, Retrieval-Augmented Generation (RAG), persistent conversation storage, role-based access control, and dedicated management dashboards.

The platform demonstrates how modern AI technologies and full-stack application development can be integrated into a mental health support environment.

AnchoredSupport is designed as a support tool and is not intended to replace professional mental health care, clinical diagnosis, or emergency services.

## 2. Project Objectives

The primary objectives of the project were to:

- Develop an interactive AI-powered mental health support experience.
- Integrate a knowledge-based retrieval system to provide relevant contextual information to AI responses.
- Implement secure user authentication and role-based access.
- Maintain persistent conversations so users can return to previous sessions.
- Provide therapists with tools to oversee assigned patients and review relevant conversations.
- Provide administrators with system-level management and monitoring capabilities.
- Deploy the application using cloud-based infrastructure.

## 3. Key Project Accomplishments

The project has progressed from an initial application prototype into a deployed, integrated full-stack system.

| Area | Accomplishment |
|---|---|
| Frontend Development | Developed a React-based interface with dedicated patient, therapist, and administrator experiences. |
| Backend Development | Implemented a FastAPI backend providing application APIs and business logic. |
| Authentication | Integrated JWT-based authentication and role-based access control. |
| Database Integration | Integrated Supabase PostgreSQL for persistent application data. |
| AI Integration | Connected an AI language model to generate conversational responses. |
| RAG Implementation | Implemented semantic embedding generation and vector-based knowledge retrieval. |
| Chat Persistence | Implemented persistent conversations and message history. |
| Therapist Dashboard | Developed functionality for therapist access to assigned patient information and conversations. |
| Administrator Dashboard | Implemented administrative views for system-level information and management. |
| Safety Functionality | Integrated safety-related event recording and notification functionality. |
| Cloud Deployment | Deployed frontend and backend services independently through Vercel. |

## 4. Core Platform Features

### 4.1 Patient Experience

The patient-facing application provides:

- AI-powered conversational mental health support.
- Persistent conversations and message history.
- Access to previous conversations across sessions.
- An interactive chat interface.
- Context-aware AI responses supported by knowledge retrieval.

### 4.2 Therapist Dashboard

The therapist dashboard provides functionality designed to support therapist oversight, including:

- Access to assigned patient information.
- Visibility into relevant patient conversations.
- Conversation review capabilities.
- Access to safety-related notifications and information.

### 4.3 Administrator Dashboard

The administrator dashboard provides system-level functionality, including:

- Administrative access to platform information.
- Visibility into system-level data.
- Management and monitoring capabilities.

### 4.4 Authentication and Access Control

Authentication and authorization are implemented on the backend using JSON Web Tokens (JWT).

The system incorporates role-based access control to distinguish between patient, therapist, and administrator permissions.

Protected backend endpoints validate authentication and enforce access restrictions based on the user's role.

## 5. Artificial Intelligence and RAG Architecture

A central component of AnchoredSupport is its Retrieval-Augmented Generation (RAG) implementation.

Rather than relying exclusively on the language model's existing knowledge, the platform incorporates a retrieval process that allows relevant information from a designated knowledge base to be incorporated into AI responses.

### RAG Pipeline

The implementation follows this general process:

1. **Knowledge Base:** Relevant reference documents are maintained within the project's knowledge base.
2. **Embedding Generation:** Text content is converted into numerical vector representations using the Sentence Transformers model `all-MiniLM-L6-v2`.
3. **Vector Storage:** Embeddings are stored in PostgreSQL using the pgvector extension.
4. **Semantic Retrieval:** When a user submits a message, the system generates a corresponding embedding and searches for semantically relevant information.
5. **Context Assembly:** Retrieved information is incorporated into the context provided to the language model.
6. **Response Generation:** The language model generates a conversational response using the supplied context.

This architecture allows the application to retrieve relevant reference material based on semantic similarity rather than relying exclusively on exact keyword matching.

### AI Technologies

| Component | Technology |
|---|---|
| Language Model Integration | OpenAI API |
| Embedding Model | Sentence Transformers `all-MiniLM-L6-v2` |
| Vector Search | PostgreSQL with pgvector |
| AI Architecture | Retrieval-Augmented Generation (RAG) |

## 6. Conversation Management and Data Persistence

Conversation persistence was implemented to ensure that chat history is retained beyond an individual browser session.

The general conversation lifecycle is:

1. An authenticated user initiates or selects a conversation.
2. The backend associates the conversation with the authenticated user.
3. User messages are processed through the AI conversation service.
4. Messages and generated responses are stored in the database.
5. Previous conversations can be retrieved when the user returns.
6. Conversation history remains available after refreshing or revisiting the application, subject to the user's permissions.

This provides continuity across sessions and establishes a persistent record of interactions within the application.

## 7. Technical Architecture

AnchoredSupport follows a layered application architecture consisting of a frontend, backend, database, and integrated AI services.

### Application Components

**Frontend — React and Vite**

Provides the user interface for patients, therapists, and administrators. It communicates with the backend through REST API requests.

**Backend — FastAPI**

Handles application logic, authentication, authorization, conversation management, AI orchestration, and communication with the database and external AI services.

**Database — Supabase PostgreSQL**

Stores application data, including user information, conversations, messages, and knowledge-base embeddings. The pgvector extension supports semantic similarity searches for the RAG pipeline.

**AI and Retrieval Services**

The backend coordinates embedding generation, vector-based knowledge retrieval, and OpenAI API requests to generate context-aware conversational responses.

### Application Request Flow

1. Users interact with the React frontend.
2. The frontend sends requests to the FastAPI backend.
3. The backend authenticates users and enforces role-based permissions.
4. Application services retrieve or update relevant information in Supabase.
5. For AI conversations, the RAG pipeline retrieves relevant knowledge-base content and supplies it as context to the language model.
6. The generated response is returned to the frontend, and conversation messages are persisted in the database.

### Technology Stack

| Component | Technology |
|---|---|
| Frontend | React |
| Frontend Build Tool | Vite |
| Backend Framework | FastAPI |
| Programming Languages | Python, JavaScript |
| Database | Supabase PostgreSQL |
| Vector Database Extension | pgvector |
| ORM | SQLAlchemy |
| Authentication | JSON Web Tokens (JWT) |
| AI Integration | OpenAI API |
| Embeddings | Sentence Transformers |
| Deployment | Vercel |
| API Communication | REST |

## 8. Security and Privacy Considerations

Security was considered throughout the development of the platform.

Implemented security-related functionality includes:

- JWT-based authentication.
- Backend authentication validation.
- Role-based authorization.
- Protected API endpoints.
- Database-backed user and conversation records.
- Cross-Origin Resource Sharing (CORS) configuration.
- Separation of frontend and backend deployment environments.

The application uses role-based permissions to help restrict access to protected resources.

**Important:** Although security controls have been implemented, the prototype has not been independently certified or validated for regulatory compliance. A formal security assessment, privacy review, and applicable healthcare regulatory assessment should be completed before handling real patient information in a clinical environment.

## 9. Production Deployment

The application is deployed using Vercel, with the frontend and backend maintained as separate deployments.

The production architecture separates the user-facing application from the backend API, allowing each component to be maintained and deployed independently.

The deployed application has been tested for its primary functionality, including authentication, AI conversations, conversation persistence, and dashboard access.

**Access to the live AI application is managed separately from this public project documentation.** This helps keep demonstrations controlled and allows application usage and associated AI service costs to be monitored.

## 10. Current Implementation Status

The following capabilities have been implemented, with the primary user-facing workflows verified in the deployed application.

| Capability | Status |
|---|---|
| User authentication and login | Implemented and verified |
| AI-powered conversations | Implemented and verified |
| Conversation persistence | Implemented and verified |
| Message history after refresh | Implemented and verified |
| Therapist dashboard | Implemented and verified |
| Administrator dashboard | Implemented and verified |
| Supabase database integration | Implemented |
| RAG and semantic retrieval | Implemented |
| Production frontend deployment | Live |
| Production backend deployment | Live |

## 11. Handover and Future Considerations

AnchoredSupport provides a foundation for continued development and organizational adoption.

Potential next steps for the receiving organization include:

- Conducting a formal security and privacy assessment.
- Evaluating applicable healthcare data protection and regulatory requirements.
- Reviewing AI response quality and retrieval accuracy.
- Expanding the knowledge base and improving document management.
- Implementing additional monitoring, logging, and operational alerting.
- Establishing backup, recovery, and database maintenance procedures.
- Reviewing deployment ownership, credentials, and environment configuration.
- Conducting additional usability and accessibility testing.
- Evaluating scalability and performance under increased usage.
- Establishing AI usage controls, rate limits, and cost monitoring.

These considerations represent opportunities for continued development and should not be interpreted as functionality already completed.

## 12. Project Deliverables

The project delivers an integrated application consisting of:

- A React-based frontend application.
- A FastAPI backend and REST API.
- A Supabase PostgreSQL database integration.
- An AI-powered conversational support service.
- A Retrieval-Augmented Generation pipeline.
- Persistent conversation and message management.
- Patient, therapist, and administrator interfaces.
- A deployed functional prototype.

---

**AnchoredSupport — AI-Powered Clinical Mental Health Support Platform**

*Developed as a collaborative software engineering project, with a focus on integrating artificial intelligence, secure application development, and persistent data management into an accessible mental health support platform.*
