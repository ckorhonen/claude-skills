# Tuimorphic Component Reference

Complete API reference for the Tuimorphic React component library.

## Installation

```bash
npm install tuimorphic
# or
yarn add tuimorphic
# or
pnpm add tuimorphic
```

## Setup

```tsx
// Import styles (required)
import 'tuimorphic/styles.css';

// Import components
import { Button, Card, Input } from 'tuimorphic';
```

## Theme Configuration

Apply themes via CSS classes on a container element:

```tsx
// Dark mode with green tint (classic terminal)
<div className="theme-dark tint-green">
  <App />
</div>

// Light mode with blue tint
<div className="theme-light tint-blue">
  <App />
</div>
```

### Available Themes
- `theme-dark` - Dark background, light text
- `theme-light` - Light background, dark text

### Available Tints
- `tint-green` - Classic terminal green
- `tint-blue` - Cool blue
- `tint-red` - Alert red
- `tint-yellow` - Warning yellow
- `tint-purple` - Creative purple
- `tint-orange` - Energetic orange
- `tint-pink` - Playful pink

### CSS Custom Properties

Override theme values:

```css
:root {
  --theme-background: #001100;
  --theme-foreground: #00ff00;
  --theme-accent: #00cc00;
  --theme-border: #004400;
  --theme-muted: #003300;
}
```

---

## Component Reference

### Form Controls

#### Button
```tsx
import { Button } from 'tuimorphic';

<Button variant="primary">Submit</Button>
<Button variant="secondary">Cancel</Button>
<Button variant="ghost">More Info</Button>
<Button disabled>Disabled</Button>
```

**Props:**
- `variant`: `"primary"` | `"secondary"` | `"ghost"`
- `disabled`: `boolean`
- `onClick`: `() => void`

#### Input
```tsx
import { Input } from 'tuimorphic';

<Input
  placeholder="Enter command..."
  value={value}
  onChange={(e) => setValue(e.target.value)}
/>

<Input type="password" placeholder="Password" />
<Input disabled placeholder="Disabled" />
```

**Props:**
- `type`: `"text"` | `"password"` | `"email"` | etc.
- `placeholder`: `string`
- `value`: `string`
- `disabled`: `boolean`
- `onChange`: `(e: ChangeEvent) => void`

#### TextArea
```tsx
import { TextArea } from 'tuimorphic';

<TextArea
  placeholder="Enter description..."
  rows={4}
  value={text}
  onChange={(e) => setText(e.target.value)}
/>
```

#### Checkbox
```tsx
import { Checkbox } from 'tuimorphic';

<Checkbox
  checked={checked}
  onChange={(checked) => setChecked(checked)}
>
  Enable notifications
</Checkbox>
```

#### RadioGroup
```tsx
import { RadioGroup, RadioItem } from 'tuimorphic';

<RadioGroup value={selected} onChange={setSelected}>
  <RadioItem value="option1">Option 1</RadioItem>
  <RadioItem value="option2">Option 2</RadioItem>
  <RadioItem value="option3">Option 3</RadioItem>
</RadioGroup>
```

#### Toggle
```tsx
import { Toggle } from 'tuimorphic';

<Toggle
  checked={enabled}
  onChange={(enabled) => setEnabled(enabled)}
>
  Dark Mode
</Toggle>
```

#### Select
```tsx
import { Select, SelectOption } from 'tuimorphic';

<Select value={selected} onChange={setSelected}>
  <SelectOption value="1">Option 1</SelectOption>
  <SelectOption value="2">Option 2</SelectOption>
  <SelectOption value="3">Option 3</SelectOption>
</Select>
```

#### ComboBox
```tsx
import { ComboBox } from 'tuimorphic';

<ComboBox
  options={['Apple', 'Banana', 'Cherry']}
  value={fruit}
  onChange={setFruit}
  placeholder="Select fruit..."
/>
```

#### DatePicker
```tsx
import { DatePicker } from 'tuimorphic';

<DatePicker
  value={date}
  onChange={setDate}
/>
```

#### Slider
```tsx
import { Slider } from 'tuimorphic';

<Slider
  min={0}
  max={100}
  value={volume}
  onChange={setVolume}
/>
```

---

### Layout Components

#### Card
```tsx
import { Card } from 'tuimorphic';

<Card>
  <h2>Card Title</h2>
  <p>Card content goes here.</p>
</Card>
```

#### CardDouble
```tsx
import { CardDouble } from 'tuimorphic';

<CardDouble>
  <div>Left Panel</div>
  <div>Right Panel</div>
</CardDouble>
```

