---
name: gsplat-optimizer
description: Optimize 3D Gaussian Splat scenes for real-time rendering on iOS, macOS, and visionOS. Use when working with .ply or .splat files, targeting mobile/Apple GPU performance, or needing LOD, pruning, or compression strategies for 3DGS scenes.
---

# Gaussian Splat Optimizer

Optimize 3D Gaussian Splatting scenes for real-time rendering on Apple platforms (iOS, macOS, visionOS) using Metal.

## When to Use

- Optimizing `.ply` or `.splat` files for mobile/Apple GPU targets
- Reducing gaussian count for performance (pruning strategies)
- Implementing Level-of-Detail (LOD) for large scenes
- Compressing splat data for bandwidth/storage constraints
- Profiling and optimizing Metal rendering performance
- Targeting specific FPS goals on Apple hardware

## Quick Start

**Input**: Provide a `.ply`/`.splat` file path, target device class, and FPS target.

```bash
# Analyze a splat file
python ~/.claude/skills/gsplat-optimizer/scripts/analyze_splat.py scene.ply --device iphone --fps 60
```

**Output**: The skill provides:
1. Point/gaussian pruning plan (opacity, size, error thresholds)
2. LOD scheme suggestion (distance bins, gaussian subsets)
3. Compression recommendation (if bandwidth/storage bound)
4. Metal profiling checklist with shader/compute tips

## Optimization Workflow

### Step 1: Analyze the Scene

First, understand your scene characteristics:
- **Gaussian count**: Total number of splats
- **Opacity distribution**: Histogram of opacity values
- **Size distribution**: Gaussian scale statistics
- **Memory footprint**: Estimated GPU memory usage

### Step 2: Determine Target Device

| Device Class | GPU Budget | Max Gaussians (60fps) | Storage Mode |
|-------------|-----------|----------------------|--------------|
| iPhone (A15+) | 4-6GB unified | ~2-4M | Shared |
| iPad Pro (M1+) | 8-16GB unified | ~6-8M | Shared |
| Mac (M1-M3) | 8-24GB unified | ~8-12M | Shared/Managed |
| Vision Pro | 16GB unified | ~4-6M (stereo) | Shared |
| Mac (discrete GPU) | 8-24GB VRAM | ~10-15M | Private |

### Step 3: Apply Pruning

If gaussian count exceeds device budget:

1. **Opacity threshold**: Remove gaussians with opacity < 0.01-0.05
2. **Size culling**: Remove sub-pixel gaussians (< 1px at target resolution)
3. **Importance pruning**: Use LODGE algorithm for error-proxy selection
4. **Foveated rendering**: For Vision Pro, reduce density in peripheral view

See [references/pruning-strategies.md](references/pruning-strategies.md) for details.

### Step 4: Implement LOD (Large Scenes)

For scenes exceeding single-frame budget:

1. **Distance bins**: Near (0-10m), Mid (10-50m), Far (50m+)
2. **Hierarchical structure**: Octree or LoD tree for spatial queries
3. **Chunk streaming**: Load/unload based on camera position
4. **Smooth transitions**: Opacity blending at chunk boundaries

See [references/lod-schemes.md](references/lod-schemes.md) for details.

### Step 5: Apply Compression (If Needed)

For bandwidth/storage constraints:

| Method | Compression | Use Case |
|--------|-------------|----------|
| SOGS | 20x | Web delivery, moderate quality |
| SOG | 24x | Web delivery, better quality |
| CodecGS | 30x+ | Maximum compression |
| C3DGS | 31x | Fast rendering priority |

See [references/compression.md](references/compression.md) for details.

### Step 6: Profile and Optimize Metal

1. **Choose storage mode**: Private for static data, Shared for dynamic
2. **Optimize shaders**: Function constants, thread occupancy
3. **Profile with Xcode**: GPU Frame Capture, Metal System Trace
4. **Iterate**: Measure, optimize, repeat

See [references/metal-profiling.md](references/metal-profiling.md) for details.

## Common Pitfalls

### 1. Point Cloud Density Mismatch

**Problem:** Gaussian count doesn't match your scene complexity, causing either visual artifacts or wasted GPU resources.

