# 3D Attitude Monitoring System (Pro v1.1) - Portable Release

## 🎉 v1.1 Update Notes
*   **One-Click Bilingual**: Added a dynamic language switch function in the top-left corner of the UI, taking effect immediately without restarting.
*   **Bilingual Log Terminal**: The interactive log console (CMD) at the bottom now fully supports bilingual command feedback.
*   **Remember User Preferences**: Language selection will be automatically saved locally and loaded by default on the next startup.

---

Welcome to the **3D Attitude Monitoring System**! This software is a portable version that does not require installation. It is mainly used in conjunction with the ESP32 + LIS3DH hardware terminal to monitor and visualize 3D attitude (Pitch, Roll), total acceleration (Acc), and ambient temperature (Temp) in real-time.

---

## 📂 Directory Structure Guide

After unzipping this package, you will see the following file structure:

*   🚀 **`monitor_3d.exe`** —— **Core Application**. Double-click to run directly, no environment installation required.
*   ⚙️ **`config.json`** —— **UI Configuration File**. Open with Notepad to customize the software window title, internal text, and button names.
*   📁 **`assets/`** —— **Resource Folder**. Contains the `logo.png` image displayed in the bottom right corner of the software.
*   📖 **`User_Manual.md`** —— **User Manual**. Contains detailed hardware/software usage guides and firmware flashing instructions.

---

## ⚡ Quick Start

1. **Unzip Files**: Please **extract the entire zip package** to any folder on your computer (do not run directly from within the zip file).
2. **Connect Hardware**: Use a USB cable to connect the matching sensor hardware to your computer.
3. **Run Software**: Double-click to run `monitor_3d.exe`.
   *(Note: If intercepted by antivirus software or Windows Defender on the first run, please select "More info" -> "Run anyway" or add it to the whitelist.)*
4. **Auto Connect**: The software will automatically scan and connect to the sensor port after startup. If no hardware is connected, the software will automatically enter **Simulation** mode for you to experience.

---

## 🎨 How to do Enterprise OEM Customization?

This software natively supports high-level white-label customization. You can easily transform it into your company's exclusive software without recompiling the code:

1. **Modify Interface Text**: Open `config.json` with Notepad and modify the corresponding titles and text (make sure to keep the English double quotes format).
2. **Replace Enterprise Logo**: Prepare your own enterprise Logo image (PNG format with a transparent background is recommended), name it `logo.png`, and place it in the `assets` folder to overwrite the original image.
3. **Restart to Apply**: Reopen `monitor_3d.exe` to see the brand new customized interface.

---

## 🔌 Firmware Flashing Instructions

If you need to flash firmware to a brand new ESP32 development board, or need to upgrade the firmware of existing hardware, please refer to **"Part Three: Standard Firmware Flashing Guide"** in the attached **`User_Manual.md`**.
The manual details how to use Espressif's official **Flash Download Tools** to safely and quickly flash the matching `.bin` firmware package into the main controller chip.

---

## ❓ Get More Help

Regarding the interaction of the 3D interface perspective, the sensor's "0-degree reference" reset, and absolute physical gravity calibration, please read the attached **`User_Manual.md`** in detail for complete graphical guidance.