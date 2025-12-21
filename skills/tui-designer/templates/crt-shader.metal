/**
 * CRT Effect Metal Shader
 *
 * Complete Metal shader for authentic CRT monitor effects in SwiftUI.
 * Add this file to your Xcode project alongside your Swift files.
 *
 * Features:
 *   - Barrel distortion (screen curvature)
 *   - Animated scanlines
 *   - Chromatic aberration (RGB split)
 *   - Flicker effect
 *   - Vignette (edge darkening)
 *
 * Usage in SwiftUI:
 *   .layerEffect(
 *       ShaderLibrary.crtEffect(
 *           .float(time),
 *           .float2(size),
 *           .float(scanlineIntensity),
 *           .float(distortionStrength),
 *           .float(chromaticStrength),
 *           .float(flickerIntensity)
 *       ),
 *       maxSampleOffset: CGSize(width: 10, height: 10)
 *   )
 */

#include <metal_stdlib>
#include <SwiftUI/SwiftUI.h>
using namespace metal;

// ============================================
// Helper Functions
// ============================================

/**
 * Barrel distortion - simulates CRT screen curvature
 * strength: 0.0 = no distortion, 0.2 = strong curvature
 */
float2 barrelDistort(float2 uv, float strength) {
    float2 center = uv - 0.5;
    float dist = length(center);
    float2 distorted = center * (1.0 + strength * dist * dist);
    return distorted + 0.5;
}

/**
 * Simple hash function for noise generation
 */
float hash(float2 p) {
    return fract(sin(dot(p, float2(12.9898, 78.233))) * 43758.5453);
}

// ============================================
// Main CRT Effect Shader
// ============================================

[[stitchable]] half4 crtEffect(
    float2 position,
    SwiftUI::Layer layer,
    float time,
    float2 size,
    float scanlineIntensity,      // Recommended: 0.05 - 0.2
    float distortionStrength,     // Recommended: 0.0 - 0.15
    float chromaticStrength,      // Recommended: 0.0 - 0.005
    float flickerIntensity        // Recommended: 0.0 - 0.03
) {
    // Convert to UV coordinates (0-1)
    float2 uv = position / size;

    // Apply barrel distortion
    float2 distortedUv = barrelDistort(uv, distortionStrength);

    // Check bounds (render black outside the curved screen)
    if (distortedUv.x < 0.0 || distortedUv.x > 1.0 ||
        distortedUv.y < 0.0 || distortedUv.y > 1.0) {
        return half4(0.0, 0.0, 0.0, 1.0);
    }

    // Convert back to pixel coordinates
    float2 samplePos = distortedUv * size;

    // Chromatic aberration - sample R, G, B at slightly different positions
    float2 rOffset = float2(chromaticStrength * size.x, 0.0);
    float2 bOffset = float2(-chromaticStrength * size.x, 0.0);

    half4 color;
    color.r = layer.sample(samplePos + rOffset).r;
    color.g = layer.sample(samplePos).g;
    color.b = layer.sample(samplePos + bOffset).b;
    color.a = layer.sample(samplePos).a;

    // Scanlines - horizontal lines that darken at regular intervals
    float scanlineFrequency = 2.0; // Lines per pixel
    float scanline = sin(position.y * 3.14159 * scanlineFrequency) * 0.5 + 0.5;
    scanline = pow(scanline, 0.5); // Soften the transition
    color.rgb *= 1.0 - (scanlineIntensity * scanline);

    // Subtle per-line brightness variation (simulates refresh)
    float lineVariation = sin(position.y * 0.5 + time * 5.0) * 0.02;
    color.rgb *= 1.0 + lineVariation;

    // Flicker - rapid brightness changes
    float flicker = 1.0 + flickerIntensity * sin(time * 60.0);
    color.rgb *= flicker;

    // Vignette - darken the edges
    float vignette = 1.0 - length(uv - 0.5) * 0.5;
    vignette = pow(vignette, 0.5);
    color.rgb *= vignette;

    return color;
}

// ============================================
// Scanlines-Only Shader (Lighter Weight)
// ============================================

