---
name: subway-info
description: Get real-time NYC subway information including train arrivals, service alerts, station search, and trip planning via the Subway Info API at subwayinfo.nyc.
---

# Subway Info API

## Overview

Real-time NYC subway information via the Subway Info REST API. Get train arrivals, service alerts, station details, and trip planning for all 496 NYC subway stations.

## When to Use

- Checking real-time train arrivals at a station
- Getting current service alerts and delays
- Searching for subway stations by name or line
- Planning trips between subway stations
- Building transit-aware applications
- Commute planning and schedule checking

## Prerequisites

- `curl` for HTTP requests
- `jq` for JSON parsing (`brew install jq` on macOS, `apt install jq` on Linux)
- No API key required for basic usage (10 req/min anonymous tier)

## API Base URL

```
https://subwayinfo.nyc
```

## Rate Limits

| Tier | Requests/Min | Authentication |
|------|--------------|----------------|
| Anonymous | 10 | None (IP-based) |
| Free | 60 | `X-API-Key` header |
| Standard | 300 | `X-API-Key` header |
| Premium | 1000 | `X-API-Key` header |

Rate limit headers are included in all responses:

```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 9
X-RateLimit-Reset: 1704067260
X-RateLimit-Tier: anonymous
```

If you have an API key, include it via header:

```bash
-H "X-API-Key: mta_your_key_here"
```

## Quick Start

Get arrivals at Times Square:

```bash
curl -s -X POST https://subwayinfo.nyc/api/arrivals \
  -H "Content-Type: application/json" \
  -d '{"station_id": "127", "limit": 5}'
```

Search for a station:

```bash
curl -s -X POST https://subwayinfo.nyc/api/stations \
  -H "Content-Type: application/json" \
  -d '{"query": "grand central"}'
```

## Endpoints

All data endpoints use `POST` with JSON body.

### Get Arrivals

Get real-time train arrivals at a station.

```bash
POST /api/arrivals
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `station_id` | string | Yes | Station ID (use search to find) |
| `line` | string | No | Filter by line (e.g., "1", "A", "F") |
| `direction` | "N" \| "S" | No | N=uptown/Bronx, S=downtown/Brooklyn |
| `limit` | number | No | Max arrivals (default: 10) |

**Example:**

```bash
# Arrivals at Times Square, 1 train only, uptown
curl -s -X POST https://subwayinfo.nyc/api/arrivals \
  -H "Content-Type: application/json" \
  -d '{"station_id": "127", "line": "1", "direction": "N", "limit": 5}'
```

**Response includes:** arrival times, line, direction, headsign, minutes until arrival.

### Get Alerts

Get active service alerts.

```bash
POST /api/alerts
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `line` | string | No | Filter by line (e.g., "A", "1") |
| `alert_type` | string | No | Filter by type (e.g., "Delays", "Planned Work") |

**Example:**

```bash
# All alerts for the A train
curl -s -X POST https://subwayinfo.nyc/api/alerts \
  -H "Content-Type: application/json" \
  -d '{"line": "A"}'

# All current alerts
curl -s -X POST https://subwayinfo.nyc/api/alerts \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Search Stations

Find stations by name or line.

```bash
POST /api/stations
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | No | Station name search |
| `line` | string | No | Filter by line |
| `limit` | number | No | Max results (default: 10) |

**Example:**

```bash
# Search by name
curl -s -X POST https://subwayinfo.nyc/api/stations \
  -H "Content-Type: application/json" \
  -d '{"query": "union square"}'

# All stations on the L line
curl -s -X POST https://subwayinfo.nyc/api/stations \
  -H "Content-Type: application/json" \
  -d '{"line": "L", "limit": 50}'
```

**Response includes:** station ID, name, lines served, coordinates.

### Get Station Info

Get detailed information about a specific station.

```bash
POST /api/station
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `station_id` | string | Yes | Station ID |

**Example:**

```bash
curl -s -X POST https://subwayinfo.nyc/api/station \
  -H "Content-Type: application/json" \
  -d '{"station_id": "127"}'
