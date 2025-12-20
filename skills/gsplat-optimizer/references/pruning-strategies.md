# Gaussian Pruning Strategies

Techniques for reducing gaussian count while maintaining visual quality.

## Overview

Pruning removes unnecessary gaussians to meet GPU memory and performance budgets. The goal is to achieve target FPS on the device while minimizing visual degradation.

## Pruning Methods

### 1. Opacity Thresholding

Remove gaussians with opacity below a threshold.

**Recommended thresholds:**
- Aggressive: `opacity < 0.05` (removes ~20-40% of gaussians)
- Moderate: `opacity < 0.02` (removes ~10-20%)
- Conservative: `opacity < 0.01` (removes ~5-10%)

```python
# Example: opacity thresholding
def prune_by_opacity(gaussians, threshold=0.02):
    return [g for g in gaussians if g.opacity >= threshold]
```

**Trade-offs:**
- Aggressive pruning may cause visible "holes" in semi-transparent areas
- Start conservative and increase threshold until artifacts appear

### 2. Size-Based Culling

Remove gaussians that are too small to be visible at target resolution.

**Calculation:**
```python
# Gaussian projects to ~3 sigma pixels on screen
pixel_size = (scale * 3) / depth * focal_length

# Cull if smaller than threshold
if pixel_size < min_pixel_threshold:
    cull(gaussian)
```

**Recommended thresholds:**
- 1080p: `min_pixel_size = 0.5px`
- 4K: `min_pixel_size = 0.25px`
- Vision Pro: `min_pixel_size = 0.3px` (per eye)

### 3. Importance-Based Pruning (LODGE Algorithm)

LODGE uses an error-proxy to identify least-contributing gaussians:

1. **Compute importance score** based on:
   - View coverage (how many views the gaussian contributes to)
   - Contribution magnitude (opacity × size × visibility)
   - Rendering error delta when removed

2. **Prune lowest-importance gaussians** until budget is met

3. **Fine-tune remaining gaussians** to compensate for removed ones

**Reference:** [LODGE: Level-of-Detail Large-Scale Gaussian Splatting](https://arxiv.org/abs/2505.23158)

### 4. View-Frustum Culling

Only render gaussians visible in the current view frustum.

**Implementation:**
- Use octree or BVH for spatial queries
- Cull gaussians outside frustum before GPU upload
- Update culling each frame for dynamic cameras

**MetalSplatter approach:**
- Hierarchical frustum culling on CPU
- Per-gaussian visibility in compute shader

### 5. Foveated Rendering (Vision Pro)

Reduce gaussian density based on distance from gaze point.

**Zones:**
- Foveal (0-5 deg): Full density
- Parafoveal (5-15 deg): 50% density
- Peripheral (15+ deg): 25% density

**Implementation:**
- Use eye tracking data from Vision Pro
- Apply density reduction in compute shader
- Blend smoothly between zones

**Reference:** [RTGS: Real-Time Gaussian Splatting on Mobile](https://arxiv.org/abs/2406.01828)

## Pruning Pipeline

```
Original PLY (e.g., 10M gaussians)
    |
Opacity threshold (< 0.02)
    | ~8M gaussians
Size culling (< 0.5px @ 1080p)
    | ~6M gaussians
Importance pruning (target: 4M)
    | 4M gaussians
Fine-tuning (optimize remaining)
    |
Optimized PLY (4M gaussians)
```

## Quality Metrics

Measure pruning impact with:

| Metric | Description | Target |
|--------|-------------|--------|
| PSNR | Peak signal-to-noise ratio | > 30 dB |
| SSIM | Structural similarity | > 0.95 |
| LPIPS | Perceptual similarity | < 0.1 |
| FPS | Frames per second | >= 60 |

## Device-Specific Budgets

| Device | Max Gaussians | Recommended |
|--------|--------------|-------------|
| iPhone 15 Pro | 4M | 2-3M |
| iPad Pro M2 | 8M | 5-6M |
| MacBook Pro M3 | 12M | 8-10M |
| Vision Pro | 6M (stereo) | 4M |

## Tools

### analyze_splat.py

Use the included script to analyze your scene:

```bash
python scripts/analyze_splat.py scene.ply --analyze-pruning
```

Output includes:
- Opacity histogram with suggested thresholds
- Size distribution with resolution-based recommendations
- Estimated memory savings per pruning level

## Best Practices

1. **Profile first**: Measure actual performance before pruning
2. **Start conservative**: Begin with minimal pruning, increase as needed
3. **Validate quality**: Check PSNR/SSIM after each pruning pass
4. **Consider use case**: Interactive viewing needs more aggressive pruning than offline rendering
5. **Test on target device**: Desktop results don't always translate to mobile