- **Too sparse (undersampling):** Visible gaps, blockiness, loss of fine details
- **Too dense (oversampling):** Exceeds device budget, causes frame drops, GPU thrashing

**Debugging:**
```bash
# Analyze gaussian distribution
python ~/.claude/skills/gsplat-optimizer/scripts/analyze_splat.py scene.ply --histogram

# Check against device budget
# Compare total_gaussians vs. device_max in the output table
```

**Strategy:**
- Start with device budget from Step 2 (e.g., 4M for iPhone)
- If scene exceeds budget by >20%, apply pruning before training
- If visual quality drops too much after pruning, consider LOD or chunking
- Use importance-weighted sampling (LODGE) to remove low-contribution gaussians, not just opaque ones

---

### 2. Training Instability (Gradient Explosions, Divergence)

**Problem:** During optimization (if fine-tuning on device), gaussian parameters diverge, causing:
- Loss suddenly jumps to NaN
- Gaussians disappear or explode in scale
- Model becomes unrecoverable mid-session

**Debugging:**
```bash
# Monitor loss during training
tail -f training.log | grep -E "loss|nan|inf"

# Check gradient magnitudes
python -c "
import numpy as np
from plyfile import PlyData
ply_data = PlyData.read('scene.ply')
scales = ply_data['vertex']['scale_0'].data
print(f'Scale range: {scales.min():.6f} to {scales.max():.6f}')
print(f'Any NaN: {np.isnan(scales).any()}')
"
```

**Strategy:**
- **Gradient clipping:** Cap gradient updates to ±0.1 scale per step
- **Learning rate decay:** Start at 1e-4, decay by 0.95 every epoch
- **Loss regularization:** Add L2 penalty on scale magnitudes to prevent explosions
- **Checkpoint early:** Save state every 10 iterations; rollback if loss spikes
- **Freeze covariance:** If converged, stop updating scale/rotation after 80% of training
- **For device training:** Reduce batch size or resolution if instability persists

---

### 3. Memory Limitations (OOM Errors on Large Scenes)

**Problem:** Scene exceeds available unified memory, causing allocation failures or GPU stalls.

- iPhone: 4–6GB shared between app + GPU
- iPad Pro: 8–16GB shared
- Vision Pro: 16GB (but stereo doubles gaussian count)

**Debugging:**
```bash
# Estimate memory footprint
python << 'EOF'
num_gaussians = 5_000_000  # Your count
bytes_per_gaussian = 56  # pos (12) + scale (12) + rot quaternion (16) + opacity (4) + SH DC (12)
total_mb = (num_gaussians * bytes_per_gaussian) / (1024 ** 2)
print(f"Est. memory: {total_mb:.1f} MB")
print(f"Safe for iPhone A15: {total_mb < 2000}")  # Leave headroom for app
EOF

# Monitor live memory in Xcode
# Memory graph + Allocations instrument during scene load
```

**Strategy:**
- **Chunking for large scenes:** Break into 1–4M gaussian chunks, stream based on camera distance
- **Quantization:** Store gaussians in FP16 instead of FP32 (2x memory reduction)
- **Pruning first:** Remove <0.01 opacity or sub-pixel gaussians before transfer to device
- **Lazy loading:** Keep only active LOD level in memory; unload far chunks
- **Vision Pro consideration:** Dual-eye rendering = 2x gaussian count; cap at 4M per eye

---

### 4. Quality/Speed Trade-Offs (Over-Optimization for One Metric)

**Problem:** Optimizing heavily for one metric breaks another:
- **Maximize FPS → visual artifacts:** Over-pruning removes important geometry
- **Maximize quality → frame drops:** Too many gaussians for target device
- **Minimize memory → banding/posterization:** Excessive quantization or LOD culling

**Debugging:**
```bash
# Profile before/after each change
python << 'EOF'
metrics = {
  "original": {"fps": 60, "gaussians": 5_000_000, "artifacts": "none"},
  "after_pruning": {"fps": 58, "gaussians": 3_500_000, "artifacts": "block edges visible"},
}
for label, m in metrics.items():
    print(f"{label}: {m['fps']}fps, {m['gaussians']/1e6:.1f}M, {m['artifacts']}")
EOF
```

