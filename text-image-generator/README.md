# TRDG + Streamlit

Goals:

- Create training data for text recognition tasks
- Use custom / video game fonts
- Minimal human intervention for maximum generation

## Local run:

`docker-compose up`

Runs as root as to add font files.
Volume mount provides `out` directory of images for you.

Use `docker-compose up --build` if dependencies change.

Watchdog might not work on some systems.
Reloading the webpage manually should work.