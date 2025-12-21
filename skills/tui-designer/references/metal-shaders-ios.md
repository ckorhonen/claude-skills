# Metal Shaders for iOS/macOS

SwiftUI Metal shader implementations for CRT effects, glow, and retro aesthetics.

## Overview

iOS 17+ and macOS Sonoma+ support Metal shaders directly in SwiftUI via three modifiers:

| Modifier | Purpose |
|----------|---------|
| `.colorEffect()` | Transform pixel colors |
| `.distortionEffect()` | Move/distort pixel positions |
| `.layerEffect()` | Full access to view as texture |

---

## CRT Effect Shader

Complete implementation with barrel distortion, scanlines, chromatic aberration, and flicker.

### CRT.metal

```metal
#include <metal_stdlib>
#include <SwiftUI/SwiftUI.h>
using namespace metal;

// Helper: Barrel distortion
float2 barrelDistort(float2 uv, float strength) {
    float2 center = uv - 0.5;
    float dist = length(center);
    float2 distorted = center * (1.0 + strength * dist * dist);
    return distorted + 0.5;
}

// Main CRT effect shader
[[stitchable]] half4 crtEffect(
    float2 position,
    SwiftUI::Layer layer,
    float time,
    float2 size,
    float scanlineIntensity,      // 0.0 - 0.3 recommended
    float distortionStrength,     // 0.0 - 0.2 recommended
    float chromaticStrength,      // 0.0 - 0.01 recommended
    float flickerIntensity        // 0.0 - 0.05 recommended
) {
    float2 uv = position / size;

    // Apply barrel distortion
    float2 distortedUv = barrelDistort(uv, distortionStrength);

    // Bounds check (black outside screen)
    if (distortedUv.x < 0.0 || distortedUv.x > 1.0 ||
        distortedUv.y < 0.0 || distortedUv.y > 1.0) {
        return half4(0.0, 0.0, 0.0, 1.0);
    }

    float2 samplePos = distortedUv * size;

    // Chromatic aberration (RGB split)
    float2 rOffset = float2(chromaticStrength * size.x, 0.0);
    float2 bOffset = float2(-chromaticStrength * size.x, 0.0);

    half4 color;
    color.r = layer.sample(samplePos + rOffset).r;
    color.g = layer.sample(samplePos).g;
    color.b = layer.sample(samplePos + bOffset).b;
    color.a = layer.sample(samplePos).a;

    // Scanlines
    float scanline = sin(position.y * 3.14159 * 2.0) * 0.5 + 0.5;
    scanline = pow(scanline, 0.5); // Soften
    color.rgb *= 1.0 - (scanlineIntensity * scanline);

    // Subtle brightness variation per line
    float lineVar = sin(position.y * 0.5 + time * 5.0) * 0.02;
    color.rgb *= 1.0 + lineVar;

    // Flicker
    float flicker = 1.0 + flickerIntensity * sin(time * 60.0);
    color.rgb *= flicker;

    // Vignette (darken edges)
    float vignette = 1.0 - length(uv - 0.5) * 0.5;
    vignette = pow(vignette, 0.5);
    color.rgb *= vignette;

    return color;
}

// Simpler scanlines-only shader
[[stitchable]] half4 scanlines(
    float2 position,
    SwiftUI::Layer layer,
    float2 size,
    float intensity,
    float lineSpacing
) {
    half4 color = layer.sample(position);
    float scanline = sin(position.y / lineSpacing * 3.14159) * 0.5 + 0.5;
    color.rgb *= 1.0 - (intensity * scanline);
    return color;
}

// Glow/bloom effect
[[stitchable]] half4 glowEffect(
    float2 position,
    SwiftUI::Layer layer,
    float2 size,
    float radius,
    float intensity
) {
    half4 color = layer.sample(position);
    half4 blur = half4(0);
    float samples = 0.0;

    // Simple box blur for glow
    for (float x = -radius; x <= radius; x += 1.0) {
        for (float y = -radius; y <= radius; y += 1.0) {
            float2 offset = float2(x, y);
            blur += layer.sample(position + offset);
            samples += 1.0;
        }
    }
    blur /= samples;

    // Add glow to original
    return color + blur * intensity;
}
```

### SwiftUI View Modifier

