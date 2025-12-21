/**
 * Tuimorphic React Starter Template
 *
 * A complete React application demonstrating Tuimorphic components
 * with retro terminal aesthetics.
 *
 * Setup:
 *   npm install tuimorphic
 *   npm install react react-dom
 */

import React, { useState, useEffect } from 'react';
import {
  Button,
  Card,
  Input,
  TextArea,
  Checkbox,
  Toggle,
  Select,
  SelectOption,
  Alert,
  Badge,
  Progress,
  Tabs,
  TabList,
  Tab,
  TabPanel,
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogFooter,
  Menu,
  MenuTrigger,
  MenuContent,
  MenuItem,
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableCell,
  CodeBlock,
  Text,
  Heading,
  Divider,
  BarLoader,
} from 'tuimorphic';
import 'tuimorphic/styles.css';

// ============================================
// Custom Styles for Enhanced Effects
// ============================================

const customStyles = `
  /* Neon text glow */
  .neon-text {
    text-shadow:
      0 0 5px currentColor,
      0 0 10px currentColor,
      0 0 20px currentColor;
  }

  /* Scanlines overlay */
  .scanlines {
    position: relative;
  }

  .scanlines::after {
    content: '';
    position: absolute;
    inset: 0;
    background: repeating-linear-gradient(
      0deg,
      rgba(0, 0, 0, 0.1),
      rgba(0, 0, 0, 0.1) 1px,
      transparent 1px,
      transparent 2px
    );
    pointer-events: none;
    z-index: 100;
  }

  /* Flicker animation */
  @keyframes flicker {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.98; }
    52% { opacity: 1; }
    54% { opacity: 0.96; }
  }

  .flicker {
    animation: flicker 3s infinite;
  }

  /* Cursor blink */
  @keyframes cursor-blink {
    0%, 49% { opacity: 1; }
    50%, 100% { opacity: 0; }
  }

  .cursor::after {
    content: '_';
    animation: cursor-blink 1s step-end infinite;
  }

  /* Container styling */
  .terminal-container {
    min-height: 100vh;
    padding: 20px;
  }

  .terminal-header {
    text-transform: uppercase;
    letter-spacing: 0.1em;
  }
`;

// ============================================
// Types
// ============================================

interface SystemStatus {
  cpu: number;
  memory: number;
  disk: number;
  network: string;
}

interface LogEntry {
  timestamp: string;
  level: 'info' | 'warning' | 'error';
  message: string;
}

// ============================================
// Components
// ============================================

// Status Dashboard Card
const StatusCard: React.FC<{
  label: string;
  value: number | string;
  unit?: string;
}> = ({ label, value, unit }) => (
  <Card>
    <Text variant="muted" className="terminal-header">
      {label}
    </Text>
    <Heading level={2}>
      {value}
      {unit && <span style={{ fontSize: '0.5em' }}>{unit}</span>}
    </Heading>
    {typeof value === 'number' && <Progress value={value} max={100} />}
  </Card>
);

// Log Viewer
const LogViewer: React.FC<{ logs: LogEntry[] }> = ({ logs }) => (
  <Card>
    <Heading level={3} className="terminal-header">
      SYSTEM LOGS
    </Heading>
    <Divider />
    <div style={{ maxHeight: '200px', overflow: 'auto' }}>
      {logs.map((log, i) => (
        <div key={i} style={{ fontFamily: 'monospace', fontSize: '12px' }}>
          <Text variant="muted">[{log.timestamp}]</Text>{' '}
          <Badge
            variant={
              log.level === 'error'
                ? 'destructive'
                : log.level === 'warning'
                  ? 'warning'
                  : 'default'
            }
          >
            {log.level.toUpperCase()}
          </Badge>{' '}
          <Text>{log.message}</Text>
        </div>
      ))}
    </div>
  </Card>
);

