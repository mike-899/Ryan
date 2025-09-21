# Computer Vision Color Detection System

A real-time computer vision system that detects colors in specific regions of interest (ROI) from camera feed and makes navigation decisions based on color patterns. This system is designed for autonomous navigation applications using OpenCV and Python.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Usage](#usage)
- [System Architecture](#system-architecture)
- [Algorithm Flow](#algorithm-flow)
- [Troubleshooting](#troubleshooting)
- [Technical Specifications](#technical-specifications)

## Overview

This project implements a sophisticated color detection system that analyzes camera feed in real-time to make navigation decisions. The system divides the camera frame into 5 predefined segments and detects predominant colors (green, black, white) in each segment to determine appropriate movement actions.

### Key Components

- **Real-time Color Detection**: Uses HSV color space for robust color recognition
- **Region of Interest (ROI) Analysis**: Processes 5 specific segments of the camera frame
- **Decision Logic**: Implements complex rule-based navigation decisions
- **Visual Feedback**: Displays detection results with bounding boxes and labels

## Features

- **Multi-Color Detection**: Detects green, black, and white colors with configurable HSV thresholds
- **Adaptive Camera Selection**: Automatically tries multiple camera indices for robust initialization
- **Morphological Operations**: Uses opening operations to reduce noise in color detection
- **Optional Median Blur**: Configurable blur filter for improved detection accuracy
- **Debug Mode**: Comprehensive logging for development and troubleshooting
- **Real-time Visualization**: Live display of detection results and ROI boundaries

### Required Libraries

```
opencv-python>=4.5.0
numpy>=1.21.0
```

### HSV Color Thresholds

```python
HSV_THRESHOLDS = {
    "verde": ((35, 80, 60), (85, 255, 255)),    # Green color range
    "negro": ((0, 0, 0), (180, 255, 50)),       # Black color range
    "blanco": ((0, 0, 200), (180, 50, 255)),    # White color range
}
```

### Detection Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MIN_RATIO` | 0.30 | Minimum ratio of detected pixels to ROI area for color predominance |
| `MORPH_KERNEL` | (3, 3) | Kernel size for morphological operations |
| `USE_MEDIAN_BLUR` | True | Enable/disable median blur preprocessing |
| `BLUR_KSIZE` | 5 | Kernel size for median blur (must be odd ≥3) |
| `CAM_INDEXS` | [3, 0, 1, 2] | Camera indices to try in order |
| `DEBUG` | False | Enable debug output for development |

### Region of Interest (ROI) Segments

The system analyzes 5 predefined segments:

```python
segmentos = {
    "segmento1": (100, 200, 200, 300),  # Left region
    "segmento2": (400, 200, 500, 300),  # Right region
    "segmento3": (250, 50, 350, 150),   # Top center region
    "segmento4": (100, 400, 200, 500),  # Bottom left region
    "segmento5": (400, 400, 500, 500),  # Bottom right region
}
```

## Usage

### Basic Operation

1. **Start the system**:
   ```bash
   python main.py
   ```

2. **Camera initialization**: The system will automatically try to open a camera using the configured indices.

3. **Real-time detection**: The system will display the camera feed with:
   - Green rectangles showing ROI boundaries
   - Color detection labels with confidence ratios
   - Navigation decisions printed to console

4. **Exit**: Press 'q' to quit the application

### Navigation Actions

The system outputs the following navigation commands:

- `adelante` - Move forward
- `atras` - Move backward
- `izquierda` - Turn left
- `derecha` - Turn right
- `izquierdaYAjuste` - Turn left with adjustment
- `derechaYAjuste` - Turn right with adjustment

All these navigation actions are executed in 90-degree increments.

### Debug Mode

Enable debug mode by setting `DEBUG = True` to see:
- Color detection ratios for each segment
- Decision logic case matching
- Detailed action reasoning

## System Architecture

### Core Functions

#### `detectar_color_en_roi(hsv_frame, coords)`
- Analyzes a specific ROI for color predominance
- Applies optional median blur and morphological operations
- Returns the predominant color and confidence ratio

#### `mov(grado)`
- Maps numerical codes to navigation actions
- Provides consistent action naming

#### `abrir_camara(indices_preferidos)`
- Attempts to open camera with fallback indices
- Ensures robust camera initialization

#### `main()`
- Main processing loop
- Coordinates color detection and decision making
- Handles visualization and user interaction

### Processing Pipeline

1. **Frame Capture**: Acquire frame from camera
2. **Color Space Conversion**: Convert BGR to HSV
3. **ROI Processing**: Analyze each of the 5 segments
4. **Color Detection**: Apply thresholding and morphological operations
5. **Decision Logic**: Use pattern matching for navigation decisions
6. **Visualization**: Display results and ROI boundaries
7. **Action Output**: Print navigation command

## Algorithm Flow

The system follows the detailed flowchart documented in <mcfile name="FlowChart.md" path="e:\Ryan\FlowChart.md"></mcfile>:

### FlowChart Documentation

The project includes a comprehensive Mermaid flowchart (`FlowChart.md`) that visualizes the entire system workflow. This flowchart serves as the architectural blueprint and shows:

#### Flowchart Phases

1. **Initialization Phase**
   - Parameter setup (HSV thresholds, morphological kernels, camera settings)
   - Camera opening with fallback indices
   - Error handling for camera initialization failures

2. **Main Processing Loop**
   - Continuous frame capture and validation
   - BGR to HSV color space conversion
   - Iterative processing of all 5 segments

3. **Segment Processing**
   - Coordinate clamping to frame boundaries
   - ROI extraction and validation
   - Optional median blur application
   - Morphological kernel preparation

4. **Color Detection**
   - HSV threshold application for each color
   - Morphological opening operations
   - Pixel counting and ratio calculations
   - Best color selection based on highest ratio

5. **Decision Logic**
   - Result collection from all segments
   - seg4_flag calculation (bottom segments analysis)
   - Complex pattern matching using tuple evaluation
   - Action determination through case analysis

6. **Action Execution**
   - Single action emission per processing cycle
   - Return to main processing loop

#### Implementation Mapping

The flowchart directly corresponds to the code implementation:

- **Initialization** → `abrir_camara()` function and parameter definitions
- **Main Loop** → `main()` function's while loop
- **Segment Processing** → `clamp_coords()` and ROI extraction logic
- **Color Detection** → `detectar_color_en_roi()` function
- **Decision Logic** → match/case statement in main loop
- **Action Execution** → `mov()` function and action printing

This flowchart serves as both documentation and a debugging tool, allowing developers to trace the exact execution path and understand the decision-making process at each step.

### Decision Logic Cases

The system uses Python's match/case statement (requires Python 3.10+) to handle complex decision scenarios:

1. **Priority Cases**:
   - Both segments 1&2 are green → Move backward
   - Segment 1 is green (no bottom flag) → Left adjustment
   - Segment 2 is green (no bottom flag) → Right adjustment

2. **Path Following**:
   - Segment 3 is black → Move forward (various conditions)
   - Both segments 1&2 are white → Move forward

3. **Correction Cases**:
   - Segment 1 black, segment 2 white → Turn left
   - Segment 1 white, segment 2 black → Turn right

4. **Fallback**: Default to forward movement

### Color Detection Algorithm

1. **ROI Extraction**: Extract region from HSV frame
2. **Preprocessing**: Apply median blur if enabled
3. **Color Thresholding**: Create binary masks for each color
4. **Morphological Opening**: Remove noise using kernel operations
5. **Ratio Calculation**: Compute detected pixels / total ROI area
6. **Best Match Selection**: Choose color with highest ratio above threshold

## Troubleshooting

### Common Issues

#### Camera Not Opening
- **Problem**: "Error al abrir la cámara" message
- **Solution**: 
  - Check camera connection
  - Modify `CAM_INDEXS` list to try different indices
  - Ensure no other applications are using the camera

#### Poor Color Detection
- **Problem**: Colors not detected accurately
- **Solutions**:
  - Adjust HSV thresholds in `HSV_THRESHOLDS`
  - Modify `MIN_RATIO` for sensitivity
  - Enable median blur with appropriate `BLUR_KSIZE`
  - Ensure proper lighting conditions

#### Performance Issues
- **Problem**: Slow frame processing
- **Solutions**:
  - Disable debug mode (`DEBUG = False`)
  - Reduce `BLUR_KSIZE` or disable blur
  - Use smaller morphological kernel
  - Ensure adequate system resources

### Debug Information

Enable debug mode to see:
```
[DEBUG] Resultados: c1=verde(0.45), c2=blanco(0.23), c3=negro(0.67), seg4_flag=True
[DEBUG] Caso disparado: c1_verde_no_seg4 -> Accion: izquierdaYAjuste
```

## Technical Specifications

### Performance Metrics
- **Frame Rate**: Depends on camera and system performance
- **Detection Latency**: < 50ms per frame (typical)
- **Memory Usage**: ~100-200MB during operation

### Color Space Details
- **Input**: BGR color space from camera
- **Processing**: HSV color space for detection
- **Thresholds**: Configurable HSV ranges for each color

### Image Processing Operations
- **Median Blur**: Noise reduction (optional)
- **Morphological Opening**: Noise removal and shape refinement
- **Binary Thresholding**: Color segmentation