# subway-info

Claude Code skill for real-time NYC transit information via [subwayinfo.nyc](https://subwayinfo.nyc).

## What It Does

Provides Claude with knowledge of the Subway Info CLI and REST API to answer transit queries: subway arrivals, bus stops, ferry landings, commuter rail departures, service alerts, station search, and trip planning across all NYC transit modes.

## Install

```bash
# Via skills.sh
curl -s https://skills.sh/subway-info | bash

# Manual (project-level)
cp -r skills/subway-info /path/to/project/.claude/skills/

# Manual (user-level)
cp -r skills/subway-info ~/.claude/skills/
```

## Helper Scripts

| Script | Description | Usage |
|--------|-------------|-------|
| `arrivals.sh` | Real-time arrivals at a station | `./scripts/arrivals.sh "times square"` |
| `alerts.sh` | Active service alerts | `./scripts/alerts.sh A` |
| `trip.sh` | Plan a trip between stations | `./scripts/trip.sh "union square" "grand central"` |
| `status.sh` | Line status overview | `./scripts/status.sh L` |

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `SUBWAY_API_URL` | API base URL | `https://subwayinfo.nyc` |
| `SUBWAY_API_KEY` | API key for higher rate limits | None (anonymous: 10 req/min) |

## Requirements

- `curl`
- `jq` (`brew install jq`)
