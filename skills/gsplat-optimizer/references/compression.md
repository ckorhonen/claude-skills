# Gaussian Splat Compression

Techniques for reducing file size and bandwidth requirements for 3D Gaussian Splat data.

## Overview

Compression is essential when:
- Delivering splats over mobile networks
- Fitting within iOS app size limits
- Streaming large scenes on demand
- Reducing initial load times

## Compression Methods

### 1. SOGS (Self-Organizing Gaussians)

**Compression ratio:** ~20x (1GB PLY -> 55MB)

**How it works:**
1. Reshape gaussian attributes into 2D "attribute images"
   - X positions form one image
   - Y positions another
   - Each SH coefficient its own image (59+ images total)

2. Sort gaussians by primary attributes (position, scale, color)
   - Similar gaussians become spatially adjacent
   - Creates smooth attribute images

3. Apply WebP compression to each attribute image
   - Standard browser decoding
   - Fast, hardware-accelerated

**Example:**
```
4M gaussians @ 1GB PLY
    |
    v
SOGS encoding
    |
    v
55MB compressed (WebP images)
```

**Reference:** [PlayCanvas Blog](https://blog.playcanvas.com/playcanvas-adopts-sogs-for-20x-3dgs-compression/)

### 2. SOG (Spatially Ordered Gaussians)

**Compression ratio:** ~24x (1GB PLY -> 42MB)

Improved version of SOGS:
- Better spatial ordering algorithm
- Higher quality at same compression
- ~95% file size reduction

**Reference:** [PlayCanvas SOG](https://github.com/playcanvas/sogs)

### 3. CodecGS

**Compression ratio:** 30x+

Uses video codec infrastructure:

1. **Tri-plane representation**: Store features in 2D planes
2. **HEVC encoding**: Leverage hardware video decoders
3. **Progressive training**: Optimize channel importance

**Key features:**
- Frequency-domain entropy modeling
- Channel importance bit allocation
- Hardware decoder support

**Reference:** [CodecGS](https://fraunhoferhhi.github.io/CodecGS/)

### 4. C3DGS (Compressed 3D Gaussian Splatting)

**Compression ratio:** 31x with 4x faster rendering

**Approach:**
1. Sensitivity-aware vector clustering
2. Quantization-aware training
3. Learned codebooks

**Benefits:**
- Minimal quality degradation
- Hardware rasterization support
- Faster rendering on lightweight GPUs

**Reference:** [C3DGS](https://github.com/KeKsBoTer/c3dgs)

### 5. CompGS

**Compression ratio:** 10-20x

**Approach:**
- K-Means quantization on covariance and color
- Replace values with codebook entries
- Simple implementation

**Best for:** Quick compression with acceptable quality

**Reference:** [CompGS](https://github.com/UCDvision/compact3d)

## Comparison

| Method | Compression | Quality | Decode Speed | iOS Support |
|--------|-------------|---------|--------------|-------------|
| SOGS | 20x | Good | Fast (WebP) | Yes |
| SOG | 24x | Better | Fast (WebP) | Yes |
| CodecGS | 30x+ | Good | Fast (HEVC) | Yes |
| C3DGS | 31x | Good | Very Fast | Yes |
| CompGS | 10-20x | Acceptable | Medium | Yes |

## Spherical Harmonics Compression

SH coefficients are major contributors to file size.

### Strategies:

1. **Reduce SH degree**: Use degree 1 instead of 3
   - 4 coefficients vs 16 per color channel
   - 75% reduction in SH data
   - Acceptable for diffuse-dominant scenes

2. **Quantize SH coefficients**:
   - 16-bit -> 8-bit: 50% reduction
   - Use per-channel scale factors

3. **PCA compression**:
   - Project SH to principal components
   - Keep top k components

```python
# Example: reduce SH degree
def reduce_sh_degree(sh_coeffs, target_degree=1):
    # SH degree 3 has 16 coeffs per channel
    # SH degree 1 has 4 coeffs per channel
    coeffs_per_channel = (target_degree + 1) ** 2
    return sh_coeffs[:, :coeffs_per_channel * 3]
```

## Position Quantization

### Fixed-point encoding

```python
# Quantize positions to 16-bit
def quantize_positions(positions, bbox):
    normalized = (positions - bbox.min) / (bbox.max - bbox.min)
    quantized = (normalized * 65535).astype(np.uint16)
    return quantized, bbox
```

### Octree-based encoding

- Store positions relative to octree cell
- Higher precision for smaller cells
- Adaptive based on gaussian density

## When to Use Compression

### Use compression when:
- Delivering over mobile networks (3G/4G/5G)
- iOS app size limits (< 200MB for cellular download)
- Streaming on-demand content
- Initial page load is critical

### Skip compression when:
- Local file loading (direct PLY is fine)
- Development/debugging
- Maximum quality required
- One-time transfer over fast network

## iOS-Specific Considerations

### App Store Limits
- 200MB: Maximum cellular download size
- 4GB: Maximum app bundle size
- Consider on-demand resources for large scenes

### Network Conditions
- Test on throttled connections
- Consider progressive loading
- Provide quality options

### Memory Pressure
- Decompression requires temporary memory
- Monitor memory warnings
- Stream large scenes in chunks

## Implementation Checklist

- [ ] Measure original file size and load time
- [ ] Choose compression method based on use case
- [ ] Test quality metrics (PSNR, SSIM)
- [ ] Measure decode time on target devices
- [ ] Verify memory usage during decompression
- [ ] Test on slow network conditions
- [ ] Implement progressive loading if needed

## Tools

### SOGS/SOG
```bash
pip install sogs
sogs compress input.ply output.sog --quality medium
```

### analyze_splat.py
```bash
python scripts/analyze_splat.py scene.ply --compression-analysis
```

Output:
- Current file size
- Estimated compressed sizes for each method
- Recommended compression based on target device
