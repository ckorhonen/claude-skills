# CRT Effects for Web

CSS, WebGL, and JavaScript techniques for authentic CRT monitor effects.

## CSS-Only Effects

### Scanlines Overlay

```css
/* Basic scanlines using repeating gradient */
.scanlines {
  position: relative;
}

.scanlines::after {
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    rgba(0, 0, 0, 0.15),
    rgba(0, 0, 0, 0.15) 1px,
    transparent 1px,
    transparent 2px
  );
  pointer-events: none;
  z-index: 10;
}

/* Animated scanlines */
.scanlines-animated::after {
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
  animation: scanline-scroll 10s linear infinite;
  pointer-events: none;
}

@keyframes scanline-scroll {
  from { background-position: 0 0; }
  to { background-position: 0 100%; }
}
```

### Neon Text Glow

```css
/* Basic neon glow */
.neon-text {
  color: #0ff;
  text-shadow:
    0 0 5px #fff,
    0 0 10px #fff,
    0 0 20px #0ff,
    0 0 40px #0ff,
    0 0 80px #0ff;
}

/* Intense neon (more layers) */
.neon-text-intense {
  color: #fff;
  text-shadow:
    0 0 2px #fff,
    0 0 5px #fff,
    0 0 10px #0ff,
    0 0 20px #0ff,
    0 0 30px #0ff,
    0 0 40px #0ff,
    0 0 55px #0ff,
    0 0 75px #0ff,
    0 0 100px #0ff;
}

/* Multi-color neon (cyberpunk) */
.neon-text-cyber {
  color: #fff;
  text-shadow:
    0 0 5px #fff,
    0 0 10px #ff00ff,
    0 0 20px #ff00ff,
    0 0 40px #00ffff,
    0 0 80px #00ffff;
}

/* Pulsing animation */
@keyframes neon-pulse {
  0%, 100% {
    text-shadow:
      0 0 5px #fff,
      0 0 10px #0ff,
      0 0 20px #0ff,
      0 0 40px #0ff;
  }
  50% {
    text-shadow:
      0 0 10px #fff,
      0 0 20px #0ff,
      0 0 40px #0ff,
      0 0 80px #0ff;
  }
}

.neon-pulse {
  animation: neon-pulse 2s ease-in-out infinite;
}
```

### Neon Border Glow

```css
.neon-border {
  border: 2px solid #0ff;
  box-shadow:
    0 0 5px #0ff,
    0 0 10px #0ff,
    inset 0 0 5px #0ff,
    inset 0 0 10px #0ff;
}

/* Rounded neon border */
.neon-border-rounded {
  border: 2px solid #0ff;
  border-radius: 8px;
  box-shadow:
    0 0 5px #0ff,
    0 0 10px #0ff,
    0 0 20px #0ff,
    inset 0 0 5px rgba(0, 255, 255, 0.2);
}
```

### CRT Screen Curvature

```css
.crt-curved {
  border-radius: 20px / 10px;
  overflow: hidden;
}

/* Perspective-based curvature */
.crt-perspective {
  transform: perspective(1000px) rotateX(2deg);
  border-radius: 10px;
}

/* Vignette effect */
.crt-vignette {
  position: relative;
}

.crt-vignette::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(
    ellipse at center,
    transparent 50%,
    rgba(0, 0, 0, 0.5) 100%
  );
  pointer-events: none;
}
```

### Flicker Effect

```css
@keyframes flicker {
  0%, 19.999%, 22%, 62.999%, 64%, 64.999%, 70%, 100% {
    opacity: 1;
  }
  20%, 21.999%, 63%, 63.999%, 65%, 69.999% {
    opacity: 0.95;
  }
}

.flicker {
  animation: flicker 3s infinite;
}

/* Subtle flicker (less distracting) */
@keyframes flicker-subtle {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.98; }
  52% { opacity: 1; }
  54% { opacity: 0.96; }
}

.flicker-subtle {
  animation: flicker-subtle 0.1s infinite;
}
```

### RGB Chromatic Aberration (CSS)

