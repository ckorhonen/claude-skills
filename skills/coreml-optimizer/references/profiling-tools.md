# CoreML Profiling Tools Reference

## Python Profiling

### Basic Benchmarking

```python
import coremltools as ct
import numpy as np
import time
from typing import Dict, List
import statistics

def benchmark_model(
    model_path: str,
    input_shapes: Dict[str, tuple],
    iterations: int = 100,
    warmup: int = 10
) -> Dict:
    """Comprehensive model benchmarking"""

    model = ct.models.MLModel(model_path)

    # Prepare input
    input_data = {
        name: np.random.rand(*shape).astype(np.float32)
        for name, shape in input_shapes.items()
    }

    # Warm up
    print(f"Warming up ({warmup} iterations)...")
    for _ in range(warmup):
        _ = model.predict(input_data)

    # Benchmark
    print(f"Benchmarking ({iterations} iterations)...")
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        _ = model.predict(input_data)
        times.append((time.perf_counter() - start) * 1000)

    results = {
        "mean_ms": statistics.mean(times),
        "std_ms": statistics.stdev(times),
        "min_ms": min(times),
        "max_ms": max(times),
        "p50_ms": statistics.median(times),
        "p90_ms": np.percentile(times, 90),
        "p99_ms": np.percentile(times, 99),
        "throughput_fps": 1000 / statistics.mean(times)
    }

    return results

# Usage
results = benchmark_model(
    "Model.mlpackage",
    {"input": (1, 3, 224, 224)},
    iterations=100
)

print(f"Mean: {results['mean_ms']:.2f}ms")
print(f"P99: {results['p99_ms']:.2f}ms")
print(f"Throughput: {results['throughput_fps']:.1f} FPS")
```

### Model Size Analysis

```python
import os
import coremltools as ct

def analyze_model_size(model_path: str) -> Dict:
    """Detailed model size analysis"""

    def get_dir_size(path):
        total = 0
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total += os.path.getsize(fp)
        return total

    # Get file/directory size
    if model_path.endswith('.mlpackage'):
        size_bytes = get_dir_size(model_path)
    else:
        size_bytes = os.path.getsize(model_path)

    # Load model for analysis
    model = ct.models.MLModel(model_path)
    spec = model.get_spec()

    # Count parameters
    param_count = 0
    if hasattr(spec, 'neuralNetwork'):
        for layer in spec.neuralNetwork.layers:
            if hasattr(layer, 'weights'):
                param_count += len(layer.weights)

    return {
        "size_bytes": size_bytes,
        "size_mb": size_bytes / (1024 * 1024),
        "size_gb": size_bytes / (1024 * 1024 * 1024),
        "param_count": param_count
    }

# Usage
info = analyze_model_size("Model.mlpackage")
print(f"Size: {info['size_mb']:.2f} MB")
```

### Compare Compressed Models

```python
def compare_models(model_paths: Dict[str, str], test_data: np.ndarray):
    """Compare multiple model variants"""

    results = []
    baseline_output = None

    for name, path in model_paths.items():
        model = ct.models.MLModel(path)

        # Size
        size_info = analyze_model_size(path)

        # Speed
        speed_info = benchmark_model(path, {"input": test_data.shape})

        # Accuracy comparison (vs baseline)
        output = model.predict({"input": test_data})
        if baseline_output is None:
            baseline_output = output
            accuracy_diff = 0
        else:
            accuracy_diff = compute_difference(baseline_output, output)

        results.append({
            "name": name,
            "size_mb": size_info["size_mb"],
            "latency_ms": speed_info["mean_ms"],
            "accuracy_diff": accuracy_diff
        })

    # Print comparison table
    print(f"{'Model':<20} {'Size (MB)':<12} {'Latency (ms)':<14} {'Acc Diff':<10}")
    print("-" * 56)
    for r in results:
        print(f"{r['name']:<20} {r['size_mb']:<12.2f} {r['latency_ms']:<14.2f} {r['accuracy_diff']:<10.4f}")

# Usage
compare_models({
    "baseline": "Model.mlpackage",
    "int8": "Model_int8.mlpackage",
    "int4": "Model_int4.mlpackage"
}, test_input)
```

## Swift Profiling

### Comprehensive Benchmarking

