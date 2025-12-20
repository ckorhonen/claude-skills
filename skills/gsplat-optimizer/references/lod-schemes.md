# Level-of-Detail (LOD) Schemes

Techniques for rendering large gaussian splat scenes by dynamically selecting gaussian subsets based on view distance and device capabilities.

## Overview

LOD enables rendering of scenes that exceed single-frame GPU budgets by:
- Loading only nearby high-detail regions
- Using coarser representations for distant areas
- Streaming content based on camera position

## LOD Approaches

### 1. LODGE (Hierarchical LOD)

LODGE creates a hierarchical representation for large-scale scenes.

**Key concepts:**
- Depth-aware 3D smoothing filter for LOD level construction
- Importance-based pruning at each level
- Fine-tuning to maintain visual fidelity

**LOD levels:**
| Level | Distance | Gaussian Density | Quality |
|-------|----------|-----------------|---------|
| L0 | 0-10m | 100% | Full detail |
| L1 | 10-30m | 50% | High |
| L2 | 30-100m | 25% | Medium |
| L3 | 100m+ | 10% | Low |

**Implementation:**
```python
def select_lod_level(distance, device_budget):
    if distance < 10:
        return LOD_FULL
    elif distance < 30:
        return LOD_HIGH
    elif distance < 100:
        return LOD_MEDIUM
    else:
        return LOD_LOW
```

**Reference:** [LODGE](https://arxiv.org/abs/2505.23158)

### 2. FLoD (Flexible Level of Detail)

FLoD constructs multi-level representations with level-specific 3D scale constraints.

**Key features:**
- Each level independently reconstructs the entire scene
- Scales from 2GB laptop GPU to 24GB server GPU
- Trade-off between quality and memory usage

**Memory scaling:**
| Level | VRAM | Quality |
|-------|------|---------|
| L1 | 2GB | Acceptable |
| L2 | 4GB | Good |
| L3 | 8GB | High |
| L4 | 16GB | Full |

**Reference:** [FLoD](https://arxiv.org/abs/2408.12894)

### 3. HierarchicalGS (Tree Structure)

Used in Voyager for city-scale rendering.

**Structure:**
- Gaussians stored in LoD tree
- Each tree level represents specific detail granularity
- Efficient frustum queries via tree traversal

**Benefits:**
- Fast view-dependent selection
- Memory-efficient streaming
- Scalable to city-scale scenes

**Reference:** [Voyager](https://arxiv.org/html/2506.02774v2)

### 4. Continuous LOD (CLOD)

Importance-ordered splats for arbitrary count rendering.

**Approach:**
- Learn to order splats by importance
- Render arbitrary splat count based on budget
- No discrete LOD transitions

**Use cases:**
- Adaptive quality based on frame budget
- Foveated rendering integration
- Budget-based rendering

## Chunk-Based Streaming

For scenes too large to fit in memory:

### Spatial Partitioning

```
Scene Grid (e.g., 100m x 100m chunks)
+---+---+---+---+
| A | B | C | D |
+---+---+---+---+
| E | F | G | H |
+---+---+---+---+
| I | J | K | L |
+---+---+---+---+
```

### Loading Strategy

1. **Active chunks**: Fully loaded (camera position +/- 1 chunk)
2. **Preload chunks**: Background loading (+/- 2 chunks)
3. **Unload chunks**: Free memory (> 3 chunks away)

### Boundary Handling

Use opacity blending to avoid visible seams:

```python
def blend_chunk_boundary(gaussian, chunk_center, blend_distance=5.0):
    dist_to_boundary = distance_to_chunk_edge(gaussian.position)
    if dist_to_boundary < blend_distance:
        # Fade out near boundaries
        gaussian.opacity *= dist_to_boundary / blend_distance
```

## Memory Budget Allocation

### Per-Level Budgets

```
Total Budget: 6GB (Vision Pro)
+-- L0 (Full detail): 2GB
+-- L1 (High): 2GB
+-- L2 (Medium): 1.5GB
+-- L3 (Low): 0.5GB
```

### Dynamic Adjustment

Adjust LOD based on real-time performance:

```python
def adjust_lod_thresholds(current_fps, target_fps):
    if current_fps < target_fps * 0.9:
        # Reduce quality to improve performance
        increase_lod_distances()
    elif current_fps > target_fps * 1.1:
        # Increase quality if headroom available
        decrease_lod_distances()
```

## Apple Platform Considerations

### iOS/iPhone

- Limited thermal envelope
- Start with aggressive LOD thresholds
- Monitor thermal state via `ProcessInfo.thermalState`

### Vision Pro

- Stereo rendering (2x workload)
- Use foveated LOD with eye tracking
- Balance between eyes for smooth experience

### macOS

- More thermal headroom
- Can use finer LOD granularity
- Leverage Metal 4 features

## Implementation Checklist

- [ ] Partition scene into spatial chunks
- [ ] Create LOD levels for each chunk
- [ ] Implement distance-based LOD selection
- [ ] Add chunk streaming with preloading
- [ ] Blend boundaries to avoid seams
- [ ] Test on target devices
- [ ] Profile memory and performance
- [ ] Add dynamic LOD adjustment

## Best Practices

1. **Pre-compute LOD offline**: Generate LOD levels during asset processing
2. **Use octree for queries**: O(log n) frustum culling
3. **Async loading**: Don't block render thread for chunk loading
4. **Cache recently used**: Keep warm cache of recent chunks
5. **Profile on device**: Desktop performance != mobile performance
