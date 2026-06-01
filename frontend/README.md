# Frontend

The frontend is the user interface for EasyDeployerHub. It is responsible for
authentication screens, repository selection, deployment actions, deployment
status, and log viewing.

The deployment workflow itself remains in the backend. The frontend should stay
thin: it calls backend APIs, renders state, and provides clear controls for the
user.

## Stack

- Vite
- React
- JavaScript
- CSS

## Structure

- `src/pages/` - route-level application screens.
- `src/components/` - reusable UI building blocks.
- `src/api.js` - backend API client.
- `src/main.jsx` - application entry point.
- `vite.config.js` - Vite configuration.

## Responsibilities

The frontend may:

- start deployment requests through the backend API;
- show repositories available through GitHub integration;
- display deployment status, logs, diagnostics, and lifecycle actions;
- provide a predictable dashboard for local deployment work.

The frontend must not:

- execute deployment steps directly;
- access Docker, Traefik, or host infrastructure;
- store secrets in browser code;
- duplicate backend orchestration rules.

## Local Development

Run the frontend with the Vite dev server and point it at a running backend API.
Backend behavior, authentication, deployment execution, and persistence should
be verified in the backend test suite.
