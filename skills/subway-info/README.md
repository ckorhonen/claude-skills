# subway-info

Claude Code skill for real-time NYC subway information via [subwayinfo.nyc](https://subwayinfo.nyc).

## What It Does

Provides Claude with knowledge of the Subway Info REST API to answer transit queries: train arrivals, service alerts, station search, and trip planning for all 496 NYC subway stations.

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