#### Grid
```tsx
import { Grid, GridItem } from 'tuimorphic';

<Grid columns={3} gap={16}>
  <GridItem>Item 1</GridItem>
  <GridItem>Item 2</GridItem>
  <GridItem>Item 3</GridItem>
</Grid>
```

#### Tabs
```tsx
import { Tabs, TabList, Tab, TabPanel } from 'tuimorphic';

<Tabs defaultValue="tab1">
  <TabList>
    <Tab value="tab1">Overview</Tab>
    <Tab value="tab2">Details</Tab>
    <Tab value="tab3">Settings</Tab>
  </TabList>
  <TabPanel value="tab1">Overview content</TabPanel>
  <TabPanel value="tab2">Details content</TabPanel>
  <TabPanel value="tab3">Settings content</TabPanel>
</Tabs>
```

#### Accordion
```tsx
import { Accordion, AccordionItem } from 'tuimorphic';

<Accordion>
  <AccordionItem title="Section 1">
    Content for section 1
  </AccordionItem>
  <AccordionItem title="Section 2">
    Content for section 2
  </AccordionItem>
</Accordion>
```

#### SidebarLayout
```tsx
import { SidebarLayout, Sidebar, SidebarContent } from 'tuimorphic';

<SidebarLayout>
  <Sidebar>
    <nav>Navigation items</nav>
  </Sidebar>
  <SidebarContent>
    Main content area
  </SidebarContent>
</SidebarLayout>
```

#### Divider
```tsx
import { Divider } from 'tuimorphic';

<Divider />
<Divider orientation="vertical" />
```

---

### Feedback Elements

#### Alert
```tsx
import { Alert } from 'tuimorphic';

<Alert variant="info">Information message</Alert>
<Alert variant="success">Success message</Alert>
<Alert variant="warning">Warning message</Alert>
<Alert variant="error">Error message</Alert>
```

**Props:**
- `variant`: `"info"` | `"success"` | `"warning"` | `"error"`

#### Badge
```tsx
import { Badge } from 'tuimorphic';

<Badge>New</Badge>
<Badge variant="secondary">Beta</Badge>
```

#### Progress
```tsx
import { Progress } from 'tuimorphic';

<Progress value={75} max={100} />
```

#### Tooltip
```tsx
import { Tooltip } from 'tuimorphic';

<Tooltip content="Helpful information">
  <Button>Hover me</Button>
</Tooltip>
```

#### BarLoader / BlockLoader
```tsx
import { BarLoader, BlockLoader } from 'tuimorphic';

<BarLoader />
<BlockLoader />
```

#### Message
```tsx
import { Message } from 'tuimorphic';

<Message type="system">System initialized</Message>
<Message type="user">User input here</Message>
<Message type="error">Error occurred</Message>
```

---

### Overlays

#### Dialog
```tsx
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogFooter } from 'tuimorphic';

<Dialog>
  <DialogTrigger>
    <Button>Open Dialog</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>Dialog Title</DialogHeader>
    <p>Dialog content goes here.</p>
    <DialogFooter>
      <Button variant="ghost">Cancel</Button>
      <Button variant="primary">Confirm</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

#### Drawer
```tsx
import { Drawer, DrawerTrigger, DrawerContent } from 'tuimorphic';

<Drawer>
  <DrawerTrigger>
    <Button>Open Drawer</Button>
  </DrawerTrigger>
  <DrawerContent side="right">
    Drawer content
  </DrawerContent>
</Drawer>
```

#### Menu
```tsx
import { Menu, MenuTrigger, MenuContent, MenuItem } from 'tuimorphic';

<Menu>
  <MenuTrigger>
    <Button>Menu</Button>
  </MenuTrigger>
  <MenuContent>
    <MenuItem onClick={() => {}}>Item 1</MenuItem>
    <MenuItem onClick={() => {}}>Item 2</MenuItem>
    <MenuItem onClick={() => {}}>Item 3</MenuItem>
  </MenuContent>
</Menu>
```

#### Popover
```tsx
import { Popover, PopoverTrigger, PopoverContent } from 'tuimorphic';

<Popover>
  <PopoverTrigger>
    <Button>Info</Button>
  </PopoverTrigger>
  <PopoverContent>
    Additional information here
  </PopoverContent>
</Popover>
```

---

### Data Display

#### CodeBlock
```tsx
import { CodeBlock } from 'tuimorphic';

