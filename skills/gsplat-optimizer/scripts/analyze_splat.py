#!/usr/bin/env python3
"""
Gaussian Splat Analyzer

Analyzes .ply and .splat files to provide optimization recommendations
for real-time rendering on Apple platforms (iOS, macOS, visionOS).

Usage:
    python analyze_splat.py scene.ply --device iphone --fps 60
    python analyze_splat.py scene.splat --analyze-pruning
    python analyze_splat.py scene.ply --compression-analysis
"""

import argparse
import json
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np

# Device specifications
DEVICE_SPECS = {
    "iphone": {
        "name": "iPhone (A15+)",
        "gpu_memory_gb": 6,
        "max_gaussians_60fps": 3_000_000,
        "storage_mode": "shared",
    },
    "ipad": {
        "name": "iPad Pro (M1+)",
        "gpu_memory_gb": 16,
        "max_gaussians_60fps": 7_000_000,
        "storage_mode": "shared",
    },
    "mac": {
        "name": "Mac (M1-M3)",
        "gpu_memory_gb": 24,
        "max_gaussians_60fps": 10_000_000,
        "storage_mode": "shared",
    },
    "visionpro": {
        "name": "Vision Pro",
        "gpu_memory_gb": 16,
        "max_gaussians_60fps": 5_000_000,  # Stereo rendering
        "storage_mode": "shared",
    },
    "mac_discrete": {
        "name": "Mac (Discrete GPU)",
        "gpu_memory_gb": 24,
        "max_gaussians_60fps": 12_000_000,
        "storage_mode": "private",
    },
}

# Bytes per gaussian (approximate)
BYTES_PER_GAUSSIAN = {
    "position": 12,  # 3 x float32
    "scale": 12,     # 3 x float32
    "rotation": 16,  # 4 x float32 (quaternion)
    "opacity": 4,    # 1 x float32
    "sh_degree_0": 12,   # 3 x float32 (RGB)
    "sh_degree_1": 36,   # 9 x float32
    "sh_degree_2": 60,   # 15 x float32
    "sh_degree_3": 84,   # 21 x float32
}


@dataclass
class GaussianStats:
    """Statistics about a gaussian splat scene."""
    count: int
    file_size_mb: float
    memory_estimate_mb: float
    opacity_min: float
    opacity_max: float
    opacity_mean: float
    opacity_median: float
    scale_min: float
    scale_max: float
    scale_mean: float
    sh_degree: int
    has_positions: bool
    has_scales: bool
    has_rotations: bool
    has_sh: bool


def read_ply_header(filepath: Path) -> dict:
    """Read PLY header and return element info."""
    header = {}
    header["properties"] = []
    
    with open(filepath, "rb") as f:
        line = f.readline().decode("utf-8").strip()
        if line != "ply":
            raise ValueError("Not a valid PLY file")
        
        while True:
            line = f.readline().decode("utf-8").strip()
            if line == "end_header":
                header["header_size"] = f.tell()
                break
            
            parts = line.split()
            if parts[0] == "format":
                header["format"] = parts[1]
            elif parts[0] == "element":
                header["element_name"] = parts[1]
                header["element_count"] = int(parts[2])
            elif parts[0] == "property":
                prop_type = parts[1]
                prop_name = parts[2]
                header["properties"].append((prop_type, prop_name))
    
    return header