// Command Input
const CommandInput: React.FC<{
  onSubmit: (command: string) => void;
}> = ({ onSubmit }) => {
  const [command, setCommand] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (command.trim()) {
      onSubmit(command);
      setCommand('');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div style={{ display: 'flex', gap: '8px' }}>
        <div style={{ flex: 1 }}>
          <Input
            value={command}
            onChange={(e) => setCommand(e.target.value)}
            placeholder="> Enter command..."
          />
        </div>
        <Button type="submit" variant="primary">
          EXECUTE
        </Button>
      </div>
    </form>
  );
};

// Settings Panel
const SettingsPanel: React.FC = () => {
  const [notifications, setNotifications] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState('30');

  return (
    <Card>
      <Heading level={3} className="terminal-header">
        SETTINGS
      </Heading>
      <Divider />

      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <Toggle checked={notifications} onChange={setNotifications}>
          Enable Notifications
        </Toggle>

        <Toggle checked={autoRefresh} onChange={setAutoRefresh}>
          Auto Refresh
        </Toggle>

        {autoRefresh && (
          <Select value={refreshInterval} onChange={setRefreshInterval}>
            <SelectOption value="10">10 seconds</SelectOption>
            <SelectOption value="30">30 seconds</SelectOption>
            <SelectOption value="60">60 seconds</SelectOption>
          </Select>
        )}

        <Checkbox checked={true} onChange={() => {}}>
          Show detailed metrics
        </Checkbox>
      </div>
    </Card>
  );
};

