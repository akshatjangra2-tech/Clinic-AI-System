# AI Healthcare Assistant for Clinics & Hospitals

An AI-powered healthcare assistant built for hospital and clinic websites to automate patient communication, answer common hospital queries, and handle appointment booking.

## Features

- AI chatbot for hospital queries
- RAG-based knowledge retrieval
- Appointment booking workflow
- Doctor selection flow
- Consultation fee response handling
- Emergency / NICU / location query support
- Google Sheets integration for appointment logging
- Admin panel for chat visibility
- Deployed on VPS using FastAPI

## Tech Stack

- Python
- FastAPI
- JavaScript
- HTML / CSS
- Retrieval-Augmented Generation (RAG)
- Google Apps Script
- Google Sheets
- VPS Deployment

## Problem Solved

Hospitals and clinics often lose patient leads because:
- receptionists are unavailable 24/7
- repetitive patient queries consume staff time
- appointments are not captured efficiently
- website visitors drop off without converting

This system solves that by acting as an AI receptionist.

## Key Functionalities

### 1. AI Query Handling
Answers patient questions like:
- consultation fees
- hospital location
- NICU availability
- emergency support
- doctor-related queries

### 2. Appointment Booking
Collects:
- patient name
- phone number
- doctor
- appointment date
- time
- issue / concern

Then stores the booking automatically.

### 3. CRM Logging
Pushes appointment data into Google Sheets for easy management and tracking.

### 4. Rule + RAG Hybrid Architecture
Uses:
- rule-based responses for critical and fixed information
- RAG for hospital knowledge retrieval
- controlled response logic to reduce hallucinations

## Architecture

User → Website Chatbot → FastAPI Backend → RAG / Rules Engine → Google Sheets Booking Log

## Deployment

Deployed on VPS with FastAPI and Uvicorn.

## Why This Project Is Strong

This is not just a chatbot UI.

It is a real-world healthcare automation system combining:
- backend APIs
- retrieval system design
- stateful chatbot logic
- workflow automation
- deployment
- admin visibility

## Use Cases

- Hospitals
- Clinics
- Gynecology centers
- Dental clinics
- Skin clinics
- Multi-speciality centers

## Future Scope

- WhatsApp integration
- doctor slot availability engine
- payment collection
- admin analytics dashboard
- multilingual patient interaction

## Author

Built as an end-to-end AI healthcare workflow system for real-world deployment and business use.
