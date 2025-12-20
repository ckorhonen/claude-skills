# Neural Engine Optimization Guide

## Understanding Apple's Neural Engine

The Apple Neural Engine (ANE) is a dedicated ML accelerator in Apple Silicon chips:

| Chip | ANE TOPS | First Available |
|------|----------|-----------------|
| A11 | ~0.6 | iPhone 8 (2017) |
| A12 | ~5 | iPhone XS (2018) |
| A14 | ~11 | iPhone 12 (2020) |
| A15 | ~15.8 | iPhone 13 (2021) |
| A16 | ~17 | iPhone 14 Pro (2022) |
| A17 Pro | ~35 | iPhone 15 Pro (2023) |
| M1 | ~11 | Mac M1 (2020) |
| M2 | ~15.8 | Mac M2 (2022) |
| M3 | ~18 | Mac M3 (2023) |
| M4 | ~38 | iPad Pro M4 (2024) |

## Compute Unit Selection

### Configuration Options

```swift
import CoreML

let config = MLModelConfiguration()

// Let runtime choose (recommended for production)
config.computeUnits = .all

// CPU + Neural Engine (skip GPU)
config.computeUnits = .cpuAndNeuralEngine

// CPU + GPU (skip Neural Engine)
config.computeUnits = .cpuAndGPU

// CPU only (for debugging)
config.computeUnits = .cpuOnly
```

### Python Conversion Options

```python
import coremltools as ct

mlmodel = ct.convert(
    model,
    compute_units=ct.ComputeUnit.ALL,  # Default
    # or ct.ComputeUnit.CPU_AND_NE
    # or ct.ComputeUnit.CPU_AND_GPU
    # or ct.ComputeUnit.CPU_ONLY
)
```

## Querying Device Capabilities (iOS 17+)

Use the official `MLComputeDevice` API to inspect available hardware:

```swift
import CoreML

// Get all compute devices
let devices = MLComputeDevice.allComputeDevices

for device in devices {
    switch device {
    case .cpu(let cpuDevice):
        print("CPU: Available")

    case .gpu(let gpuDevice):
        print("GPU: Available (Metal device)")

    case .neuralEngine(let neDevice):
        print("Neural Engine: Available")
        print("  Total cores: \(neDevice.totalCoreCount)")

    @unknown default:
        break
    }
}
```

The `MLNeuralEngineComputeDevice.totalCoreCount` property returns the number of Neural Engine cores available on the device.

## Pre-Execution Analysis with MLComputePlan (iOS 17.4+)

Analyze which compute unit will execute each operation without running inference:

```swift
import CoreML

// Load compute plan
let config = MLModelConfiguration()
config.computeUnits = .all

let plan = try await MLComputePlan.load(
    contentsOf: modelURL,
    configuration: config
)

// Iterate through operations
let mainFunction = plan.modelStructure.mainFunction
for operation in mainFunction.operations {
    print("Operation: \(operation.name) (\(operation.type))")

    // Check which device will run this operation
    if let deviceUsage = plan.deviceUsage(for: operation) {
        print("  Runs on: \(deviceUsage)")
    }

    // Get estimated cost
    if let cost = plan.estimatedCost(of: operation) {
        print("  Estimated cost: \(cost)")
    }
}
```

This is invaluable for identifying operations that fall back to CPU/GPU before deploying.

## Detecting Neural Engine Usage

### Method 1: Performance Comparison

```swift
func compareComputeUnits(modelURL: URL) throws {
    let iterations = 100

    let configs: [(String, MLComputeUnits)] = [
        ("All (ANE+GPU+CPU)", .all),
        ("CPU+GPU", .cpuAndGPU),
        ("CPU+NE", .cpuAndNeuralEngine),
        ("CPU Only", .cpuOnly)
    ]

    for (name, units) in configs {
        let config = MLModelConfiguration()
        config.computeUnits = units

        let model = try MLModel(contentsOf: modelURL, configuration: config)
        let input = createDummyInput()

        // Warm up
        for _ in 0..<10 { _ = try? model.prediction(from: input) }

        // Benchmark
        let start = CFAbsoluteTimeGetCurrent()
        for _ in 0..<iterations {
            _ = try model.prediction(from: input)
        }
        let avgMs = (CFAbsoluteTimeGetCurrent() - start) / Double(iterations) * 1000

        print("\(name): \(String(format: "%.2f", avgMs))ms")
    }
}
```

**Interpretation:**
- If `.all` is much faster than `.cpuAndGPU` → ANE is being used effectively
- If similar performance → ANE may not be used or only partially

### Method 2: Thread Inspection (Debugger)

1. Run app and pause during inference
2. Look for thread named `H11ANEServicesThread`
3. If present, Neural Engine is active

### Method 3: Symbolic Breakpoints

```
# Set breakpoints in Xcode for:
-[_ANEModel program]                           # ANE usage
Espresso::MPSEngine::context::__launch_kernel  # GPU usage
Espresso::BNNSEngine::convolution_kernel       # CPU usage
```

### Method 4: Core ML Instruments

