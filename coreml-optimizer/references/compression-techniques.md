# CoreML Compression Techniques - Detailed Reference

## Overview

CoreML Tools provides three primary compression methods that can be applied post-training or during training for optimal results.

## 1. Quantization

### Linear Quantization Modes

**Symmetric Quantization** (Recommended for Neural Engine):
- Maps values symmetrically around zero
- `zero_point = 0`
- Formula: `Q(x) = round(x / scale)`
- Best for weights centered around zero

**Asymmetric Quantization**:
- Allows offset from zero
- Formula: `Q(x) = round(x / scale) + zero_point`
- Better for activations with non-zero mean

### Granularity Options

```python
import coremltools.optimize as cto

# Per-tensor (smallest model, lowest accuracy)
config = cto.coreml.OpLinearQuantizerConfig(
    granularity="per_tensor"
)

# Per-channel (best balance)
config = cto.coreml.OpLinearQuantizerConfig(
    granularity="per_channel"
)

# Per-block (available in coremltools 8+)
config = cto.coreml.OpLinearQuantizerConfig(
    granularity="per_block",
    block_size=32
)
```

### Precision Levels

| Precision | Size Reduction | Accuracy Loss | Speed Gain |
|-----------|---------------|---------------|------------|
| INT8 | 50% (from FP16) | <1% typical | 2-3x |
| INT4 | 75% (from FP16) | 1-3% typical | 3-4x |
| INT2 | 87.5% (from FP16) | 5-10%+ | 4-5x |

### Advanced Quantization Configurations

```python
# Selective quantization by operation type
config = cto.coreml.OptimizationConfig()

# Quantize convolutions to INT8
config.set_op_type(
    "conv",
    cto.coreml.OpLinearQuantizerConfig(dtype="int8")
)

# Quantize linear layers to INT4 for transformers
config.set_op_type(
    "linear",
    cto.coreml.OpLinearQuantizerConfig(dtype="int4", granularity="per_block")
)

# Keep first/last layers in FP16 for accuracy
config.set_op_name("input_conv", None)
config.set_op_name("output_linear", None)
```

### Calibration-Based Quantization

```python
# Load calibration data (128-256 samples recommended)
def load_calibration_data():
    samples = []
    for image_path in calibration_paths[:256]:
        img = preprocess_image(image_path)
        samples.append({"input": img})
    return samples

calibration_data = load_calibration_data()

# Apply with calibration
compressed = cto.coreml.linear_quantize_weights(
    model,
    config=config,
    calibration_data=calibration_data,
    calibration_num_samples=128
)
```

## 2. Palettization

### How It Works

Palettization clusters weights into k unique values (palette), storing only indices + lookup table:

```
Original weights: [0.12, 0.15, 0.11, 0.89, 0.91, 0.88]
4-bit palette (16 values): [0.13, 0.90, ...]
Indices: [0, 0, 0, 1, 1, 1]
```

### Configuration Options

```python
# K-means clustering (best accuracy)
config = cto.coreml.OpPalettizerConfig(
    mode="kmeans",
    nbits=4,
    granularity="per_channel"
)

# Uniform distribution (faster, lower accuracy)
config = cto.coreml.OpPalettizerConfig(
    mode="uniform",
    nbits=4,
    granularity="per_channel"
)
```

### Bit Depths

| nbits | Unique Values | Size Reduction | Use Case |
|-------|--------------|----------------|----------|
| 8 | 256 | 50% | Conservative |
| 6 | 64 | 62.5% | Balanced |
| 4 | 16 | 75% | Aggressive |
| 3 | 8 | 81.25% | Very aggressive |
| 2 | 4 | 87.5% | Extreme |
| 1 | 2 | 93.75% | Binary (limited use) |

### When to Use Palettization vs Quantization

**Use Palettization When:**
- Quantization causes significant accuracy drop
- Model has irregular weight distributions
- Targeting Neural Engine (palettization well-optimized)

**Use Quantization When:**
- Maximum speed is priority
- Model has regular weight distributions
- Need calibration data integration

## 3. Pruning

### Pruning Strategies

**Magnitude Pruning** (Default):
Removes weights with smallest absolute values.

```python
config = cto.coreml.OpMagnitudePrunerConfig(
    target_sparsity=0.5,
    granularity="per_scalar"
)
```

**Structured Pruning** (Better for hardware):
Removes entire filters/channels.

```python
config = cto.coreml.OpMagnitudePrunerConfig(
    target_sparsity=0.5,
    granularity="per_channel"  # Removes entire channels
)
```

### Sparsity Levels

| Sparsity | Size Benefit | Speed Benefit | Accuracy Impact |
|----------|-------------|---------------|-----------------|
| 30% | Minimal | Minimal | Low |
| 50% | Moderate | 1.2-1.5x | Moderate |
| 75% | High | 2-3x | Significant |
| 90%+ | Very high | 3-5x | High (needs fine-tuning) |

### Training-Aware Pruning (Recommended)

