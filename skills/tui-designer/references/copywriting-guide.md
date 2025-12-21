# Copywriting Guide for Retro/Cyberpunk TUI

Default voice, tone, and language patterns for terminal-style interfaces. Use these conventions unless the project specifies otherwise.

## Core Voice Principles

### 1. Terse and Direct
Terminal interfaces value efficiency. Every word must earn its place.

| Instead of | Write |
|------------|-------|
| "Please wait while we process your request" | "PROCESSING..." |
| "An error has occurred" | "ERROR" |
| "Successfully completed" | "COMPLETE" |
| "Are you sure you want to delete this?" | "CONFIRM DELETE? [Y/N]" |

### 2. Technical Authority
Speak with confidence. The system knows what it's doing.

| Weak | Strong |
|------|--------|
| "We think there might be a problem" | "ANOMALY DETECTED" |
| "Something went wrong" | "OPERATION FAILED: ERR_0x4F2" |
| "Please try again later" | "RETRY IN 30s" |

### 3. Mechanical Precision
Machines don't hedge, apologize, or use filler words.

**Avoid:**
- "Please", "Sorry", "Oops"
- "Just", "Maybe", "Might"
- Exclamation points (except for CRITICAL alerts)
- Emoji (unless specifically requested)

**Use:**
- Imperatives: "ENTER", "SELECT", "CONFIRM"
- Status words: "ACTIVE", "IDLE", "PENDING"
- Technical terms: "INITIALIZE", "EXECUTE", "TERMINATE"

---

## Text Formatting

### Case Conventions

| Element | Case | Example |
|---------|------|---------|
| Headers/Titles | UPPERCASE | `SYSTEM STATUS` |
| Labels | UPPERCASE | `CPU USAGE:` |
| Status indicators | UPPERCASE | `ONLINE`, `OFFLINE` |
| Commands | lowercase | `> run diagnostic` |
| Body text | Sentence case | `Connection established` |
| User input prompts | lowercase | `enter password:` |
| File paths | lowercase | `/var/log/system.log` |

### Prefixes and Tags

Use bracketed prefixes for message categorization:

```
[SYS] System message
[USR] User action/input
[ERR] Error message
[WRN] Warning
[INF] Information
[DBG] Debug output
[NET] Network activity
[SEC] Security event
```

### Timestamps

```
14:23:01       # 24-hour, no date
2024-12-20     # ISO date
1703084581     # Unix timestamp (for logs)
+00:42:17      # Elapsed time
T-00:05:00     # Countdown
```

---

## Message Patterns

### System Messages

```
> INITIALIZING SYSTEM...
> LOADING CORE MODULES [████████░░] 80%
> ESTABLISHING SECURE CONNECTION...
> AUTHENTICATION COMPLETE
> SYSTEM READY
```

```
[SYS] Boot sequence initiated
[SYS] Memory check: 16384MB OK
[SYS] Network adapter: CONNECTED
[SYS] All systems nominal
```

### Status Updates

```
STATUS: OPERATIONAL
UPTIME: 47d 12h 34m 08s
LOAD: 0.42 | 0.38 | 0.31
MEMORY: 2.1GB / 8.0GB (26%)
```

### Progress Indicators

```
DOWNLOADING... 45%
[████████████░░░░░░░░░░░░] 52%
TRANSFER: 142MB/s | ETA: 00:03:24
PROCESSING RECORDS: 1,247 of 5,000
```

### User Prompts

```
> _
> enter command:
PASSWORD: ********
CONFIRM [Y/N]:
SELECT OPTION [1-5]:
```

### Success Messages

```
OPERATION COMPLETE
TRANSFER SUCCESSFUL
CHANGES SAVED
CONNECTION ESTABLISHED
AUTHENTICATION VERIFIED
```

### Error Messages

```
ERROR: ACCESS DENIED
ERR_CONNECTION_REFUSED
FATAL: KERNEL PANIC
INVALID INPUT: Expected integer
TIMEOUT: No response from server
```

Format: `ERROR_TYPE: Brief description`

Include error codes when available:
```
ERROR 0x4F2: Memory allocation failed
ERR_NET_001: Connection timeout after 30s
```

### Warning Messages

```
WARNING: Low disk space (< 10%)
CAUTION: Unsaved changes will be lost
ALERT: Unusual activity detected
NOTICE: Maintenance scheduled for 02:00
```

