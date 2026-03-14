---
name: subway-info
description: Get real-time NYC transit information — subway, bus, ferry, and commuter rail — via the subway-info CLI or REST API at subwayinfo.nyc.
---

# Subway Info

## Overview

Real-time NYC transit information covering subway, bus, ferry, and commuter rail (LIRR/Metro-North). Covers all 496 subway stations, 16,000+ bus stops, NYC Ferry landings, and LIRR/Metro-North stations.

## When to Use

- Checking real-time train arrivals at a station
- Getting current service alerts and delays
- Searching for subway stations by name or line
- Planning trips between subway stations
- Checking bus arrivals and routes
- NYC Ferry schedules and alerts
- LIRR and Metro-North departures
- Commute planning and schedule checking

## CLI Tool (Preferred)

If `subway-info` CLI is available, prefer it over raw curl — it handles retries, auth, and outputs token-efficient text by default.

### Install

```bash
# From the mta-mcp repo
npm run build:cli
# Binary at ./dist/subway-info

# Or run directly
npm run cli -- arrivals --station 127
```

### Subway Commands

```bash
subway-info arrivals --station 127 --line 1 --direction N --limit 5
subway-info alerts --line A
subway-info stations --query "times square"
subway-info trip --from 127 --to 631
subway-info status --line L
```

### Bus Commands

```bash
subway-info bus arrivals --stop 402940 --route M1
subway-info bus alerts --route M1
subway-info bus stops --query "5th ave" --borough Manhattan
subway-info bus route --route M1
```

### Ferry Commands

```bash
subway-info ferry arrivals --landing <id>
subway-info ferry alerts
subway-info ferry landings --query "wall street"
subway-info ferry routes
```

### Rail Commands (LIRR / Metro-North)

```bash
subway-info rail departures --station <id> --system LIRR
subway-info rail alerts --system MNR
subway-info rail stations --query "penn" --system LIRR
subway-info rail station --station <id>
```

### Global Options

```
--json          Print raw JSON instead of compact text
--api-key <key> Override $SUBWAY_INFO_API_KEY
--base-url <url> Override https://subwayinfo.nyc
```

## REST API

All data endpoints use `POST` with JSON body. Base URL: `https://subwayinfo.nyc`

### Rate Limits

| Tier | Requests/Min | Authentication |
|------|--------------|----------------|
| Anonymous | 10 | None (IP-based) |
| Free | 60 | `X-API-Key` header |
| Standard | 300 | `X-API-Key` header |
| Premium | 1000 | `X-API-Key` header |

### Subway Endpoints

#### Get Arrivals

```bash
curl -s -X POST https://subwayinfo.nyc/api/arrivals \
  -H "Content-Type: application/json" \
  -d '{"station_id": "127", "line": "1", "direction": "N", "limit": 5}'
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `station_id` | string | Yes | Station ID (use search to find) |
| `line` | string | No | Filter by line (e.g., "1", "A", "F") |
| `direction` | "N" \| "S" | No | N=uptown/Bronx, S=downtown/Brooklyn |
| `limit` | number | No | Max arrivals (default: 10) |

#### Get Alerts

```bash
curl -s -X POST https://subwayinfo.nyc/api/alerts \
  -H "Content-Type: application/json" \
  -d '{"line": "A"}'
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `line` | string | No | Filter by line |
| `alert_type` | string | No | Filter by type (e.g., "Delays", "Planned Work") |

#### Search Stations

```bash
curl -s -X POST https://subwayinfo.nyc/api/stations \
  -H "Content-Type: application/json" \
  -d '{"query": "union square"}'
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | No | Station name search |
| `line` | string | No | Filter by line |
| `limit` | number | No | Max results (default: 10) |

#### Get Station Info

```bash
curl -s -X POST https://subwayinfo.nyc/api/station \
  -H "Content-Type: application/json" \
  -d '{"station_id": "127"}'
```

#### Plan Trip

```bash
curl -s -X POST https://subwayinfo.nyc/api/trip \
  -H "Content-Type: application/json" \
  -d '{"origin_station_id": "127", "destination_station_id": "631"}'
```

### Bus Endpoints

```bash
POST /api/bus/arrivals   {"stop_id": "402940", "route": "M1", "limit": 5}
POST /api/bus/alerts     {"route": "M1"}
POST /api/bus/stops      {"query": "5th ave", "borough": "Manhattan"}
POST /api/bus/route      {"route_id": "M1"}
```

### Ferry Endpoints

```bash
POST /api/ferry/arrivals  {"landing_id": "<id>", "route": "<route>"}
POST /api/ferry/alerts    {"route": "<route>"}
POST /api/ferry/landings  {"query": "wall street"}
POST /api/ferry/routes    {}
```

### Rail Endpoints (LIRR / Metro-North)

```bash
POST /api/rail/departures {"station_id": "<id>", "system": "LIRR"}
POST /api/rail/alerts     {"system": "MNR", "branch": "Hudson"}
POST /api/rail/stations   {"query": "penn", "system": "LIRR"}
POST /api/rail/station    {"station_id": "<id>"}
```

### Health Check

```bash
GET /health
```

## Common Station IDs

| Station | ID | Lines |
|---------|-----|-------|
| Times Sq-42 St | 127 | 1, 2, 3, 7, N, Q, R, W, S |
| Grand Central-42 St | 631 | 4, 5, 6, 7, S |
| 14 St-Union Sq | L03 | L, 4, 5, 6, N, Q, R, W |
| 34 St-Penn Station | A28 | A, C, E, 1, 2, 3 |
| Fulton St | A38 | A, C, J, Z, 2, 3, 4, 5 |
| Atlantic Av-Barclays Ctr | D24 | B, D, N, Q, R, 2, 3, 4, 5 |

Use `subway-info stations --query "..."` or `/api/stations` to find any station ID.

## Helper Scripts

```bash
./scripts/arrivals.sh "times square"          # Search by name
./scripts/arrivals.sh 127 1 N 5              # By ID with filters
./scripts/alerts.sh A                         # A train alerts
./scripts/trip.sh "times square" "grand central"
./scripts/status.sh L                         # L train status
```

## Error Handling

| Status Code | Meaning | Action |
|-------------|---------|--------|
| 400 | Bad Request | Check required parameters |
| 401 | Unauthorized | Invalid API key |
| 429 | Rate Limited | Reduce request frequency or add API key |
| 500 | Server Error | Retry with backoff |

## Best Practices

- **Use CLI when available** — handles retries, auth, and compact output automatically
- **Search first**: Find station IDs before calling arrivals
- **Filter by line**: Narrow arrivals with `line` parameter for cleaner results
- **Cache station IDs**: Station IDs are stable; cache them after first lookup
- **Respect rate limits**: Anonymous tier is 10 req/min; set `SUBWAY_INFO_API_KEY` for higher limits

## Resources

- [Subway Info Website](https://subwayinfo.nyc)
- [API Documentation](https://subwayinfo.nyc/docs)
- [MTA Developer Resources](https://www.mta.info/developers)