**Strategy:**
- **Define priority:** Is this device speed-critical (AR, real-time) or quality-focused (preview)?
- **Measure baseline:** Profile original unoptimized scene first
- **Iterate incrementally:** Apply one optimization (pruning OR compression OR LOD), measure, decide
- **Preserve quality metrics:** Keep PSNR/SSIM scores; stop pruning if quality drops >1dB
- **Target range:** Aim for 50–60fps headroom (don't max out at exactly 60fps; device will throttle)

---

### 5. Real-Time Rendering Failures (Frame Drops, Shader Compilation)

**Problem:** Rendering pipeline stalls despite low gaussian count:
- First frame (cold start): 2–5s delay while shaders compile
- Mid-scene: Frame drops spike when new LOD levels load
- Smooth playback → stuttering after 30–60s

**Debugging:**
```bash
# Capture Metal frame statistics
# In Xcode: Product > Scheme > Edit > Run > Diagnostics
# Enable: Metal API Validation, GPU Frame Capture

# Check shader compilation time
python ~/.claude/skills/gsplat-optimizer/scripts/metal_profile.py \
  --capture-shader-compile \
  --target iphone14

# Monitor frame time distribution
tail -f xcode.log | grep -E "frame_time|stutter"
```

**Strategy:**
- **Pre-warm shader cache:** Compile all function variants on first load (avoid runtime jank)
- **Limit LOD transitions:** If using multiple LOD levels, cap transitions to 2 per frame
- **Asynchronous streaming:** Load new geometry chunks on background thread, upload in-between frames
- **Device-specific tuning:** 
  - iPhone: Keep draw calls < 50, geometry per call < 500K gaussians
  - Mac: More generous; aim for < 2M gaussians per draw call
  - Vision Pro: Account for stereo; effective capacity is half the budget
- **Profile regimen:** Run Metal System Trace before and after each optimization; track:
  - GPU utilization (target 70–85%)
  - Shader time (target <10ms)
  - Memory bandwidth (target <50GB/s)

---

## Key Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Frame time | 16.6ms (60fps) | Metal System Trace |
| GPU memory | < device budget | Xcode Memory Graph |
| Bandwidth | < 50GB/s | GPU Counters |
| Shader time | < 10ms | GPU Frame Capture |

## Reference Implementation

**MetalSplatter** is the primary reference for Swift/Metal gaussian splatting:
- Repository: https://github.com/scier/MetalSplatter
- Supports iOS, macOS, visionOS
- ~8M splat capacity with v1.1 optimizations
- Stereo rendering for Vision Pro

### Getting Started with MetalSplatter

```bash
git clone https://github.com/scier/MetalSplatter.git
cd MetalSplatter
open SampleApp/MetalSplatter_SampleApp.xcodeproj
# Set to Release scheme for best performance
```

## Resources

### Reference Documentation
- [Pruning Strategies](references/pruning-strategies.md) - Gaussian reduction techniques
- [LOD Schemes](references/lod-schemes.md) - Level-of-detail approaches
- [Compression](references/compression.md) - Bandwidth/storage optimization
- [Metal Profiling](references/metal-profiling.md) - Apple GPU optimization

### Research Papers
- [LODGE](https://arxiv.org/abs/2505.23158) - LOD for large-scale scenes
- [FLoD](https://arxiv.org/abs/2408.12894) - Flexible LOD for variable hardware
- [Voyager](https://arxiv.org/html/2506.02774v2) - City-scale mobile rendering
- [3DGS Compression Survey](https://w-m.github.io/3dgs-compression-survey/)

### Apple Developer Resources
- [Metal Best Practices Guide](https://developer.apple.com/library/archive/documentation/3DDrawing/Conceptual/MTLBestPracticesGuide/)
- [Metal Shader Performance (Tech Talk)](https://developer.apple.com/videos/play/tech-talks/111373/)
- [Optimize GPU Renderers (WWDC23)](https://developer.apple.com/videos/play/wwdc2023/10127/)