```swift
import SwiftUI

struct CRTEffectModifier: ViewModifier {
    @State private var startTime = Date()

    var scanlineIntensity: Float = 0.1
    var distortionStrength: Float = 0.08
    var chromaticStrength: Float = 0.003
    var flickerIntensity: Float = 0.02

    func body(content: Content) -> some View {
        TimelineView(.animation) { timeline in
            let elapsedTime = Float(timeline.date.timeIntervalSince(startTime))

            GeometryReader { geometry in
                content
                    .layerEffect(
                        ShaderLibrary.crtEffect(
                            .float(elapsedTime),
                            .float2(geometry.size),
                            .float(scanlineIntensity),
                            .float(distortionStrength),
                            .float(chromaticStrength),
                            .float(flickerIntensity)
                        ),
                        maxSampleOffset: CGSize(width: 10, height: 10)
                    )
            }
        }
    }
}

extension View {
    func crtEffect(
        scanlines: Float = 0.1,
        distortion: Float = 0.08,
        chromatic: Float = 0.003,
        flicker: Float = 0.02
    ) -> some View {
        modifier(CRTEffectModifier(
            scanlineIntensity: scanlines,
            distortionStrength: distortion,
            chromaticStrength: chromatic,
            flickerIntensity: flicker
        ))
    }
}
```

### Usage

```swift
struct TerminalView: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("> SYSTEM ONLINE")
            Text("> LOADING MODULES...")
            Text("> READY_")
        }
        .font(.system(size: 16, design: .monospaced))
        .foregroundColor(.green)
        .padding()
        .background(Color.black)
        .crtEffect(
            scanlines: 0.15,
            distortion: 0.1,
            chromatic: 0.002,
            flicker: 0.01
        )
    }
}
```

---

## Neon Glow Effect

Pure SwiftUI glow using shadow modifiers.

### Basic Neon Glow

```swift
extension View {
    func neonGlow(color: Color, radius: CGFloat = 10) -> some View {
        self
            .shadow(color: color.opacity(0.9), radius: radius * 0.25, x: 0, y: 0)
            .shadow(color: color.opacity(0.7), radius: radius * 0.5, x: 0, y: 0)
            .shadow(color: color.opacity(0.5), radius: radius, x: 0, y: 0)
            .shadow(color: color.opacity(0.3), radius: radius * 2, x: 0, y: 0)
    }

    func neonGlowIntense(color: Color) -> some View {
        self
            .shadow(color: .white.opacity(0.9), radius: 2, x: 0, y: 0)
            .shadow(color: color.opacity(0.9), radius: 5, x: 0, y: 0)
            .shadow(color: color.opacity(0.7), radius: 10, x: 0, y: 0)
            .shadow(color: color.opacity(0.5), radius: 20, x: 0, y: 0)
            .shadow(color: color.opacity(0.3), radius: 40, x: 0, y: 0)
            .shadow(color: color.opacity(0.1), radius: 80, x: 0, y: 0)
    }
}
```

### Animated Neon Pulse

```swift
struct NeonPulseModifier: ViewModifier {
    @State private var intensity: CGFloat = 1.0
    let color: Color
    let duration: Double

    func body(content: Content) -> some View {
        content
            .shadow(color: color.opacity(0.9 * intensity), radius: 5, x: 0, y: 0)
            .shadow(color: color.opacity(0.6 * intensity), radius: 15, x: 0, y: 0)
            .shadow(color: color.opacity(0.3 * intensity), radius: 30, x: 0, y: 0)
            .onAppear {
                withAnimation(.easeInOut(duration: duration).repeatForever(autoreverses: true)) {
                    intensity = 0.6
                }
            }
    }
}

extension View {
    func neonPulse(color: Color, duration: Double = 1.5) -> some View {
        modifier(NeonPulseModifier(color: color, duration: duration))
    }
}
```

### Usage

```swift
Text("NEON")
    .font(.system(size: 48, weight: .bold, design: .monospaced))
    .foregroundColor(.cyan)
    .neonGlow(color: .cyan, radius: 15)

Text("PULSE")
    .font(.system(size: 36, design: .monospaced))
    .foregroundColor(.magenta)
    .neonPulse(color: .magenta, duration: 2.0)
```

---

## Inferno Library Effects

