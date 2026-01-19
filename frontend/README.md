# Frontend

This directory contains the frontend application for the deployment platform.

## Purpose

The frontend provides a user interface to:
- authenticate via GitHub
- view repositories
- trigger deployments
- monitor deployment status and logs
- manage deployed projects

It communicates exclusively with the backend API.

## Tech Stack

- Vite
- React
- JavaScript
- CSS

## Project Structure

- `src/pages/`  
  Application pages (Login, Dashboard, Projects, Logs).

- `src/components/`  
  Reusable UI components (buttons, lists, cards, log viewer).

- `src/api.js`  
  Backend API interaction layer.

- `src/main.jsx`  
  Frontend application entry point.

- `vite.config.js`  
  Frontend build and dev server configuration.

## Development

Local development is handled via Vite dev server.

The frontend expects the backend API to be available
(either locally or via proxy configuration).

## Responsibilities

Frontend:
- handles UI and user interaction
- displays backend data
- sends commands to backend API

Backend:
- handles authentication
- performs deployments
- manages state and infrastructure

Frontend does NOT:
- perform deployments
- access infrastructure directly
- store secrets

## Notes

The frontend is a consumer of the backend API.
It contains no business logic related to deployment execution.
