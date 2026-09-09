# Clinician-Connected AI Conversation Platform

A secure, clinician-connected generative AI platform developed for **Anchored Support Services** to improve clinician visibility into patient use of generative AI.

## Project Overview

This full-stack proof of concept provides patients with controlled access to an OpenAI-powered conversation platform while allowing authorized therapists to review relevant patient-AI interactions.

The project focused on engineering the secure application layer surrounding the LLM rather than developing a new AI model.

## Key Features

* Role-based access control for patients, therapists, and administrators
* Secure therapist-patient authorization and backend access isolation
* OpenAI API integration with controlled model access and system instructions
* Patient consent and informed AI disclosure
* Secure conversation storage and conversation history
* Sponsor-managed knowledge base and AI context
* Configurable red-flag monitoring
* Therapist notifications and conversation review
* Administrative user and system management

## Technical Focus

**Full-Stack Development**
**OpenAI API Integration**
**AI Workflow Engineering**
**Role-Based Access Control**
**Secure Data Design**
**UX Design**
**Software Testing**
**Requirements Engineering**

## Architecture

```text
Patient
   |
   v
Secure Application
   |
   +-- Authentication & Authorization
   +-- Consent & Disclosure
   +-- Knowledge Context
   |
   v
OpenAI API
   |
   v
Conversation Storage
   |
   +-- Red-Flag Monitoring
   +-- Notifications
   |
   v
Authorized Therapist
```

## Security & Privacy

The proof of concept uses synthetic patient data and emphasizes backend authorization, least-privilege access, secure API credential handling, conversation privacy, and appropriate data protection practices.

The system is designed as a proof of concept and is not intended to replace therapy, provide diagnoses, or function as an emergency or production clinical system.

## Outcome

Demonstrated how a conventional LLM can be integrated into a secure, governed application environment that makes AI interactions **transparent, controlled, reviewable, and connected to the therapist-patient relationship**.