def analyze_ply(filepath: Path) -> GaussianStats:
    """Analyze a PLY gaussian splat file."""
    header = read_ply_header(filepath)
    count = header["element_count"]
    file_size_mb = filepath.stat().st_size / (1024 * 1024)
    
    # Determine SH degree from properties
    sh_props = [p[1] for p in header["properties"] if p[1].startswith("f_rest_")]
    if len(sh_props) >= 45:
        sh_degree = 3
    elif len(sh_props) >= 24:
        sh_degree = 2
    elif len(sh_props) >= 9:
        sh_degree = 1
    else:
        sh_degree = 0
    
    # Check for required properties
    prop_names = [p[1] for p in header["properties"]]
    has_positions = "x" in prop_names and "y" in prop_names and "z" in prop_names
    has_scales = "scale_0" in prop_names
    has_rotations = "rot_0" in prop_names
    has_sh = "f_dc_0" in prop_names
    
    # Estimate memory
    memory_per_gaussian = (
        BYTES_PER_GAUSSIAN["position"] +
        BYTES_PER_GAUSSIAN["scale"] +
        BYTES_PER_GAUSSIAN["rotation"] +
        BYTES_PER_GAUSSIAN["opacity"]
    )
    if sh_degree >= 0:
        memory_per_gaussian += BYTES_PER_GAUSSIAN["sh_degree_0"]
    if sh_degree >= 1:
        memory_per_gaussian += BYTES_PER_GAUSSIAN["sh_degree_1"]
    if sh_degree >= 2:
        memory_per_gaussian += BYTES_PER_GAUSSIAN["sh_degree_2"]
    if sh_degree >= 3:
        memory_per_gaussian += BYTES_PER_GAUSSIAN["sh_degree_3"]
    
    memory_estimate_mb = (count * memory_per_gaussian) / (1024 * 1024)
    
    # Try to read opacity data for statistics
    opacity_min = 0.0
    opacity_max = 1.0
    opacity_mean = 0.5
    opacity_median = 0.5
    scale_min = 0.0
    scale_max = 1.0
    scale_mean = 0.1
    
    try:
        # Find opacity property index
        opacity_idx = None
        scale_idx = None
        prop_offset = 0
        
        for i, (ptype, pname) in enumerate(header["properties"]):
            if pname == "opacity":
                opacity_idx = prop_offset
            if pname == "scale_0":
                scale_idx = prop_offset
            # Advance offset based on type
            if ptype == "float":
                prop_offset += 4
            elif ptype == "double":
                prop_offset += 8
            elif ptype == "uchar":
                prop_offset += 1
        
        bytes_per_vertex = prop_offset
        
        if header["format"] == "binary_little_endian" and opacity_idx is not None:
            # Read sample of opacities
            sample_size = min(count, 10000)
            sample_indices = np.random.choice(count, sample_size, replace=False)
            opacities = []
            scales = []
            
            with open(filepath, "rb") as f:
                f.seek(header["header_size"])
                for idx in sorted(sample_indices):
                    f.seek(header["header_size"] + idx * bytes_per_vertex)
                    vertex_data = f.read(bytes_per_vertex)
                    
                    if opacity_idx is not None:
                        opacity_bytes = vertex_data[opacity_idx:opacity_idx+4]
                        opacity = struct.unpack("<f", opacity_bytes)[0]
                        # Apply sigmoid
                        opacity = 1.0 / (1.0 + np.exp(-opacity))
                        opacities.append(opacity)
                    
                    if scale_idx is not None:
                        scale_bytes = vertex_data[scale_idx:scale_idx+4]
                        scale = struct.unpack("<f", scale_bytes)[0]
                        scale = np.exp(scale)
                        scales.append(scale)
            
            if opacities:
                opacities = np.array(opacities)
                opacity_min = float(np.min(opacities))
                opacity_max = float(np.max(opacities))
                opacity_mean = float(np.mean(opacities))
                opacity_median = float(np.median(opacities))
            
            if scales:
                scales = np.array(scales)
                scale_min = float(np.min(scales))
                scale_max = float(np.max(scales))
                scale_mean = float(np.mean(scales))
    
    except Exception as e:
        print(f"Warning: Could not read gaussian data: {e}", file=sys.stderr)
    
    return GaussianStats(
        count=count,
        file_size_mb=file_size_mb,
        memory_estimate_mb=memory_estimate_mb,
        opacity_min=opacity_min,
        opacity_max=opacity_max,
        opacity_mean=opacity_mean,
        opacity_median=opacity_median,
        scale_min=scale_min,
        scale_max=scale_max,
        scale_mean=scale_mean,
        sh_degree=sh_degree,
        has_positions=has_positions,
        has_scales=has_scales,
        has_rotations=has_rotations,
        has_sh=has_sh,
    )


