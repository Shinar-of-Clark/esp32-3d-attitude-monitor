# 3D Attitude Monitoring System - Product Specification (Pro v1.1)

## 1. Product Introduction
The **3D Attitude Monitor** is a professional monitoring solution that combines IoT hardware with a 3D desktop visualization host application. This system is specifically designed for long-term tilt and attitude monitoring of rod-like or tower-like structures such as lightning rods, tall towers, and bridges. It collects data through a high-precision MEMS sensor at the front end and performs real-time 3D model reconstruction and smooth display on the computer, helping users to intuitively grasp the health status of the structure.
<div align="center">

![System Architecture Diagram](assets/system_architecture.png)
> **Figure 1: System Overall Architecture Diagram** 
</div>

## 2. Core Features
*   **Real-time 3D Attitude Visualization**: Converts raw angle data into an intuitive 3D "lightning rod" model based on underlying mathematical matrix transformations.
*   **Industrial-Grade Anti-Jitter Algorithm**: Built-in Exponential Moving Average (EMA) low-pass filter and an advanced Deadzone filtering algorithm completely eliminate environmental sensor noise, resulting in a rock-steady display.
*   **Multi-dimensional Data Synchronization**: In addition to X/Y axis tilt angles (Roll/Pitch), it simultaneously monitors the structure's total acceleration (Total Acc) and ambient temperature (Temp).
*   **One-Click Reference Plane Calibration**: Supports dynamic calibration of a relative zero point and restoration of the absolute physical gravity reference.
*   **Highly Customizable (White-labeling)**: Allows for no-code modification of the software title and button text via an external configuration file, and enables one-click replacement of the company logo.

## 3. Technical Specifications
*   **Applicable Hardware**: ESP32 series main controller + LIS3DH 3-axis accelerometer/temperature sensor
*   **Communication Interface**: USB to Serial (Default Baud Rate: 115200)
*   **Host PC Environment**: Windows 10/11 (Standalone version, no Python dependencies required)
*   **Attitude Refresh Rate**: ~50Hz (20ms interval, extremely fast response)
*   **Algorithm Deadzone Thresholds**: Angle 0.6° / Acceleration 0.02G / Temperature 0.2°C (The underlying algorithm is encrypted for excellent anti-interference performance)

<div align="center">

## 4. Hardware Wiring Requirements
<img src="assets/hardware_wiring.png" alt="Hardware Wiring Diagram" width="50%" />

> **Figure 2: Photo of ESP32 and Sensor Wiring**  
</div>