---

## Vocabulary

### Action Verbs

| Action | Terminal Verb |
|--------|--------------|
| Start | INITIALIZE, BOOT, LAUNCH, ACTIVATE |
| Stop | TERMINATE, HALT, ABORT, KILL |
| Save | WRITE, COMMIT, STORE, PERSIST |
| Load | READ, FETCH, RETRIEVE, LOAD |
| Delete | PURGE, REMOVE, CLEAR, WIPE |
| Search | SCAN, QUERY, LOCATE, FIND |
| Connect | LINK, SYNC, HANDSHAKE, ESTABLISH |
| Disconnect | SEVER, DROP, RELEASE, CLOSE |
| Send | TRANSMIT, PUSH, DISPATCH, RELAY |
| Receive | ACQUIRE, PULL, INTERCEPT, CAPTURE |
| Update | PATCH, REFRESH, SYNC, UPGRADE |
| Verify | VALIDATE, CHECK, CONFIRM, AUTHENTICATE |

### Status Words

| State | Terminal Word |
|-------|--------------|
| Working | PROCESSING, EXECUTING, RUNNING, ACTIVE |
| Waiting | PENDING, STANDBY, IDLE, QUEUED |
| Done | COMPLETE, FINISHED, DONE, SUCCESS |
| Failed | FAILED, ERROR, FAULT, ABORTED |
| Ready | READY, ONLINE, AVAILABLE, ARMED |
| Not ready | OFFLINE, UNAVAILABLE, DISABLED, DOWN |

### Technical Nouns

```
SYSTEM      MODULE      PROTOCOL    BUFFER
PROCESS     DAEMON      INTERFACE   CACHE
THREAD      SERVICE     SOCKET      STREAM
QUEUE       HANDLER     ENDPOINT    PAYLOAD
STACK       REGISTRY    CHANNEL     PACKET
NODE        CLUSTER     INSTANCE    SESSION
```

---

## Tone Variations

### Standard (Neutral)
Default for most interfaces. Professional, efficient.

```
SYSTEM INITIALIZED
USER AUTHENTICATED
OPERATION COMPLETE
```

### Cyberpunk (Dramatic)
For immersive, narrative-driven interfaces.

```
NEURAL LINK ESTABLISHED
FIREWALL BREACH DETECTED
ICE COUNTERMEASURES ACTIVE
JACKING IN...
```

### Military (Formal)
High-security, mission-critical systems.

```
AUTHORIZATION REQUIRED
CLEARANCE LEVEL: ALPHA
MISSION STATUS: GREEN
ENGAGE PROTOCOL DELTA-7
```

### Hacker (Underground)
Rebellious, counter-culture aesthetic.

```
owned.
access granted, meatbag
we're in
root acquired. game over.
```

### Retro Computing (Nostalgic)
1980s personal computer vibes.

```
READY.
?SYNTAX ERROR IN LINE 20
PRESS ANY KEY TO CONTINUE
LOAD "*",8,1
```

---

## Common Phrases

### Boot/Startup
```
BOOTING...
INITIALIZING SUBSYSTEMS
PERFORMING SELF-DIAGNOSTICS
LOADING CONFIGURATION
MOUNTING FILESYSTEMS
STARTING SERVICES
BOOT SEQUENCE COMPLETE
SYSTEM READY
```

### Authentication
```
ENTER CREDENTIALS
VERIFYING IDENTITY
ACCESS GRANTED
ACCESS DENIED
AUTHENTICATION FAILED
SESSION EXPIRED
BIOMETRIC SCAN REQUIRED
TWO-FACTOR REQUIRED
```

### Network
```
ESTABLISHING CONNECTION
HANDSHAKE COMPLETE
SIGNAL STRENGTH: STRONG
LATENCY: 24ms
PACKET LOSS: 0.2%
CONNECTION LOST
RECONNECTING...
```

### Errors
```
OPERATION FAILED
UNKNOWN ERROR
SEGMENTATION FAULT
STACK OVERFLOW
OUT OF MEMORY
FILE NOT FOUND
PERMISSION DENIED
CHECKSUM MISMATCH
```

### Shutdown
```
INITIATING SHUTDOWN
SAVING STATE
TERMINATING PROCESSES
CLOSING CONNECTIONS
FLUSHING BUFFERS
SHUTDOWN COMPLETE
POWER OFF
```

---

## Formatting Patterns