[Inferno](https://github.com/twostraws/Inferno) provides 22 pre-built Metal shaders for SwiftUI.

### Installation

```swift
// Swift Package Manager
.package(url: "https://github.com/twostraws/Inferno", from: "1.0.0")
```

### Relevant Effects

```swift
import Inferno

// Interlace (scanlines)
Text("TERMINAL")
    .colorEffect(ShaderLibrary.interlace(
        .float(0.5),      // width of each line
        .color(.black)    // line color
    ))

// White noise (static)
Rectangle()
    .colorEffect(ShaderLibrary.whiteNoise(
        .float(Date().timeIntervalSinceReferenceDate)
    ))

// Circle wave (distortion)
Image("content")
    .distortionEffect(ShaderLibrary.circleWave(
        .float(Date().timeIntervalSinceReferenceDate),
        .float2(200, 200),  // center
        .float(20),         // speed
        .float(10),         // strength
        .float(50)          // frequency
    ), maxSampleOffset: .init(width: 10, height: 10))
```

---

## Color Definitions

### Retro Color Extensions

```swift
extension Color {
    // Phosphor Green
    static let phosphorBright = Color(red: 0, green: 1, blue: 0)
    static let phosphorMedium = Color(red: 0, green: 0.8, blue: 0)
    static let phosphorDim = Color(red: 0, green: 0.6, blue: 0)
    static let phosphorBg = Color(red: 0, green: 0.067, blue: 0)

    // Cyberpunk
    static let cyberCyan = Color(red: 0, green: 1, blue: 1)
    static let cyberMagenta = Color(red: 1, green: 0, blue: 1)
    static let cyberPink = Color(red: 1, green: 0.078, blue: 0.576)
    static let cyberBg = Color(red: 0.039, green: 0.039, blue: 0.102)

    // Amber
    static let amberBright = Color(red: 1, green: 0.69, blue: 0)
    static let amberDim = Color(red: 0.6, green: 0.41, blue: 0)
    static let amberBg = Color(red: 0.102, green: 0.063, blue: 0)
}
```

---

## Performance Considerations

### Shader Compilation

```swift
// iOS 18+: Pre-compile shaders
Task {
    try await ShaderLibrary.crtEffect.compile(as: .layerEffect)
}
```

### Best Practices

1. **Minimize shader complexity** - Each pixel runs the shader
2. **Reduce sample count** in blur/glow effects
3. **Use `maxSampleOffset`** appropriately
4. **Test on older devices** (A12 minimum for iOS 17)
5. **Profile with Instruments** Core Animation template

### Device Performance

| Device | Expected FPS | Notes |
|--------|--------------|-------|
| iPhone 15 Pro | 120 | ProMotion, excellent |
| iPhone 14 | 60 | Good performance |
| iPhone 12 | 60 | May need reduced effects |
| iPad Pro M2 | 120 | Excellent |
| Mac M1+ | 120 | Native performance |

---

## Complete Example: Retro Terminal View

```swift
import SwiftUI

struct RetroTerminalView: View {
    @State private var lines: [String] = [
        "> INITIALIZING SYSTEM...",
        "> LOADING CORE MODULES...",
        "> ESTABLISHING CONNECTION...",
        "> READY_"
    ]

    var body: some View {
        ZStack {
            // Background
            Color.phosphorBg
                .ignoresSafeArea()

            // Terminal content
            VStack(alignment: .leading, spacing: 4) {
                ForEach(lines, id: \.self) { line in
                    Text(line)
                        .font(.system(size: 14, design: .monospaced))
                        .foregroundColor(.phosphorBright)
                }
            }
            .padding()
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
            .neonGlow(color: .phosphorMedium, radius: 5)
        }
        .crtEffect(
            scanlines: 0.12,
            distortion: 0.05,
            chromatic: 0.002,
            flicker: 0.01
        )
        .clipShape(RoundedRectangle(cornerRadius: 20))
        .padding()
    }
}

#Preview {
    RetroTerminalView()
        .preferredColorScheme(.dark)
}
```

---

## Accessibility

```swift
struct AccessibleCRTView: View {
    @Environment(\.accessibilityReduceMotion) var reduceMotion

    var body: some View {
        content
            .modifier(
                reduceMotion
                    ? AnyViewModifier(StaticCRTModifier())
                    : AnyViewModifier(CRTEffectModifier())
            )
    }
}

struct StaticCRTModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .overlay(
                Rectangle()
                    .fill(
                        LinearGradient(
                            colors: [.clear, .black.opacity(0.1)],
                            startPoint: .top,
                            endPoint: .bottom
                        )
                    )
                    .allowsHitTesting(false)
            )
    }
}
```