<CodeBlock language="javascript">
{`function hello() {
  console.log("Hello, World!");
}`}
</CodeBlock>
```

#### TreeView
```tsx
import { TreeView, TreeItem } from 'tuimorphic';

<TreeView>
  <TreeItem label="src">
    <TreeItem label="components">
      <TreeItem label="Button.tsx" />
      <TreeItem label="Input.tsx" />
    </TreeItem>
    <TreeItem label="App.tsx" />
  </TreeItem>
</TreeView>
```

#### Table
```tsx
import { Table, TableHeader, TableBody, TableRow, TableCell } from 'tuimorphic';

<Table>
  <TableHeader>
    <TableRow>
      <TableCell>Name</TableCell>
      <TableCell>Status</TableCell>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow>
      <TableCell>Server 1</TableCell>
      <TableCell>Online</TableCell>
    </TableRow>
  </TableBody>
</Table>
```

#### Avatar
```tsx
import { Avatar } from 'tuimorphic';

<Avatar src="/user.png" alt="User" />
<Avatar fallback="JD" />
```

#### Code (Inline)
```tsx
import { Code } from 'tuimorphic';

<p>Run <Code>npm install</Code> to get started.</p>
```

---

### Navigation

#### BreadCrumbs
```tsx
import { BreadCrumbs, BreadCrumb } from 'tuimorphic';

<BreadCrumbs>
  <BreadCrumb href="/">Home</BreadCrumb>
  <BreadCrumb href="/docs">Docs</BreadCrumb>
  <BreadCrumb>Current Page</BreadCrumb>
</BreadCrumbs>
```

#### Navigation
```tsx
import { Navigation, NavItem } from 'tuimorphic';

<Navigation>
  <NavItem href="/" active>Home</NavItem>
  <NavItem href="/about">About</NavItem>
  <NavItem href="/contact">Contact</NavItem>
</Navigation>
```

#### ActionBar
```tsx
import { ActionBar, ActionButton } from 'tuimorphic';

<ActionBar>
  <ActionButton icon="save" onClick={save}>Save</ActionButton>
  <ActionButton icon="delete" onClick={del}>Delete</ActionButton>
</ActionBar>
```

---

### Typography

#### Text
```tsx
import { Text } from 'tuimorphic';

<Text>Regular text</Text>
<Text variant="muted">Muted text</Text>
<Text variant="code">Code text</Text>
```

#### Heading
```tsx
import { Heading } from 'tuimorphic';

<Heading level={1}>Main Heading</Heading>
<Heading level={2}>Sub Heading</Heading>
<Heading level={3}>Section Heading</Heading>
```

#### Label
```tsx
import { Label } from 'tuimorphic';

<Label htmlFor="input-id">Field Label</Label>
```

---

## Common Patterns

### Terminal-Style Form
```tsx
<Card>
  <Heading level={2}>LOGIN</Heading>
  <Divider />
  <div className="space-y-4">
    <div>
      <Label>USERNAME</Label>
      <Input placeholder="Enter username..." />
    </div>
    <div>
      <Label>PASSWORD</Label>
      <Input type="password" placeholder="Enter password..." />
    </div>
    <Button variant="primary">AUTHENTICATE</Button>
  </div>
</Card>
```

### Status Dashboard
```tsx
<Grid columns={2} gap={16}>
  <Card>
    <Text variant="muted">CPU USAGE</Text>
    <Heading level={2}>45%</Heading>
    <Progress value={45} />
  </Card>
  <Card>
    <Text variant="muted">MEMORY</Text>
    <Heading level={2}>2.1GB</Heading>
    <Progress value={52} />
  </Card>
</Grid>
```

### Command Output
```tsx
<Card>
  <Message type="system">[SYS] Initializing...</Message>
  <Message type="system">[SYS] Loading modules...</Message>
  <Message type="user">> run diagnostic</Message>
  <Message type="system">[SYS] Diagnostic complete. All systems nominal.</Message>
</Card>
```

---

## TypeScript Support

All components export their prop types:

```tsx
import { Button, ButtonProps } from 'tuimorphic';

const CustomButton: React.FC<ButtonProps> = (props) => {
  return <Button {...props} className="custom-class" />;
};
```

---

## Accessibility

Tuimorphic components are built on Base UI primitives and include:
- WAI-ARIA compliance
- Keyboard navigation
- Focus management
- Screen reader support

---

## Resources

- [GitHub Repository](https://github.com/douglance/tuimorphic)
- [Live Demo](https://tuimorphic.com)
- [NPM Package](https://www.npmjs.com/package/tuimorphic)