// Process Table
const ProcessTable: React.FC = () => {
  const processes = [
    { name: 'nginx', status: 'RUNNING', cpu: 2.3, memory: 45 },
    { name: 'postgres', status: 'RUNNING', cpu: 8.1, memory: 256 },
    { name: 'redis', status: 'RUNNING', cpu: 0.5, memory: 32 },
    { name: 'worker-1', status: 'RUNNING', cpu: 12.4, memory: 128 },
    { name: 'cron', status: 'STOPPED', cpu: 0, memory: 0 },
  ];

  return (
    <Card>
      <Heading level={3} className="terminal-header">
        PROCESSES
      </Heading>
      <Divider />
      <Table>
        <TableHeader>
          <TableRow>
            <TableCell>NAME</TableCell>
            <TableCell>STATUS</TableCell>
            <TableCell>CPU %</TableCell>
            <TableCell>MEM (MB)</TableCell>
          </TableRow>
        </TableHeader>
        <TableBody>
          {processes.map((proc) => (
            <TableRow key={proc.name}>
              <TableCell>{proc.name}</TableCell>
              <TableCell>
                <Badge
                  variant={proc.status === 'RUNNING' ? 'default' : 'secondary'}
                >
                  {proc.status}
                </Badge>
              </TableCell>
              <TableCell>{proc.cpu}</TableCell>
              <TableCell>{proc.memory}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Card>
  );
};

// ============================================
// Main Application
// ============================================

const App: React.FC = () => {
  // Theme state
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [tint, setTint] = useState<string>('green');

  // System status (simulated)
  const [status, setStatus] = useState<SystemStatus>({
    cpu: 45,
    memory: 62,
    disk: 23,
    network: '142 MB/s',
  });

  // Logs
  const [logs, setLogs] = useState<LogEntry[]>([
    { timestamp: '14:23:01', level: 'info', message: 'System initialized' },
    { timestamp: '14:23:05', level: 'info', message: 'Services started' },
    { timestamp: '14:23:10', level: 'warning', message: 'High memory usage detected' },
  ]);

  // Loading state
  const [loading, setLoading] = useState(true);

  // Simulate boot sequence
  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 2000);
    return () => clearTimeout(timer);
  }, []);

  // Simulate status updates
  useEffect(() => {
    const interval = setInterval(() => {
      setStatus((prev) => ({
        ...prev,
        cpu: Math.max(10, Math.min(90, prev.cpu + (Math.random() - 0.5) * 10)),
        memory: Math.max(30, Math.min(95, prev.memory + (Math.random() - 0.5) * 5)),
      }));
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  // Handle command execution
  const handleCommand = (command: string) => {
    const timestamp = new Date().toLocaleTimeString('en-US', { hour12: false });
    setLogs((prev) => [
      ...prev,
      { timestamp, level: 'info', message: `Executed: ${command}` },
    ]);
  };

  // Inject custom styles
  useEffect(() => {
    const style = document.createElement('style');
    style.textContent = customStyles;
    document.head.appendChild(style);
    return () => {
      document.head.removeChild(style);
    };
  }, []);

  if (loading) {
    return (
      <div className={`theme-${theme} tint-${tint} terminal-container scanlines`}>
        <Card>
          <Heading level={1} className="terminal-header neon-text">
            SYSTEM BOOT
          </Heading>
          <Divider />
          <Text>Initializing system components...</Text>
          <BarLoader />
        </Card>
      </div>
    );
  }

  return (
    <div className={`theme-${theme} tint-${tint} terminal-container scanlines flicker`}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <Heading level={1} className="terminal-header neon-text">
          SYSTEM MONITOR v2.1
        </Heading>

        <div style={{ display: 'flex', gap: '8px' }}>
          {/* Theme Toggle */}
          <Menu>
            <MenuTrigger>
              <Button variant="secondary">THEME</Button>
            </MenuTrigger>
            <MenuContent>
              <MenuItem onClick={() => setTheme('dark')}>Dark Mode</MenuItem>
              <MenuItem onClick={() => setTheme('light')}>Light Mode</MenuItem>
            </MenuContent>
          </Menu>

          {/* Tint Selector */}
          <Menu>
            <MenuTrigger>
              <Button variant="secondary">COLOR</Button>
            </MenuTrigger>
            <MenuContent>
              <MenuItem onClick={() => setTint('green')}>Green</MenuItem>
              <MenuItem onClick={() => setTint('blue')}>Blue</MenuItem>
              <MenuItem onClick={() => setTint('purple')}>Purple</MenuItem>
              <MenuItem onClick={() => setTint('orange')}>Orange</MenuItem>
              <MenuItem onClick={() => setTint('pink')}>Pink</MenuItem>
            </MenuContent>
          </Menu>

          {/* Info Dialog */}
          <Dialog>
            <DialogTrigger>
              <Button variant="ghost">INFO</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>ABOUT SYSTEM MONITOR</DialogHeader>
              <Text>
                A demonstration of Tuimorphic components with retro terminal styling.
              </Text>
              <CodeBlock language="bash">
                {`npm install tuimorphic`}
              </CodeBlock>
              <DialogFooter>
                <Button variant="primary">CLOSE</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Status Alert */}
      {status.cpu > 80 && (
        <Alert variant="warning" style={{ marginBottom: '20px' }}>
          HIGH CPU USAGE DETECTED - Consider scaling resources
        </Alert>
      )}

      {/* Main Content with Tabs */}
      <Tabs defaultValue="dashboard">
        <TabList>
          <Tab value="dashboard">DASHBOARD</Tab>
          <Tab value="processes">PROCESSES</Tab>
          <Tab value="settings">SETTINGS</Tab>
        </TabList>

        <TabPanel value="dashboard">
          {/* Status Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '20px' }}>
            <StatusCard label="CPU USAGE" value={Math.round(status.cpu)} unit="%" />
            <StatusCard label="MEMORY" value={Math.round(status.memory)} unit="%" />
            <StatusCard label="DISK" value={status.disk} unit="%" />
            <StatusCard label="NETWORK" value={status.network} />
          </div>

          {/* Logs */}
          <LogViewer logs={logs} />

          {/* Command Input */}
          <div style={{ marginTop: '20px' }}>
            <Card>
              <Heading level={3} className="terminal-header">
                COMMAND <span className="cursor"></span>
              </Heading>
              <Divider />
              <CommandInput onSubmit={handleCommand} />
            </Card>
          </div>
        </TabPanel>

        <TabPanel value="processes">
          <ProcessTable />
        </TabPanel>

        <TabPanel value="settings">
          <SettingsPanel />
        </TabPanel>
      </Tabs>

      {/* Footer */}
      <div style={{ marginTop: '20px', textAlign: 'center' }}>
        <Text variant="muted">
          SYSTEM ONLINE | UPTIME: 47d 12h 34m | LAST UPDATE: {new Date().toLocaleTimeString()}
        </Text>
      </div>
    </div>
  );
};

export default App;
