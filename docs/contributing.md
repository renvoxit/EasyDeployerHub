# Contributing

Thank you for taking the time to improve EasyDeployerHub.

Contributions are welcome when they improve clarity, correctness, reliability,
or developer experience.

## Scope

EasyDeployerHub is a backend-first deployment platform MVP. The goal is to
demonstrate a clear, inspectable deployment pipeline: repository access,
project analysis, template rendering, Docker build and runtime orchestration,
status tracking, logs, and local routing.

The current scope is local development and deployment workflow experimentation.
Large product changes are easier to review when they are discussed first.

## Good Contribution Areas

Useful contributions include:

- documentation improvements;
- focused bug fixes;
- additional tests for deployment lifecycle behavior;
- analyzer fixtures and project detection cases;
- clearer API examples;
- Docker and Traefik local development notes;
- small reliability improvements with tests.

Please open an issue before starting work that changes orchestration flow,
database models, authentication, Docker execution, routing behavior, or public
API contracts. That keeps larger changes easy to coordinate.

## Development Expectations

Keep changes small and reviewable. A pull request should normally address one
problem, include the reasoning behind the change, and update documentation when
behavior changes.

Before opening a pull request:

1. Run the relevant tests.
2. Check that deployment-related behavior is still deterministic.
3. Avoid mixing formatting-only changes with functional changes.
4. Include screenshots or command output when the change affects local usage.
5. Note any follow-up work that is intentionally left out of scope.

## Code Style

Follow the existing structure and naming conventions. Prefer clear service
boundaries over broad utility modules, and keep orchestration logic easy to
trace from the API layer through the deployment stages.

New behavior should be covered by tests when it changes deployment state,
error handling, persistence, security assumptions, or API responses.

## Licensing

By submitting a contribution, you agree that the contribution may be included
in this repository under the project's license. If you plan to use the project
beyond local learning, evaluation, or contribution, please check the license
first or contact the maintainer.

## Review

Maintainers may ask for changes or suggest a smaller scope for a pull request.
The aim is to keep the codebase understandable, testable, and useful for the
deployment platform MVP.