```css
.chromatic {
  position: relative;
}

.chromatic::before,
.chromatic::after {
  content: attr(data-text);
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.chromatic::before {
  color: #f00;
  left: 2px;
  clip-path: polygon(0 0, 100% 0, 100% 45%, 0 45%);
  animation: chromatic-shift 2s infinite;
}

.chromatic::after {
  color: #0ff;
  left: -2px;
  clip-path: polygon(0 55%, 100% 55%, 100% 100%, 0 100%);
  animation: chromatic-shift 2s infinite reverse;
}

@keyframes chromatic-shift {
  0%, 100% { transform: translateX(0); }
  50% { transform: translateX(1px); }
}
```

---

## WebGL: CRTFilter.js

### Installation

```bash
npm install crtfilter
# or use CDN
```

### Basic Setup

```javascript
import { CRTFilterWebGL } from 'crtfilter';

// Get your canvas element
const canvas = document.getElementById('crt-canvas');

// Initialize with options
const crt = new CRTFilterWebGL(canvas, {
  // Effect intensities (0-1)
  scanlineIntensity: 0.15,
  glowBloom: 0.3,
  chromaticAberration: 0.002,
  barrelDistortion: 0.1,
  staticNoise: 0.03,

  // Boolean effects
  flicker: true,
  retraceLines: true,
  dotMask: true,

  // Advanced
  horizontalTearing: 0.01,
  verticalJitter: 0.01,
  signalLoss: false
});

// Start rendering
crt.start();

// Stop when needed
// crt.stop();
```

### Effect Parameters

| Parameter | Range | Description |
|-----------|-------|-------------|
| `scanlineIntensity` | 0-1 | Horizontal scanline darkness |
| `glowBloom` | 0-1 | Glow/bloom around bright areas |
| `chromaticAberration` | 0-0.01 | RGB channel separation |
| `barrelDistortion` | 0-0.5 | CRT screen curvature |
| `staticNoise` | 0-1 | Random noise intensity |
| `flicker` | bool | Enable screen flicker |
| `retraceLines` | bool | Horizontal refresh lines |
| `dotMask` | bool | CRT phosphor dot pattern |
| `horizontalTearing` | 0-0.1 | Horizontal sync issues |
| `verticalJitter` | 0-0.1 | Vertical instability |
| `signalLoss` | bool | Simulate signal degradation |

### Rendering Content

```javascript
// Render another element to the CRT canvas
const sourceElement = document.getElementById('content');

// Option 1: Single frame
crt.renderElement(sourceElement);

// Option 2: Continuous render
function animate() {
  crt.renderElement(sourceElement);
  requestAnimationFrame(animate);
}
animate();
```

---

## React Three Fiber: Post-Processing

For React apps needing advanced bloom/glow effects.

### Installation

```bash
npm install @react-three/fiber @react-three/postprocessing three
```

### Basic Bloom Setup

```tsx
import { Canvas } from '@react-three/fiber';
import { EffectComposer, Bloom, Vignette, Noise } from '@react-three/postprocessing';

function CRTScene() {
  return (
    <Canvas>
      {/* Your 3D/2D content */}
      <mesh>
        <planeGeometry args={[4, 3]} />
        <meshBasicMaterial color="#00ff00" toneMapped={false} />
      </mesh>

      {/* Post-processing effects */}
      <EffectComposer>
        <Bloom
          luminanceThreshold={0.9}
          luminanceSmoothing={0.9}
          intensity={0.5}
        />
        <Vignette darkness={0.5} offset={0.5} />
        <Noise opacity={0.02} />
      </EffectComposer>
    </Canvas>
  );
}
```

### Selective Bloom

Make only certain elements glow by using emissive colors:

```tsx
// This will glow (color > 1.0 with toneMapped=false)
<meshStandardMaterial
  color="#00ff00"
  emissive="#00ff00"
  emissiveIntensity={2}
  toneMapped={false}
/>

// This won't glow (color in normal range)
<meshStandardMaterial color="#333333" />
```

### Custom Scanline Effect

