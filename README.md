# Task Manager

A simple app for creating tasks and keeping track of what needs to get done.

## Overview

Use this project to organize tasks, update their progress, and keep your work in one place.

## Getting Started

1. Clone this repository.
2. Install the project dependencies using the package manager configured for the project.
3. Start the app using the development command defined in the project configuration.

The exact install and run commands depend on the language and framework used by this project.

### Docker Compose

Compose reads its settings from the root `.env` file. For a new checkout, copy
`.env.example` to `.env` and replace both placeholders with independently
generated secrets, for example using `openssl rand -hex 32`. Keep the file
private and never commit it. The PostgreSQL user, password, and database name
must use URL-safe characters because they are included in the database URL.

Start the services with `docker compose up --build`; the API listens on the
host port specified by `API_PORT` (8000 by default). PostgreSQL credentials are
initialized only when the `pgdata` volume is first created. Changing them in
`.env` later does not change an existing database; update the database
credentials separately or use a new volume.

## Usage

Add a task with a clear title, then update or remove it as your work changes. If supported by the app, use task details, due dates, priorities, or status to organize your list.

## Development

Run the project's configured test and lint commands before submitting changes. See the project configuration for available scripts.