```swift
import CoreML
import Foundation

struct BenchmarkResult {
    let meanMs: Double
    let stdMs: Double
    let minMs: Double
    let maxMs: Double
    let p50Ms: Double
    let p90Ms: Double
    let p99Ms: Double
    let throughputFPS: Double
}

class ModelBenchmark {

    static func benchmark(
        model: MLModel,
        input: MLFeatureProvider,
        iterations: Int = 100,
        warmup: Int = 10
    ) -> BenchmarkResult {

        // Warm up
        for _ in 0..<warmup {
            _ = try? model.prediction(from: input)
        }

        // Benchmark
        var times: [Double] = []
        for _ in 0..<iterations {
            let start = CFAbsoluteTimeGetCurrent()
            _ = try? model.prediction(from: input)
            times.append((CFAbsoluteTimeGetCurrent() - start) * 1000)
        }

        times.sort()
        let mean = times.reduce(0, +) / Double(times.count)
        let variance = times.map { pow($0 - mean, 2) }.reduce(0, +) / Double(times.count)

        return BenchmarkResult(
            meanMs: mean,
            stdMs: sqrt(variance),
            minMs: times.first!,
            maxMs: times.last!,
            p50Ms: times[times.count / 2],
            p90Ms: times[Int(Double(times.count) * 0.9)],
            p99Ms: times[Int(Double(times.count) * 0.99)],
            throughputFPS: 1000 / mean
        )
    }

    static func compareComputeUnits(modelURL: URL) throws {
        let input = try createDummyInput()

        let units: [(String, MLComputeUnits)] = [
            ("All", .all),
            ("CPU+NE", .cpuAndNeuralEngine),
            ("CPU+GPU", .cpuAndGPU),
            ("CPU", .cpuOnly)
        ]

        print("Compute Unit Comparison:")
        print(String(repeating: "-", count: 50))

        for (name, computeUnit) in units {
            let config = MLModelConfiguration()
            config.computeUnits = computeUnit

            let model = try MLModel(contentsOf: modelURL, configuration: config)
            let result = benchmark(model: model, input: input)

            print("\(name.padding(toLength: 12, withPad: " ", startingAt: 0)) | Mean: \(String(format: "%.2f", result.meanMs))ms | P99: \(String(format: "%.2f", result.p99Ms))ms")
        }
    }
}
```

### Pipeline Profiling

```swift
struct PipelineProfile {
    var preprocessingMs: Double = 0
    var inferenceMs: Double = 0
    var postprocessingMs: Double = 0

    var totalMs: Double { preprocessingMs + inferenceMs + postprocessingMs }

    var breakdown: String {
        let prePercent = (preprocessingMs / totalMs) * 100
        let infPercent = (inferenceMs / totalMs) * 100
        let postPercent = (postprocessingMs / totalMs) * 100

        return """
        Pipeline Breakdown:
        - Preprocessing:  \(String(format: "%.2f", preprocessingMs))ms (\(String(format: "%.1f", prePercent))%)
        - Inference:      \(String(format: "%.2f", inferenceMs))ms (\(String(format: "%.1f", infPercent))%)
        - Postprocessing: \(String(format: "%.2f", postprocessingMs))ms (\(String(format: "%.1f", postPercent))%)
        - Total:          \(String(format: "%.2f", totalMs))ms
        """
    }
}

class PipelineProfiler {
    let model: MLModel

    init(modelURL: URL, computeUnits: MLComputeUnits = .all) throws {
        let config = MLModelConfiguration()
        config.computeUnits = computeUnits
        self.model = try MLModel(contentsOf: modelURL, configuration: config)
    }

    func profile(
        image: UIImage,
        preprocess: (UIImage) -> MLFeatureProvider,
        postprocess: (MLFeatureProvider) -> Any
    ) -> PipelineProfile {
        var profile = PipelineProfile()

        // Preprocessing
        let preStart = CFAbsoluteTimeGetCurrent()
        let input = preprocess(image)
        profile.preprocessingMs = (CFAbsoluteTimeGetCurrent() - preStart) * 1000

        // Inference
        let infStart = CFAbsoluteTimeGetCurrent()
        let output = try! model.prediction(from: input)
        profile.inferenceMs = (CFAbsoluteTimeGetCurrent() - infStart) * 1000

        // Postprocessing
        let postStart = CFAbsoluteTimeGetCurrent()
        _ = postprocess(output)
        profile.postprocessingMs = (CFAbsoluteTimeGetCurrent() - postStart) * 1000

        return profile
    }

    func averageProfile(
        images: [UIImage],
        preprocess: (UIImage) -> MLFeatureProvider,
        postprocess: (MLFeatureProvider) -> Any
    ) -> PipelineProfile {
        var totalProfile = PipelineProfile()

        for image in images {
            let p = profile(image: image, preprocess: preprocess, postprocess: postprocess)
            totalProfile.preprocessingMs += p.preprocessingMs
            totalProfile.inferenceMs += p.inferenceMs
            totalProfile.postprocessingMs += p.postprocessingMs
        }

        let count = Double(images.count)
        totalProfile.preprocessingMs /= count
        totalProfile.inferenceMs /= count
        totalProfile.postprocessingMs /= count

        return totalProfile
    }
}
```

### Memory Profiling