[[stitchable]] half4 scanlines(
    float2 position,
    SwiftUI::Layer layer,
    float2 size,
    float intensity,      // Recommended: 0.1 - 0.3
    float lineSpacing     // Recommended: 2.0 - 4.0
) {
    half4 color = layer.sample(position);

    float scanline = sin(position.y / lineSpacing * 3.14159) * 0.5 + 0.5;
    color.rgb *= 1.0 - (intensity * scanline);

    return color;
}

// ============================================
// Glow/Bloom Effect
// ============================================

[[stitchable]] half4 glowEffect(
    float2 position,
    SwiftUI::Layer layer,
    float2 size,
    float radius,         // Recommended: 3.0 - 10.0
    float intensity       // Recommended: 0.1 - 0.5
) {
    half4 originalColor = layer.sample(position);
    half4 blurredColor = half4(0);
    float samples = 0.0;

    // Simple box blur for glow effect
    for (float x = -radius; x <= radius; x += 1.0) {
        for (float y = -radius; y <= radius; y += 1.0) {
            float2 offset = float2(x, y);
            float2 samplePos = position + offset;

            // Stay within bounds
            if (samplePos.x >= 0 && samplePos.x < size.x &&
                samplePos.y >= 0 && samplePos.y < size.y) {
                blurredColor += layer.sample(samplePos);
                samples += 1.0;
            }
        }
    }

    blurredColor /= samples;

    // Add glow to original color
    return originalColor + blurredColor * intensity;
}

// ============================================
// Phosphor Persistence Effect
// ============================================

[[stitchable]] half4 phosphorGlow(
    float2 position,
    SwiftUI::Layer layer,
    float2 size,
    float glowStrength    // Recommended: 0.1 - 0.3
) {
    half4 color = layer.sample(position);

    // Boost brightness slightly for phosphor glow appearance
    float brightness = (color.r + color.g + color.b) / 3.0;

    // Add subtle glow to bright areas
    half4 glow = color * brightness * glowStrength;

    return color + glow;
}

// ============================================
// Static Noise Effect
// ============================================

[[stitchable]] half4 staticNoise(
    float2 position,
    SwiftUI::Layer layer,
    float time,
    float intensity       // Recommended: 0.02 - 0.1
) {
    half4 color = layer.sample(position);

    // Generate random noise based on position and time
    float noise = hash(position + time * 100.0);

    // Add noise to the color
    color.rgb += (noise - 0.5) * intensity;

    return color;
}

// ============================================
// Combined CRT Effect (All Features)
// ============================================

[[stitchable]] half4 crtEffectFull(
    float2 position,
    SwiftUI::Layer layer,
    float time,
    float2 size,
    float scanlineIntensity,
    float distortionStrength,
    float chromaticStrength,
    float flickerIntensity,
    float noiseIntensity,
    float vignetteStrength
) {
    float2 uv = position / size;

    // Barrel distortion
    float2 distortedUv = barrelDistort(uv, distortionStrength);

    // Bounds check
    if (distortedUv.x < 0.0 || distortedUv.x > 1.0 ||
        distortedUv.y < 0.0 || distortedUv.y > 1.0) {
        return half4(0.0, 0.0, 0.0, 1.0);
    }

    float2 samplePos = distortedUv * size;

    // Chromatic aberration
    float2 rOffset = float2(chromaticStrength * size.x, 0.0);
    float2 bOffset = float2(-chromaticStrength * size.x, 0.0);

    half4 color;
    color.r = layer.sample(samplePos + rOffset).r;
    color.g = layer.sample(samplePos).g;
    color.b = layer.sample(samplePos + bOffset).b;
    color.a = layer.sample(samplePos).a;

    // Scanlines
    float scanline = sin(position.y * 3.14159 * 2.0) * 0.5 + 0.5;
    scanline = pow(scanline, 0.5);
    color.rgb *= 1.0 - (scanlineIntensity * scanline);

    // Line variation
    float lineVar = sin(position.y * 0.5 + time * 5.0) * 0.02;
    color.rgb *= 1.0 + lineVar;

    // Flicker
    float flicker = 1.0 + flickerIntensity * sin(time * 60.0);
    color.rgb *= flicker;

    // Static noise
    float noise = hash(position + time * 100.0);
    color.rgb += (noise - 0.5) * noiseIntensity;

    // Vignette
    float vignette = 1.0 - length(uv - 0.5) * vignetteStrength;
    vignette = pow(max(vignette, 0.0), 0.5);
    color.rgb *= vignette;

    return color;
}
