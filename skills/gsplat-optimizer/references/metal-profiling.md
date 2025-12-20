# Metal Profiling and Optimization

Apple-specific GPU optimization for gaussian splatting on iOS, macOS, and visionOS.

## Storage Modes

Choose the right storage mode for your gaussian data.

### MTLStorageModeShared

**When to use:** Small per-frame data, CPU-GPU shared access

```swift
let buffer = device.makeBuffer(length: size, options: .storageModeShared)
```

- Default on all Apple platforms
- CPU and GPU share system memory
- Good for: uniform buffers, small dynamic data
- Overhead: GPU must fetch from system memory

### MTLStorageModePrivate

**When to use:** Static gaussian data, GPU-only access

```swift
// Create staging buffer
let staging = device.makeBuffer(length: size, options: .storageModeShared)
staging.contents().copyBytes(from: data)

// Create private buffer
let gpuBuffer = device.makeBuffer(length: size, options: .storageModePrivate)

// Blit data to private buffer (one-time cost)
let blitEncoder = commandBuffer.makeBlitCommandEncoder()
blitEncoder.copy(from: staging, to: gpuBuffer)
blitEncoder.endEncoding()
```

- GPU-only, video memory on discrete GPUs
- Optimal for static gaussian position/SH data
- One-time blit from shared -> private

### MTLStorageModeManaged (macOS only)

**When to use:** Medium-sized data that changes occasionally

```swift
let buffer = device.makeBuffer(length: size, options: .storageModeManaged)

// After CPU modification:
buffer.didModifyRange(0..<size)
```

- Explicit CPU-GPU synchronization
- Good for: LOD data, occasional updates
- Requires `didModifyRange()` after CPU writes

## Profiling Tools

### 1. GPU Frame Capture (Xcode)

**How to use:**
1. Click camera button in Xcode debug bar
2. Or use `MTLCaptureManager` in code

```swift
let captureManager = MTLCaptureManager.shared()
let captureDescriptor = MTLCaptureDescriptor()
captureDescriptor.captureObject = device
try captureManager.startCapture(with: captureDescriptor)
// ... render frame ...
captureManager.stopCapture()
```

**What to look for:**
- Per-draw call timing
- Shader execution time
- Memory bandwidth usage
- Pipeline state switches

### 2. Metal System Trace (Instruments)

**When to use:** Timeline analysis, stutters, dropped frames

**Key tracks:**
- GPU: Vertex, Fragment, Compute
- Display: VSync, frame presentation
- CPU: Encoding time

**What to look for:**
- GPU idle time (CPU bottleneck)
- Long frame times
- Memory pressure events
- Thermal throttling

### 3. GPU Counters API (iOS 14+, macOS Big Sur+)

Runtime profiling without Xcode:

```swift
let counterSampleBuffer = device.makeCounterSampleBuffer(descriptor: descriptor)

// In render loop:
commandBuffer.sampleCounters(sampleBuffer: counterSampleBuffer, at: .atStageBoundary)

// Read results:
let data = counterSampleBuffer.resolveCounterRange(0..<counterCount)
```

**Key counters:**
- `totalCycles`: GPU time
- `vertexInvocations`: Vertex shader calls
- `fragmentInvocations`: Fragment shader calls
- `computeKernelInvocations`: Compute dispatches

### 4. GPU Timeline (Apple GPUs)

**Specific to Apple Silicon:**
- Visualizes TBDR (Tile-Based Deferred Rendering)
- Shows vertex/fragment/compute overlap
- Identifies tile memory pressure

## Shader Optimization

### Function Constants

Specialize shaders at compile time:

```metal
constant bool USE_SH_DEGREE_1 [[function_constant(0)]];
constant bool ENABLE_CULLING [[function_constant(1)]];

fragment float4 gaussianFragment(...) {
    if (USE_SH_DEGREE_1) {
        // Simplified SH evaluation
    } else {
        // Full SH evaluation
    }
}
```

```swift
let constants = MTLFunctionConstantValues()
constants.setConstantValue(&useSHDegree1, type: .bool, index: 0)
let function = try library.makeFunction(name: "gaussianFragment", constantValues: constants)
```

### Function Groups

Optimize indirect function calls:

```metal
[[visible]]
void gaussianKernel(...) [[function_groups("gaussian_ops")]] {
    // Kernel implementation
}
```

