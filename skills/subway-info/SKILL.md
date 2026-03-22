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

## Common Pitfalls

Transit data is notoriously tricky. These are real failure modes that catch agents and users regularly.

### Outdated Schedule Data (Cached vs Real-Time)

**The Problem:** Arrival times shown may be cached or stale, especially during heavy traffic or service disruptions.

**Why It Happens:**
- API responses cache at edge servers for 5-10 seconds to handle load
- Client-side polling without fresh server calls returns stale data
- During service disruptions, arrival predictions revert to scheduled times (not real)

**How to Detect & Fix:**
```bash
# Check data freshness timestamp in response
curl -s -X POST https://subwayinfo.nyc/api/arrivals \
  -H "Content-Type: application/json" \
  -d '{"station_id": "127"}' | jq '.data_timestamp'

# If timestamp is >10 seconds old, force fresh fetch (use new API key or IP to bypass cache)
# Or: add ?nocache=true parameter if API supports it
```

**When This Matters:** Real-time trip planning, urgent commutes, tight connections
**Solution:** Always fetch fresh data for time-critical decisions; don't rely on stale responses

### Missing Service Alerts (Planned Work, Delays Not Checked)

**The Problem:** A train arrives in 20 minutes, but there's a planned service change, track work, or delay that the arrivals endpoint didn't surface.

**Why It Happens:**
- `/api/arrivals` shows train predictions but **doesn't include active alerts**
- Planned work (weekends, nights) isn't reflected in real-time predictions
- Delays added mid-journey aren't immediately reflected across all endpoints
- Advisory alerts (e.g., "expect delays") exist but aren't tied to specific arrivals

**How to Detect & Fix:**
```bash
# Always check alerts separately from arrivals
curl -s -X POST https://subwayinfo.nyc/api/alerts \
  -H "Content-Type: application/json" \
  -d '{"line": "1"}' | jq '.[] | select(.type | contains("Planned"))'

# Cross-reference: if planning a trip at 11 PM on Saturday, check alerts first
# Many lines have weekend/night track work that predictions don't catch early
```

**When This Matters:** Weekend trips, night commutes, planned service disruptions
**Solution:** Always fetch alerts *before* planning a trip, not after seeing arrivals

### Wrong Station/Line Identification (Name Confusion, Multiple Stations)

**The Problem:** "Times Square" has 4+ stations; searching gives ambiguous results; agent picks wrong one.

**Why It Happens:**
- Station names aren't unique (e.g., "14 St" exists 6+ times across the system)
- Multiple lines serve the same physical location but with different IDs (42 St-Times Sq is 127, but 42 St-Port Authority is A09)
- Search returns top 5 results but doesn't disambiguate by line or direction
- User says "Grand Central" but means Grand Central Terminal (multiple LIRR/MNR stations exist)

**How to Detect & Fix:**
```bash
# Search returns ambiguous results
curl -s -X POST https://subwayinfo.nyc/api/stations \
  -H "Content-Type: application/json" \
  -d '{"query": "times square"}' | jq '.results[] | {name, id, lines}'

# Output: Multiple results with overlapping names
# Solution: Filter by line before picking station ID
curl -s -X POST https://subwayinfo.nyc/api/stations \
  -H "Content-Type: application/json" \
  -d '{"query": "times square", "line": "1"}' | jq '.results[0].id'
```

**When This Matters:** Multi-line stations, tourist areas, connections between systems
**Solution:** Always filter searches by line if user specifies it; confirm station ID before using it

**Reference Table (Ambiguous Stations):**
| Location | Station Names | Lines | IDs |
|----------|---------------|-------|-----|
| Times Square Area | 42 St-Times Sq, 42 St-Port Authority, 42 St-GCT | 1/2/3 vs A/C/E vs 4/5/6/7 | 127 vs A09 vs 631 |
| 14th Street | 14 St-Union Sq, 14 St-A/C, 14 St-F/M, 14 St-1/2/3, 14 St-L | Multiple | Multiple |
| Penn Station Area | 34 St-Penn, 34 St-Herald Sq, 34 St-GCT | A/C/E vs B/D/F/M vs 1/2/3 | A28 vs B24 vs 307 |

### Time Zone Handling (Schedule vs User Location Time)

**The Problem:** Schedule shows 5:30 PM arrival, but user is in Pacific time and misreads it as local 2:30 PM.

**Why It Happens:**
- MTA schedule data is always in Eastern Time (ET) — API doesn't convert
- User's system clock may be different timezone
- Travel time estimates don't account for timezone differences if trip crosses regions
- Schedule responses don't include timezone info; agent must infer