### Lists and Menus

```
┌─ MAIN MENU ─────────────┐
│ [1] NEW GAME            │
│ [2] LOAD GAME           │
│ [3] OPTIONS             │
│ [4] CREDITS             │
│ [Q] QUIT                │
└─────────────────────────┘
```

### Key-Value Pairs

```
NAME:     System Monitor
VERSION:  2.1.0
STATUS:   ACTIVE
UPTIME:   47d 12h
```

### Tables

```
ID     NAME        STATUS    CPU
─────────────────────────────────
001    nginx       RUNNING   2.3%
002    postgres    RUNNING   8.1%
003    redis       STOPPED   0.0%
```

### Hierarchical Data

```
/system
├── /core
│   ├── kernel.bin
│   └── drivers/
├── /config
│   └── settings.cfg
└── /logs
    └── system.log
```

---

## Dialog and Confirmation

### Confirmation Prompts

```
DELETE FILE? [Y/N]
CONFIRM OVERWRITE [Y/N]:
PROCEED WITH FORMAT? THIS CANNOT BE UNDONE [Y/N]
```

### Multi-Option Prompts

```
SELECT ACTION:
  [C]ONTINUE
  [R]ETRY
  [A]BORT

CHOOSE DIFFICULTY: [E]ASY [N]ORMAL [H]ARD
```

### Input Validation

```
INVALID INPUT
EXPECTED: INTEGER
RECEIVED: "abc"

INPUT OUT OF RANGE [1-100]
FIELD REQUIRED: USERNAME
```

---

## Numbers and Units

### Formatting

```
1,247,893       # Thousands separator
16,384 MB       # Space before unit
99.7%           # Percentage
0x4F2A          # Hex prefix
192.168.1.1     # IP addresses
```

### Common Units

```
MEMORY:   MB, GB, TB
SPEED:    MB/s, Gbps, Hz
TIME:     ms, s, m, h, d
TEMP:     C, F (no degree symbol)
POWER:    W, mA, V
```

### Time Durations

```
00:05:23        # MM:SS or HH:MM:SS
5h 23m 17s      # Abbreviated
5.4 hours       # Decimal
```

---

## Accessibility Notes

### Screen Reader Considerations

- Avoid excessive abbreviations in critical messages
- Spell out important status changes
- Use consistent patterns for similar messages
- Provide text alternatives for ASCII art

### Cognitive Load

- Keep messages under 80 characters when possible
- One concept per message
- Use consistent terminology throughout
- Place most important information first

---

## Examples by Context

### Login Screen
```
╔══════════════════════════════════╗
║         SYSTEM ACCESS            ║
╠══════════════════════════════════╣
║                                  ║
║  USERNAME: _                     ║
║  PASSWORD:                       ║
║                                  ║
║  [ENTER] TO AUTHENTICATE         ║
║                                  ║
╚══════════════════════════════════╝
```

### Dashboard
```
┌─ SYSTEM STATUS ─────────────────────────┐
│                                         │
│  STATUS:  ● OPERATIONAL                 │
│  UPTIME:  47d 12h 34m                   │
│  LOAD:    0.42 | 0.38 | 0.31            │
│                                         │
│  [CPU]  ████████░░░░░░░░  45%           │
│  [MEM]  ██████████░░░░░░  62%           │
│  [DSK]  ████░░░░░░░░░░░░  23%           │
│                                         │
└─────────────────────────────────────────┘
```

### Error Dialog
```
╔════════════════════════════════════════╗
║  ⚠ ERROR                               ║
╠════════════════════════════════════════╣
║                                        ║
║  CONNECTION FAILED                     ║
║                                        ║
║  CODE: ERR_NET_TIMEOUT                 ║
║  HOST: api.example.com                 ║
║  REASON: No response after 30s         ║
║                                        ║
║  [R]ETRY    [C]ANCEL    [D]ETAILS      ║
║                                        ║
╚════════════════════════════════════════╝
```

### Command Line
```
user@system:~$ scan network
[INF] Scanning 192.168.1.0/24...
[INF] Found 12 hosts
[INF] Identifying services...

HOST            SERVICES
───────────────────────────────
192.168.1.1     SSH, HTTP
192.168.1.10    HTTP, HTTPS
192.168.1.42    SSH, MYSQL

SCAN COMPLETE: 12 hosts, 8 services
user@system:~$ _
```