### Thread Occupancy

Maximize parallelism:

```metal
// Use appropriate threadgroup size
kernel void processGaussians(
    device GaussianData* gaussians [[buffer(0)]],
    uint id [[thread_position_in_grid]],
    uint localId [[thread_position_in_threadgroup]]
) {
    // 256 threads per threadgroup is often optimal
}
```

```swift
// Dispatch with optimal threadgroup size
let threadsPerGroup = MTLSize(width: 256, height: 1, depth: 1)
let numGroups = MTLSize(width: (gaussianCount + 255) / 256, height: 1, depth: 1)
encoder.dispatchThreadgroups(numGroups, threadsPerThreadgroup: threadsPerGroup)
```

### Address Space Selection

Choose correct address space for memory objects:

```metal
// device: Large arrays, random access
device float4* positions [[buffer(0)]];

// constant: Small, read-only, broadcast to all threads
constant Uniforms& uniforms [[buffer(1)]];

// threadgroup: Shared within threadgroup, fast
threadgroup float sharedData[256];
```

## Buffer Best Practices

### Single Buffer with Offsets

```swift
// DON'T: One buffer per draw
for gaussian in gaussians {
    let buffer = device.makeBuffer(bytes: gaussian.data, ...)
    encoder.setVertexBuffer(buffer, offset: 0, index: 0)
    encoder.draw(...)
}

// DO: Single buffer, incrementing offsets
let megaBuffer = device.makeBuffer(length: totalSize, ...)
var offset = 0
for gaussian in gaussians {
    megaBuffer.contents().advanced(by: offset).copyBytes(from: gaussian.data)
    encoder.setVertexBuffer(megaBuffer, offset: offset, index: 0)
    encoder.draw(...)
    offset += gaussian.dataSize
}
```

### Alignment for No-Copy

```swift
// Align to 4096 bytes for no-copy buffer creation
let alignment = 4096
let alignedSize = ((dataSize + alignment - 1) / alignment) * alignment
let buffer = device.makeBuffer(bytesNoCopy: alignedPointer, length: alignedSize, ...)
```

### Concurrent Compilation

```swift
// Enable on macOS 13.3+
device.shouldMaximizeConcurrentCompilation = true
```

## Texture Usage

Always declare explicit usage:

```swift
// DON'T
textureDescriptor.usage = .unknown  // Performance cost!

// DO
textureDescriptor.usage = [.shaderRead, .renderTarget]
```

## MetalSplatter-Specific Tips

1. **Use Release scheme**: Debug is 10x+ slower for large files
2. **Stereo amplification**: Vision Pro uses vertex amplification
3. **PLYIO module**: Standalone PLY parsing, use for preprocessing
4. **Memory**: v1.1 supports ~8M splats with 50% memory reduction

## WWDC References

- [Metal Shader Performance (Tech Talk)](https://developer.apple.com/videos/play/tech-talks/111373/)
- [Optimize GPU Renderers (WWDC23)](https://developer.apple.com/videos/play/wwdc2023/10127/)
- [ML Acceleration with Metal (WWDC24)](https://developer.apple.com/videos/play/wwdc2024/10218/)
- [Metal Debugging & Profiling (WWDC21)](https://developer.apple.com/videos/play/wwdc2021/10157/)
- [Gain Insights with Xcode 12 (WWDC20)](https://developer.apple.com/videos/play/wwdc2020/10605/)
- [Metal Game Performance (WWDC18)](https://developer.apple.com/videos/play/wwdc2018/612/)

## Profiling Checklist

- [ ] Profile in Release mode (not Debug)
- [ ] Capture GPU frame with Xcode
- [ ] Check shader execution time (target < 10ms)
- [ ] Verify storage modes are optimal
- [ ] Monitor memory bandwidth (< 50GB/s)
- [ ] Check thread occupancy
- [ ] Test on actual target device
- [ ] Monitor thermal state
- [ ] Profile memory usage over time

## Common Bottlenecks

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| Low FPS, GPU idle | CPU bottleneck | Reduce draw calls, use instancing |
| Low FPS, GPU busy | Shader bottleneck | Simplify shaders, reduce SH degree |
| Stutters | Memory pressure | Reduce gaussian count, use LOD |
| Thermal throttling | Sustained load | Reduce quality, add frame pacing |
| Slow initial load | Large file | Use compression, stream chunks |