**How to Detect & Fix:**
```bash
# API returns times in ET (no TZ field)
curl -s -X POST https://subwayinfo.nyc/api/arrivals \
  -H "Content-Type: application/json" \
  -d '{"station_id": "127"}' | jq '.arrivals[0].arrival_time'

# Always convert to user's timezone before displaying
# JavaScript example:
const etTime = new Date(arrivalTime); // Interpreted as ET
const userTz = Intl.DateTimeFormat().resolvedOptions().timeZone;
const userTime = etTime.toLocaleString('en-US', { timeZone: userTz });
```

**When This Matters:** Remote users, cross-country travel planning, scheduling meetings
**Solution:** Always note that times are in Eastern Time; convert to user's local time when displaying

### Weekend/Holiday Schedule Differences (Wrong Assumptions)

**The Problem:** Monday's train schedule is different from Saturday's; predictions assume weekday service but it's actually a holiday.

**Why It Happens:**
- MTA runs different schedules for weekdays, Saturdays, Sundays, and holidays
- Arrival predictions are weekday-based by default; weekend schedules are sparse
- Holiday schedules (Thanksgiving, Christmas, New Year's) are completely different
- Some lines have modified service on nights/weekends that predictions don't reflect clearly

**How to Detect & Fix:**
```javascript
// Check if today is a holiday or weekend
const today = new Date();
const dayOfWeek = today.getDay(); // 0 = Sunday, 6 = Saturday
const holidays = ["2026-01-01", "2026-07-04", "2026-12-25"]; // NYD, July 4, Xmas
const isSpecialDay = dayOfWeek === 0 || dayOfWeek === 6 || holidays.includes(today.toISOString().split('T')[0]);

if (isSpecialDay) {
  console.warn("Running reduced/modified schedule today. Arrivals may not reflect typical service.");
  // Fetch fresh alerts to see if specific lines have changes
}
```

**When This Matters:** Weekend trips, holiday travel, late-night commutes
**Solution:** Check day-of-week and holiday calendar; verify alerts if weekend/holiday

### MTA API Version Drift (Deprecated Endpoints, Breaking Changes)

**The Problem:** Old code uses `/arrivals` endpoint but MTA deprecated it in favor of a new schema that returns different field names.

**Why It Happens:**
- MTA occasionally updates API schemas without backward compatibility
- Field names change (e.g., `arrival_time` → `estimated_arrival_time`)
- Response structure reorganizes (nested vs flat)
- Version mismatches between live API and local documentation

**How to Detect & Fix:**
```bash
# Check API version in response headers
curl -s -i -X POST https://subwayinfo.nyc/api/arrivals \
  -H "Content-Type: application/json" \
  -d '{"station_id": "127"}' | grep -i 'api-version'

# If response structure is unexpected, check API docs at subwayinfo.nyc/docs
# Parse defensively: use `.get()` and provide defaults
const arrival_time = response.arrivals?.[0]?.estimated_arrival_time 
  ?? response.arrivals?.[0]?.arrival_time 
  ?? "Unknown";
```

**When This Matters:** Long-running services, production dashboards, archival code
**Solution:** Monitor API version headers; test after MTA updates; use defensive parsing

### Rate Limit Surprises (Exceeding Quota During Bursts)

**The Problem:** You're on the Free tier (60 req/min), but a popular line gets heavy traffic and you blast 200 requests in 10 seconds checking multiple stations.

**Why It Happens:**
- Rate limits are per-minute buckets; bursts within a minute can exceed quota
- Checking many stations or lines simultaneously exceeds limit quickly
- API returns 429 but doesn't queue requests — they fail immediately
- Error recovery (retry loops) can cascade and exceed limits further

**How to Detect & Fix:**
```bash
# Monitor for 429 responses
curl -s -X POST https://subwayinfo.nyc/api/arrivals \
  -H "Content-Type: application/json" \
  -d '{"station_id": "127"}' \
  -w "\nHTTP Status: %{http_code}\n"

# If 429: Implement exponential backoff
async function fetchWithRetry(url, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    const response = await fetch(url);
    if (response.status !== 429) return response;
    const retryAfter = response.headers.get('Retry-After') || (2 ** i);
    await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
  }
  throw new Error("Rate limited after retries");
}
```

**When This Matters:** Dashboards, multi-station queries, production load spikes
**Solution:** Serialize requests or batch them; monitor rate limit headers; use API key for higher quotas

## Resources

- [Subway Info Website](https://subwayinfo.nyc)
- [API Documentation](https://subwayinfo.nyc/docs)
- [MTA Developer Resources](https://www.mta.info/developers)