def analyze_splat(filepath: Path) -> GaussianStats:
    """Analyze a .splat file (antimatter15 format)."""
    file_size = filepath.stat().st_size
    # .splat format: 32 bytes per gaussian
    bytes_per_gaussian = 32
    count = file_size // bytes_per_gaussian
    file_size_mb = file_size / (1024 * 1024)
    
    # .splat uses SH degree 0 only
    memory_estimate_mb = (count * bytes_per_gaussian) / (1024 * 1024)
    
    return GaussianStats(
        count=count,
        file_size_mb=file_size_mb,
        memory_estimate_mb=memory_estimate_mb,
        opacity_min=0.0,
        opacity_max=1.0,
        opacity_mean=0.5,
        opacity_median=0.5,
        scale_min=0.0,
        scale_max=1.0,
        scale_mean=0.1,
        sh_degree=0,
        has_positions=True,
        has_scales=True,
        has_rotations=True,
        has_sh=True,
    )


def get_pruning_recommendations(stats: GaussianStats, device: str, target_fps: int) -> dict:
    """Generate pruning recommendations based on stats and target device."""
    spec = DEVICE_SPECS[device]
    max_gaussians = spec["max_gaussians_60fps"]
    
    if target_fps == 30:
        max_gaussians *= 2
    elif target_fps == 90:
        max_gaussians = int(max_gaussians * 0.67)
    elif target_fps == 120:
        max_gaussians = int(max_gaussians * 0.5)
    
    needs_pruning = stats.count > max_gaussians
    reduction_needed = max(0, stats.count - max_gaussians)
    reduction_percent = (reduction_needed / stats.count * 100) if stats.count > 0 else 0
    
    # Suggest opacity threshold
    if reduction_percent > 30:
        suggested_opacity_threshold = 0.05
    elif reduction_percent > 15:
        suggested_opacity_threshold = 0.02
    else:
        suggested_opacity_threshold = 0.01
    
    return {
        "needs_pruning": needs_pruning,
        "current_count": stats.count,
        "target_count": max_gaussians,
        "reduction_needed": reduction_needed,
        "reduction_percent": round(reduction_percent, 1),
        "suggested_opacity_threshold": suggested_opacity_threshold,
        "opacity_stats": {
            "min": round(stats.opacity_min, 4),
            "max": round(stats.opacity_max, 4),
            "mean": round(stats.opacity_mean, 4),
            "median": round(stats.opacity_median, 4),
        },
    }


def get_compression_recommendations(stats: GaussianStats) -> dict:
    """Generate compression recommendations."""
    sogs_estimate_mb = stats.file_size_mb / 20
    sog_estimate_mb = stats.file_size_mb / 24
    codecgs_estimate_mb = stats.file_size_mb / 30
    
    return {
        "original_size_mb": round(stats.file_size_mb, 2),
        "estimates": {
            "sogs": {
                "size_mb": round(sogs_estimate_mb, 2),
                "compression_ratio": "20x",
                "quality": "good",
                "decode_speed": "fast",
            },
            "sog": {
                "size_mb": round(sog_estimate_mb, 2),
                "compression_ratio": "24x",
                "quality": "better",
                "decode_speed": "fast",
            },
            "codecgs": {
                "size_mb": round(codecgs_estimate_mb, 2),
                "compression_ratio": "30x",
                "quality": "good",
                "decode_speed": "fast (HEVC)",
            },
        },
        "recommendation": "sog" if stats.file_size_mb > 100 else "sogs",
    }


def get_lod_recommendations(stats: GaussianStats, device: str) -> dict:
    """Generate LOD recommendations for large scenes."""
    spec = DEVICE_SPECS[device]
    max_gaussians = spec["max_gaussians_60fps"]
    
    needs_lod = stats.count > max_gaussians * 1.5
    
    if needs_lod:
        levels = {
            "L0_full": {
                "distance": "0-10m",
                "gaussian_percent": 100,
                "estimated_count": min(stats.count, max_gaussians),
            },
            "L1_high": {
                "distance": "10-30m",
                "gaussian_percent": 50,
                "estimated_count": int(stats.count * 0.5),
            },
            "L2_medium": {
                "distance": "30-100m",
                "gaussian_percent": 25,
                "estimated_count": int(stats.count * 0.25),
            },
            "L3_low": {
                "distance": "100m+",
                "gaussian_percent": 10,
                "estimated_count": int(stats.count * 0.1),
            },
        }
    else:
        levels = {}
    
    return {
        "needs_lod": needs_lod,
        "reason": "Scene exceeds 1.5x device budget" if needs_lod else "Scene fits within device budget",
        "levels": levels,
        "recommended_approach": "LODGE" if stats.count > 5_000_000 else "FLoD",
    }