1. Xcode > Product > Profile (Cmd+I)
2. Select "Core ML" template
3. Run and observe:
   - Compute lane shows ANE/GPU/CPU usage per layer
   - Filled checkmark = executed on that unit
   - Empty checkmark = supported but not chosen
   - Empty diamond = not supported

## Supported Operations

### Fully Supported (Run on ANE)

| Category | Operations |
|----------|-----------|
| Convolution | conv, depthwise_conv, transpose_conv |
| Pooling | max_pool, avg_pool, global_avg_pool |
| Normalization | batch_norm, instance_norm, layer_norm |
| Activation | relu, leaky_relu, sigmoid, tanh, gelu, swish |
| Element-wise | add, mul, sub, div, maximum, minimum |
| Linear | linear (matmul), inner_product |
| Reshape | reshape, transpose, concat, split, slice |

### Partially Supported (May Fall Back)

| Operation | Condition |
|-----------|-----------|
| Softmax | Large axis dimensions may use GPU |
| Reduce | Depends on axes and tensor size |
| Resize | Some modes (bilinear OK, bicubic may fallback) |
| Non-max suppression | Custom implementation recommended |

### Not Supported (Fall Back to CPU/GPU)

- Dynamic shapes (tensor size not known at compile time)
- TopK, ArgMax, ArgMin
- Scatter, Gather, GatherND
- Custom layers without ANE kernel
- Very large tensors (>4096 in any dimension)
- Certain advanced attention patterns

## Optimization Hints (iOS 17.4+)

Use `MLOptimizationHints` to guide Core ML's optimization strategy:

### ReshapeFrequency

Controls how the runtime handles input shape changes:

```swift
let config = MLModelConfiguration()

// Default: Optimized for variable shapes
config.optimizationHints.reshapeFrequency = .frequent
// - Minimizes latency when shapes change
// - Individual predictions may be slightly slower
// - Shape transitions are fast

// Alternative: Optimized for stable shapes
config.optimizationHints.reshapeFrequency = .infrequent
// - Re-optimizes engine when shape changes (initial delay)
// - Faster subsequent predictions for that shape
// - Use when input shapes rarely change
```

**Recommendation:**
- Use `.frequent` (default) for real-time applications with varying input sizes
- Use `.infrequent` when processing batches at fixed resolutions

### SpecializationStrategy

Controls model specialization behavior:

```swift
config.optimizationHints.specializationStrategy = .default     // Balanced
config.optimizationHints.specializationStrategy = .fastPrediction  // Prioritize speed
```

## Optimizing for Neural Engine

### 1. Use Fixed Tensor Shapes

```python
# Good: Fixed shape
ct.TensorType(shape=(1, 3, 224, 224))

# Acceptable: Enumerated shapes
ct.EnumeratedShapes(shapes=[
    (1, 3, 224, 224),
    (1, 3, 512, 512)
])

# May prevent ANE: Dynamic shapes
ct.Shape(shape=(1, 3, ct.RangeDim(1, 2048), ct.RangeDim(1, 2048)))
```

### 2. Optimize Channel Counts

```python
# Good: Powers of 2 or multiples of 16
channels = 16, 32, 64, 128, 256

# Less efficient: Odd numbers
channels = 13, 17, 127
```

### 3. Batch Size of 1

```python
# Optimal for on-device inference
ct.TensorType(shape=(1, 3, 224, 224))

# Less efficient for ANE
ct.TensorType(shape=(4, 3, 224, 224))
```

### 4. Use ML Program Format

```python
# Modern format with better ANE support
ct.convert(model, convert_to="mlprogram")

# Legacy format - avoid
ct.convert(model, convert_to="neuralnetwork")
```

### 5. Symmetric Quantization

```python
# Best for ANE
config = cto.coreml.OpLinearQuantizerConfig(
    mode="linear_symmetric",  # Symmetric quantization
    dtype="int8"
)
```

## Replacing Unsupported Operations

### GELU Approximation

```python
# PyTorch GELU (may not be fully ANE optimized)
x = F.gelu(x)

# Approximation using supported ops
def gelu_approx(x):
    return x * 0.5 * (1.0 + torch.tanh(
        0.797885 * (x + 0.044715 * x ** 3)
    ))
```

### SiLU/Swish

```python
# Direct implementation
def silu(x):
    return x * torch.sigmoid(x)  # Both ops supported
```

### Layer Normalization (for older iOS)

```python
# If layer_norm isn't supported on target iOS:
def manual_layer_norm(x, weight, bias, eps=1e-5):
    mean = x.mean(dim=-1, keepdim=True)
    var = x.var(dim=-1, keepdim=True, unbiased=False)
    x = (x - mean) / torch.sqrt(var + eps)
    return weight * x + bias
```

## Performance Debugging Workflow

### Step 1: Establish Baseline

```python
import time
import numpy as np

model = ct.models.MLModel("Model.mlpackage")
input_data = {"input": np.random.rand(1, 3, 224, 224).astype(np.float32)}

# Warm up
for _ in range(10):
    model.predict(input_data)

# Benchmark
times = []
for _ in range(100):
    start = time.time()
    model.predict(input_data)
    times.append((time.time() - start) * 1000)

print(f"Latency: {np.mean(times):.2f} ± {np.std(times):.2f} ms")
```