```tsx
import { extend, useFrame } from '@react-three/fiber';
import { shaderMaterial } from '@react-three/drei';

const ScanlineMaterial = shaderMaterial(
  { time: 0, intensity: 0.1 },
  // Vertex shader
  `varying vec2 vUv;
   void main() {
     vUv = uv;
     gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
   }`,
  // Fragment shader
  `uniform float time;
   uniform float intensity;
   varying vec2 vUv;
   void main() {
     float scanline = sin(vUv.y * 800.0) * intensity;
     vec3 color = vec3(0.0, 1.0, 0.0); // Green
     color *= 1.0 - scanline;
     gl_FragColor = vec4(color, 1.0);
   }`
);

extend({ ScanlineMaterial });

function ScanlineOverlay() {
  const ref = useRef();
  useFrame(({ clock }) => {
    ref.current.time = clock.elapsedTime;
  });

  return (
    <mesh>
      <planeGeometry args={[2, 2]} />
      <scanlineMaterial ref={ref} transparent opacity={0.5} />
    </mesh>
  );
}
```

---

## Pure JavaScript CRT Shader

For custom WebGL implementations:

```javascript
const vertexShader = `
  attribute vec2 position;
  varying vec2 vUv;
  void main() {
    vUv = position * 0.5 + 0.5;
    gl_Position = vec4(position, 0.0, 1.0);
  }
`;

const fragmentShader = `
  precision mediump float;
  uniform sampler2D uTexture;
  uniform float uTime;
  uniform vec2 uResolution;
  varying vec2 vUv;

  // Barrel distortion
  vec2 distort(vec2 uv, float strength) {
    vec2 center = uv - 0.5;
    float dist = length(center);
    return center * (1.0 + strength * dist * dist) + 0.5;
  }

  void main() {
    vec2 uv = distort(vUv, 0.1);

    // Bounds check
    if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) {
      gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
      return;
    }

    // Sample texture
    vec4 color = texture2D(uTexture, uv);

    // Scanlines
    float scanline = sin(uv.y * uResolution.y * 3.14159) * 0.1;
    color.rgb *= 1.0 - scanline;

    // Vignette
    float vignette = 1.0 - length(vUv - 0.5) * 0.8;
    color.rgb *= vignette;

    // Flicker
    color.rgb *= 1.0 + 0.01 * sin(uTime * 60.0);

    gl_FragColor = color;
  }
`;
```

---

## Performance Optimization

### CSS Effects
- Limit `box-shadow` to 4-5 layers
- Use `will-change: transform` sparingly
- Avoid animating `box-shadow` (animate `opacity` instead)
- Test on mobile devices

### WebGL
- Use lower resolution render targets
- Reduce number of shader passes
- Consider `requestAnimationFrame` throttling
- Profile with browser DevTools

### Best Practices
```css
/* Performance-friendly glow */
.glow-optimized {
  /* Pre-compute on GPU */
  will-change: filter;
  /* Use filter instead of box-shadow for better perf */
  filter: drop-shadow(0 0 10px #0ff);
}

/* Reduce motion for accessibility */
@media (prefers-reduced-motion: reduce) {
  .flicker,
  .neon-pulse,
  .scanlines-animated::after {
    animation: none;
  }
}
```

---

## Complete Example: CRT Terminal

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    .crt-container {
      background: #000800;
      padding: 20px;
      border-radius: 20px;
      position: relative;
      overflow: hidden;
    }

    /* Scanlines */
    .crt-container::after {
      content: '';
      position: absolute;
      inset: 0;
      background: repeating-linear-gradient(
        0deg,
        rgba(0, 0, 0, 0.15),
        rgba(0, 0, 0, 0.15) 1px,
        transparent 1px,
        transparent 2px
      );
      pointer-events: none;
    }

    /* Vignette */
    .crt-container::before {
      content: '';
      position: absolute;
      inset: 0;
      background: radial-gradient(
        ellipse at center,
        transparent 50%,
        rgba(0, 0, 0, 0.5) 100%
      );
      pointer-events: none;
    }

    .terminal-text {
      font-family: 'SF Mono', monospace;
      color: #00ff00;
      text-shadow:
        0 0 5px #00ff00,
        0 0 10px #00ff00;
      animation: flicker-subtle 0.1s infinite;
    }

    @keyframes flicker-subtle {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.98; }
    }
  </style>
</head>
<body>
  <div class="crt-container">
    <pre class="terminal-text">
> SYSTEM INITIALIZED
> LOADING MODULES...
> READY_
    </pre>
  </div>
</body>
</html>
```