```

**Response includes:** station name, lines, ADA accessibility, coordinates, complex info.

### Plan Trip

Get route suggestions between two stations.

```bash
POST /api/trip
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `origin_station_id` | string | Yes | Starting station ID |
| `destination_station_id` | string | Yes | Destination station ID |

**Example:**

```bash
# Times Square to Grand Central
curl -s -X POST https://subwayinfo.nyc/api/trip \
  -H "Content-Type: application/json" \
  -d '{"origin_station_id": "127", "destination_station_id": "631"}'
```

**Response includes:** route options, transfers, lines used, estimated travel segments.

### Health Check

```bash
GET /health
```

Returns feed freshness and system status. Useful for checking if real-time data is current.

## Common Station IDs

| Station | ID | Lines |
|---------|-----|-------|
| Times Sq-42 St | 127 | 1, 2, 3, 7, N, Q, R, W, S |
| Grand Central-42 St | 631 | 4, 5, 6, 7, S |
| 14 St-Union Sq | L03 | L, 4, 5, 6, N, Q, R, W |
| 34 St-Penn Station | A28 | A, C, E, 1, 2, 3 |
| Fulton St | A38 | A, C, J, Z, 2, 3, 4, 5 |
| Atlantic Av-Barclays Ctr | D24 | B, D, N, Q, R, 2, 3, 4, 5 |
| Jamaica Center | G05 | E, J, Z |

Use `mta_search_stations` or the `/api/stations` endpoint to find any station ID by name.

## Subway Lines

All NYC subway lines are covered:

- **IRT:** 1, 2, 3, 4, 5, 6, 7
- **IND:** A, C, E, B, D, F, M, G
- **BMT:** J, Z, L, N, Q, R, W
- **Shuttles:** S (42nd St, Franklin Ave, Rockaway)
- **Staten Island Railway**

## Helper Scripts

### Get Arrivals

```bash
./scripts/arrivals.sh <station_name_or_id> [line] [direction] [limit]
./scripts/arrivals.sh "times square"
./scripts/arrivals.sh 127 1 N 5
```

### Check Alerts

```bash
./scripts/alerts.sh [line]
./scripts/alerts.sh        # All alerts
./scripts/alerts.sh A      # A train alerts only
```

### Plan a Trip

```bash
./scripts/trip.sh <origin> <destination>
./scripts/trip.sh "times square" "grand central"
./scripts/trip.sh 127 631
```

### Line Status Overview

```bash
./scripts/status.sh [line]
./scripts/status.sh        # All lines
./scripts/status.sh L      # L train only
```

## Common Use Cases

### Check if my train is running on time

```bash
curl -s -X POST https://subwayinfo.nyc/api/alerts \
  -H "Content-Type: application/json" \
  -d '{"line": "L"}' | jq '.content[0].text'
```

### Get next train home

```bash
curl -s -X POST https://subwayinfo.nyc/api/arrivals \
  -H "Content-Type: application/json" \
  -d '{"station_id": "L03", "line": "L", "direction": "S", "limit": 3}' | jq '.content[0].text'
```

### Find a station I don't know the ID for

```bash
curl -s -X POST https://subwayinfo.nyc/api/stations \
  -H "Content-Type: application/json" \
  -d '{"query": "canal street"}' | jq '.content[0].text'
```

## Error Handling

| Status Code | Meaning | Action |
|-------------|---------|--------|
| 400 | Bad Request | Check required parameters |
| 401 | Unauthorized | Invalid API key |
| 429 | Rate Limited | Reduce request frequency or add API key |
| 500 | Server Error | Retry with backoff |

## Best Practices

- **Search first**: Use `/api/stations` to find station IDs before calling arrivals
- **Filter by line**: Narrow arrivals with `line` parameter for cleaner results
- **Check health**: Use `/health` to verify feed freshness before relying on arrival times
- **Cache station IDs**: Station IDs are stable; cache them after first lookup
- **Respect rate limits**: Anonymous tier is 10 req/min. Add an API key for higher limits

## Resources

- [Subway Info Website](https://subwayinfo.nyc)
- [API Documentation](https://subwayinfo.nyc/docs)
- [MTA Developer Resources](https://www.mta.info/developers)