### Step 2: Check Compute Unit Distribution

Use Xcode Instruments Core ML template:
- Look for layers running on CPU (may indicate unsupported ops)
- Identify layers with high latency
- Note any layers not on expected compute unit

### Step 3: Analyze Model Layers

```python
def analyze_model(model_path):
    model = ct.models.MLModel(model_path)
    spec = model.get_spec()

    if hasattr(spec, 'mlProgram'):
        # ML Program format
        for func in spec.mlProgram.functions:
            for block in func.block_specializations:
                for op in block.operations:
                    print(f"Op: {op.type}, Inputs: {[i.name for i in op.inputs]}")
    else:
        # NeuralNetwork format
        for layer in spec.neuralNetwork.layers:
            layer_type = layer.WhichOneof('layer')
            print(f"Layer: {layer.name}, Type: {layer_type}")
```

### Step 4: Test Alternative Configurations

```swift
// Try different compute unit configurations
for units in [.all, .cpuAndNeuralEngine, .cpuAndGPU] {
    let config = MLModelConfiguration()
    config.computeUnits = units

    // Benchmark and compare
}
```

### Step 5: Profile Full Pipeline

```swift
struct PipelineMetrics {
    var preprocessMs: Double = 0
    var inferenceMs: Double = 0
    var postprocessMs: Double = 0
    var totalMs: Double { preprocessMs + inferenceMs + postprocessMs }
}

func profilePipeline(image: UIImage, model: MLModel) -> PipelineMetrics {
    var metrics = PipelineMetrics()

    let start = CFAbsoluteTimeGetCurrent()

    // Preprocessing
    let preprocessStart = CFAbsoluteTimeGetCurrent()
    let input = preprocessImage(image)
    metrics.preprocessMs = (CFAbsoluteTimeGetCurrent() - preprocessStart) * 1000

    // Inference
    let inferenceStart = CFAbsoluteTimeGetCurrent()
    let output = try! model.prediction(from: input)
    metrics.inferenceMs = (CFAbsoluteTimeGetCurrent() - inferenceStart) * 1000

    // Postprocessing
    let postprocessStart = CFAbsoluteTimeGetCurrent()
    let result = postprocess(output)
    metrics.postprocessMs = (CFAbsoluteTimeGetCurrent() - postprocessStart) * 1000

    return metrics
}
```

## Memory Optimization

### Reduce Peak Memory

```swift
// Async prediction (iOS 17+)
Task {
    let output = try await model.prediction(from: input)
}

// Batch processing with memory management
func processLargeBatch(_ items: [Input]) async throws -> [Output] {
    var results: [Output] = []

    for chunk in items.chunked(into: 10) {
        autoreleasepool {
            for item in chunk {
                let output = try model.prediction(from: item)
                results.append(output)
            }
        }
    }

    return results
}
```

### Model Loading Strategies

```swift
// Lazy loading
class ModelManager {
    private var _model: MLModel?

    var model: MLModel {
        get throws {
            if _model == nil {
                let config = MLModelConfiguration()
                config.computeUnits = .all
                _model = try MLModel(contentsOf: modelURL, configuration: config)
            }
            return _model!
        }
    }

    func unload() {
        _model = nil
    }
}
```

## Thermal Management

### Monitor Thermal State

```swift
import Foundation

func checkThermalState() -> ProcessInfo.ThermalState {
    return ProcessInfo.processInfo.thermalState
}

// Adjust inference based on thermal state
func adaptiveInference(model: MLModel, input: MLFeatureProvider) throws -> MLFeatureProvider {
    switch checkThermalState() {
    case .nominal:
        // Full speed
        return try model.prediction(from: input)

    case .fair:
        // Slight throttling
        try? await Task.sleep(nanoseconds: 10_000_000) // 10ms delay
        return try model.prediction(from: input)

    case .serious, .critical:
        // Significant throttling or skip
        try? await Task.sleep(nanoseconds: 50_000_000) // 50ms delay
        return try model.prediction(from: input)

    @unknown default:
        return try model.prediction(from: input)
    }
}
```

### Sustained Performance Testing

```swift
func stressTest(model: MLModel, duration: TimeInterval = 60) {
    let input = createInput()
    let startTime = Date()
    var iterationCount = 0
    var times: [Double] = []

    while Date().timeIntervalSince(startTime) < duration {
        let start = CFAbsoluteTimeGetCurrent()
        _ = try? model.prediction(from: input)
        times.append((CFAbsoluteTimeGetCurrent() - start) * 1000)
        iterationCount += 1

        // Log every 10 seconds
        if iterationCount % 100 == 0 {
            let recentAvg = times.suffix(100).reduce(0, +) / 100
            print("Iteration \(iterationCount): \(recentAvg)ms, Thermal: \(checkThermalState())")
        }
    }

    // Analyze thermal throttling
    let first10 = Array(times.prefix(100)).reduce(0, +) / 100
    let last10 = Array(times.suffix(100)).reduce(0, +) / 100
    print("Thermal degradation: \((last10 / first10 - 1) * 100)%")
}
```
