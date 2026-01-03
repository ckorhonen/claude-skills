---
description: Create a conductor.json file with appropriate scripts for this project
allowed-tools: Read, Write, Bash(cat:*), Bash(ls:*)
---

# Install Conductor

Generate a `conductor.json` file for this project based on detected project type and configuration.

## Project Detection

### Package Manager Detection
- package-lock.json: !`ls package-lock.json 2>/dev/null && echo "npm detected"`
- yarn.lock: !`ls yarn.lock 2>/dev/null && echo "yarn detected"`
- bun.lockb: !`ls bun.lockb 2>/dev/null && echo "bun detected"`
- pnpm-lock.yaml: !`ls pnpm-lock.yaml 2>/dev/null && echo "pnpm detected"`

### Project Type Detection
- package.json: !`cat package.json 2>/dev/null | head -50`
- pyproject.toml: !`cat pyproject.toml 2>/dev/null | head -30`
- requirements.txt: !`ls requirements.txt 2>/dev/null && echo "Python pip project"`
- go.mod: !`cat go.mod 2>/dev/null | head -10`
- Cargo.toml: !`cat Cargo.toml 2>/dev/null | head -20`

### Environment Files
- .env.example: !`ls .env.example .env.sample .env.template 2>/dev/null | head -1`

### Existing conductor.json
!`cat conductor.json 2>/dev/null && echo "--- conductor.json already exists ---"`

## Instructions

Based on the detection above, create a `conductor.json` file in the project root.

### conductor.json Format

```json
{
  "scripts": {
    "setup": "commands to install dependencies and set up environment",
    "run": "command to start the dev server or main process",
    "runScriptMode": "nonconcurrent"
  }
}
```

### Script Guidelines

**Setup Script** - Runs when workspace is created:
1. Install dependencies using the detected package manager
2. If .env.example exists, copy it: `cp .env.example .env`
3. Chain commands with `;` (e.g., `npm install; cp .env.example .env`)

**Run Script** - Triggered by the "Run" button:
1. For web servers, use `$CONDUCTOR_PORT` environment variable
2. Look at available scripts in package.json (dev, start, serve)
3. Prefer dev/development scripts over production scripts

**runScriptMode** - Set to `"nonconcurrent"` for dev servers (kills previous before starting new)

### Framework-Specific Port Flags

| Framework | Run Command |
|-----------|-------------|
| Next.js | `npm run dev -- -p $CONDUCTOR_PORT` |
| Vite | `npm run dev -- --port $CONDUCTOR_PORT` |
| Create React App | `PORT=$CONDUCTOR_PORT npm start` |
| Express | Assumes app reads `process.env.PORT` or `$CONDUCTOR_PORT` |
| Python Flask | `flask run --port $CONDUCTOR_PORT` |
| Python FastAPI | `uvicorn main:app --port $CONDUCTOR_PORT` |
| Go | `go run . --port $CONDUCTOR_PORT` or set env |

### Heuristics by Package Manager

| Detection | Setup | Run |
|-----------|-------|-----|
| npm (package-lock.json) | `npm install` | `npm run dev` or `npm start` |
| yarn (yarn.lock) | `yarn install` | `yarn dev` or `yarn start` |
| bun (bun.lockb) | `bun install` | `bun run dev` or `bun start` |
| pnpm (pnpm-lock.yaml) | `pnpm install` | `pnpm dev` or `pnpm start` |
| Python (pyproject.toml) | `pip install -e .` | Check for scripts |
| Python (requirements.txt) | `pip install -r requirements.txt` | `python main.py` or `python app.py` |
| Go (go.mod) | `go mod download` | `go run .` |
| Rust (Cargo.toml) | `cargo build` | `cargo run` |

### Steps

1. Analyze the project detection output above
2. Determine the appropriate setup command
3. Determine the appropriate run command (with $CONDUCTOR_PORT if applicable)
4. If conductor.json already exists, show it and ask if the user wants to overwrite
5. Write the conductor.json file to the project root

### Output

Write the file and confirm:
```
Created conductor.json:
{
  "scripts": {
    "setup": "...",
    "run": "...",
    "runScriptMode": "nonconcurrent"
  }
}
```