Post-training pruning has limitations. For best results, integrate pruning during training:

```python
import coremltools.optimize.torch as cto_torch

# During training
pruner = cto_torch.pruning.MagnitudePruner(
    model,
    target_sparsity=0.5,
    granularity="per_scalar"
)

# Training loop
for epoch in range(num_epochs):
    for batch in dataloader:
        pruner.step()  # Update pruning masks
        # ... normal training ...

    # Gradually increase sparsity
    pruner.update_sparsity(epoch)

# Finalize pruning (make masks permanent)
pruner.finalize()
```

## 4. Combined Compression

### Pruning + Quantization

```python
# Step 1: Prune
prune_config = cto.coreml.OptimizationConfig(
    global_config=cto.coreml.OpMagnitudePrunerConfig(target_sparsity=0.5)
)
pruned = cto.coreml.prune_weights(model, config=prune_config)

# Step 2: Quantize
quant_config = cto.coreml.OptimizationConfig(
    global_config=cto.coreml.OpLinearQuantizerConfig(
        mode="linear_symmetric",
        dtype="int8"
    )
)
final = cto.coreml.linear_quantize_weights(pruned, config=quant_config)
```

### Pruning + Palettization

```python
# Supported in coremltools 8+
config = cto.coreml.OptimizationConfig(
    global_config=cto.coreml.OpCompoundConfig(
        pruning_config=cto.coreml.OpMagnitudePrunerConfig(target_sparsity=0.5),
        palettization_config=cto.coreml.OpPalettizerConfig(nbits=4)
    )
)
```

## 5. Compression Workflows

### Data-Free Compression (Fastest)

```python
# No training data needed
# Takes seconds to minutes
# Good for 6-8 bit compression

model = ct.models.MLModel("Model.mlpackage")
config = cto.coreml.OptimizationConfig(
    global_config=cto.coreml.OpLinearQuantizerConfig(dtype="int8")
)
compressed = cto.coreml.linear_quantize_weights(model, config=config)
```

### Calibration-Based Compression

```python
# Requires ~128 samples
# Takes minutes
# Better accuracy for 4-bit

calibration_data = load_samples(128)
config = cto.coreml.OptimizationConfig(
    global_config=cto.coreml.OpLinearQuantizerConfig(
        dtype="int4",
        granularity="per_block"
    )
)
compressed = cto.coreml.linear_quantize_weights(
    model,
    config=config,
    calibration_data=calibration_data
)
```

### Fine-Tuning Based Compression

```python
# Requires full training setup
# Takes hours/days
# Best accuracy for aggressive compression

import coremltools.optimize.torch as cto_torch

# Wrap model with quantization
quantizer = cto_torch.quantization.LinearQuantizer(
    model,
    config=cto_torch.quantization.LinearQuantizerConfig(dtype="int4")
)

# Fine-tune on training data
for epoch in range(fine_tune_epochs):
    for batch in train_loader:
        loss = compute_loss(quantizer.model(batch))
        loss.backward()
        optimizer.step()

# Export to CoreML
quantizer.finalize()
mlmodel = ct.convert(quantizer.model, ...)
```

## 6. Accuracy Preservation Tips

### Layer-Wise Sensitivity Analysis

```python
def analyze_sensitivity(model, test_data):
    """Find layers most sensitive to quantization"""
    baseline_acc = evaluate(model, test_data)

    results = []
    for layer_name in get_layer_names(model):
        # Quantize only this layer
        config = cto.coreml.OptimizationConfig()
        config.set_op_name(layer_name,
            cto.coreml.OpLinearQuantizerConfig(dtype="int8"))

        quantized = cto.coreml.linear_quantize_weights(model, config=config)
        acc = evaluate(quantized, test_data)

        results.append({
            "layer": layer_name,
            "accuracy_drop": baseline_acc - acc
        })

    # Sort by sensitivity
    return sorted(results, key=lambda x: x["accuracy_drop"], reverse=True)
```

### Mixed Precision Strategy

Based on sensitivity analysis:

```python
config = cto.coreml.OptimizationConfig()

# Keep sensitive layers in higher precision
for layer in most_sensitive_layers[:5]:
    config.set_op_name(layer, None)  # Skip compression

# Compress non-sensitive layers aggressively
config.set_global_config(
    cto.coreml.OpLinearQuantizerConfig(dtype="int4")
)
```

## 7. Model-Specific Recommendations

### Vision Models (CNN)

- 8-bit quantization typically works well
- First conv and final classifier are often sensitive
- Use per-channel quantization

### Transformer Models (LLM)

- 4-bit with per-block granularity recommended
- Attention layers can be more sensitive
- Consider palettization for embedding layers

### Detection Models (YOLO, etc.)

- Keep detection heads in higher precision
- Backbone can tolerate aggressive compression
- NMS is often the bottleneck (optimize separately)

### Diffusion Models

- Large model size makes compression essential
- 8-bit works well for U-Net
- Text encoder can use 4-bit