def main():
    parser = argparse.ArgumentParser(
        description="Analyze gaussian splat files for optimization"
    )
    parser.add_argument("file", type=Path, help="Path to .ply or .splat file")
    parser.add_argument(
        "--device",
        choices=list(DEVICE_SPECS.keys()),
        default="iphone",
        help="Target device class",
    )
    parser.add_argument(
        "--fps",
        type=int,
        choices=[30, 60, 90, 120],
        default=60,
        help="Target frames per second",
    )
    parser.add_argument(
        "--analyze-pruning",
        action="store_true",
        help="Show detailed pruning analysis",
    )
    parser.add_argument(
        "--compression-analysis",
        action="store_true",
        help="Show compression recommendations",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    
    args = parser.parse_args()
    
    if not args.file.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    
    # Analyze file
    suffix = args.file.suffix.lower()
    if suffix == ".ply":
        stats = analyze_ply(args.file)
    elif suffix == ".splat":
        stats = analyze_splat(args.file)
    else:
        print(f"Error: Unsupported file type: {suffix}", file=sys.stderr)
        sys.exit(1)
    
    # Build report
    report = {
        "file": str(args.file),
        "device": DEVICE_SPECS[args.device]["name"],
        "target_fps": args.fps,
        "stats": {
            "gaussian_count": stats.count,
            "file_size_mb": round(stats.file_size_mb, 2),
            "memory_estimate_mb": round(stats.memory_estimate_mb, 2),
            "sh_degree": stats.sh_degree,
        },
        "pruning": get_pruning_recommendations(stats, args.device, args.fps),
        "lod": get_lod_recommendations(stats, args.device),
    }
    
    if args.compression_analysis:
        report["compression"] = get_compression_recommendations(stats)
    
    # Output
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"Gaussian Splat Analysis: {args.file.name}")
        print(f"{'='*60}\n")
        
        print(f"Target: {report['device']} @ {report['target_fps']} FPS\n")
        
        print("Scene Statistics:")
        print(f"  Gaussian count: {stats.count:,}")
        print(f"  File size: {stats.file_size_mb:.2f} MB")
        print(f"  GPU memory estimate: {stats.memory_estimate_mb:.2f} MB")
        print(f"  SH degree: {stats.sh_degree}")
        print()
        
        pruning = report["pruning"]
        if pruning["needs_pruning"]:
            print("Pruning Recommendation: REQUIRED")
            print(f"  Current: {pruning['current_count']:,} gaussians")
            print(f"  Target: {pruning['target_count']:,} gaussians")
            print(f"  Reduction needed: {pruning['reduction_percent']}%")
            print(f"  Suggested opacity threshold: {pruning['suggested_opacity_threshold']}")
        else:
            print("Pruning Recommendation: Not required")
            print(f"  Scene fits within {report['device']} budget")
        print()
        
        lod = report["lod"]
        if lod["needs_lod"]:
            print("LOD Recommendation: REQUIRED")
            print(f"  Approach: {lod['recommended_approach']}")
            for level, info in lod["levels"].items():
                print(f"  {level}: {info['distance']} ({info['gaussian_percent']}%)")
        else:
            print("LOD Recommendation: Not required")
        print()
        
        if args.compression_analysis:
            comp = report["compression"]
            print("Compression Options:")
            print(f"  Original: {comp['original_size_mb']} MB")
            for name, info in comp["estimates"].items():
                print(f"  {name.upper()}: {info['size_mb']} MB ({info['compression_ratio']})")
            print(f"  Recommended: {comp['recommendation'].upper()}")
            print()


if __name__ == "__main__":
    main()