```swift
class MemoryProfiler {

    static func currentMemoryUsage() -> UInt64 {
        var info = mach_task_basic_info()
        var count = mach_msg_type_number_t(MemoryLayout<mach_task_basic_info>.size) / 4

        let kerr: kern_return_t = withUnsafeMutablePointer(to: &info) {
            $0.withMemoryRebound(to: integer_t.self, capacity: 1) {
                task_info(mach_task_self_, task_flavor_t(MACH_TASK_BASIC_INFO), $0, &count)
            }
        }

        guard kerr == KERN_SUCCESS else { return 0 }
        return info.resident_size
    }

    static func profileMemory(
        during block: () throws -> Void
    ) rethrows -> (beforeBytes: UInt64, peakBytes: UInt64, afterBytes: UInt64) {
        let before = currentMemoryUsage()
        var peak = before

        let timer = Timer.scheduledTimer(withTimeInterval: 0.01, repeats: true) { _ in
            peak = max(peak, currentMemoryUsage())
        }

        try block()

        timer.invalidate()
        let after = currentMemoryUsage()

        return (before, peak, after)
    }

    static func formatBytes(_ bytes: UInt64) -> String {
        let mb = Double(bytes) / (1024 * 1024)
        return String(format: "%.2f MB", mb)
    }
}

// Usage
let (before, peak, after) = try MemoryProfiler.profileMemory {
    let model = try MLModel(contentsOf: modelURL)
    for _ in 0..<100 {
        _ = try model.prediction(from: input)
    }
}

print("Memory Before: \(MemoryProfiler.formatBytes(before))")
print("Memory Peak: \(MemoryProfiler.formatBytes(peak))")
print("Memory After: \(MemoryProfiler.formatBytes(after))")
print("Memory Delta: \(MemoryProfiler.formatBytes(peak - before))")
```

## Xcode Instruments

### Core ML Template

1. **Launch**: Product > Profile (Cmd+I)
2. **Select**: Core ML template
3. **Configure**: Choose your app and device
4. **Record**: Press Record, run inference, press Stop

### Key Metrics to Watch

**Model Load Track**:
- `prepare and cache`: First-time compilation (slow)
- `cached`: Using cached compilation (fast)

**Predictions Track**:
- Duration per prediction
- Compute lane shows ANE/GPU/CPU usage

**Layer Details**:
- Execution time per layer
- Compute unit per layer
- Memory allocation

### Custom Instruments

```swift
import os

let coreMLLog = OSLog(subsystem: "com.app.coreml", category: "Performance")

class InstrumentedModel {
    let model: MLModel

    func predict(_ input: MLFeatureProvider) throws -> MLFeatureProvider {
        os_signpost(.begin, log: coreMLLog, name: "Prediction")
        defer { os_signpost(.end, log: coreMLLog, name: "Prediction") }

        return try model.prediction(from: input)
    }
}
```

## Automated Testing

### Performance Test Suite

```swift
import XCTest

class CoreMLPerformanceTests: XCTestCase {

    var model: MLModel!
    var input: MLFeatureProvider!

    override func setUp() {
        super.setUp()
        let config = MLModelConfiguration()
        config.computeUnits = .all
        model = try! MLModel(contentsOf: modelURL, configuration: config)
        input = try! createTestInput()

        // Warm up
        for _ in 0..<10 {
            _ = try? model.prediction(from: input)
        }
    }

    func testInferenceLatency() throws {
        measure(metrics: [XCTClockMetric()]) {
            _ = try? model.prediction(from: input)
        }
    }

    func testInferenceMemory() throws {
        measure(metrics: [XCTMemoryMetric()]) {
            _ = try? model.prediction(from: input)
        }
    }

    func testThroughput() throws {
        let iterations = 100
        let startTime = CFAbsoluteTimeGetCurrent()

        for _ in 0..<iterations {
            _ = try model.prediction(from: input)
        }

        let duration = CFAbsoluteTimeGetCurrent() - startTime
        let fps = Double(iterations) / duration

        XCTAssertGreaterThan(fps, 30, "Should maintain at least 30 FPS")
    }

    func testP99Latency() throws {
        var times: [Double] = []

        for _ in 0..<100 {
            let start = CFAbsoluteTimeGetCurrent()
            _ = try model.prediction(from: input)
            times.append((CFAbsoluteTimeGetCurrent() - start) * 1000)
        }

        times.sort()
        let p99 = times[98]

        XCTAssertLessThan(p99, 50, "P99 latency should be under 50ms")
    }
}
```

### CI Integration

```yaml
# .github/workflows/performance.yml
name: Performance Tests

on:
  pull_request:
    paths:
      - '*.mlpackage'
      - 'Sources/**'

jobs:
  performance:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Performance Tests
        run: |
          xcodebuild test \
            -scheme App \
            -destination 'platform=iOS Simulator,name=iPhone 15 Pro' \
            -only-testing:AppTests/CoreMLPerformanceTests

      - name: Benchmark Model
        run: |
          python scripts/benchmark_model.py \
            --model Model.mlpackage \
            --output benchmark_results.json

      - name: Compare to Baseline
        run: |
          python scripts/compare_baseline.py \
            --current benchmark_results.json \
            --baseline baseline.json \
            --threshold 10
```
