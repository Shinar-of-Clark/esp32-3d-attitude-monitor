# 3D Attitude Monitoring System - User Manual (Pro v1.1)

<div align="center">
    <img src="assets/system_architecture.png" alt="System Overall Architecture" />
   
   > <p><b>Figure 1: System Overall Architecture Diagram</b></p>
</div>

---

## Part One: Quick Start Guide

### 1. Hardware Sensor Wiring Instructions
To ensure the sensor works stably and is correctly identified by the main controller, please make sure the following **5 wires** are correctly connected between the LIS3DH module and the ESP32 (using I2C communication mode):

*   **VCC** -> Connect to ESP32's **3.3V** pin (Power positive)
*   **GND** -> Connect to ESP32's **GND** pin (Power negative / Common ground)
*   **SCL** -> Connect to ESP32's **I2C SCL** pin (Clock line, typically GPIO22 on a standard ESP32)
*   **SDA** -> Connect to ESP32's **I2C SDA** pin (Data line, typically GPIO21 on a standard ESP32)
*   **SDO** -> ⚠️ **Must be connected to the ESP32's GND pin** (to fix the I2C device address to `0x18`. **Do not leave floating**, as this will cause address drift, frequent disconnections, or failure to find the sensor).

> *Note: If your sensor module has other pins like `INT` (Interrupt) or `CS` (Chip Select), you can leave them unconnected in normal reading mode.*

### 2. Software Directory Guide
The system is provided as a portable version (green software) that does not require installation. After unzipping or opening the software folder, you will see the following file structure:

```text
📁 Software Distribution Root/
 ├── 🚀 monitor_3d.exe        (Core application, double-click to run)
 ├── ⚙️ config.json           (UI configuration file, for modifying title and button text)
 └── 📂 assets/
      └── 🖼️ logo.png         (Company-specific logo image, overwrite to replace)
```

双击运行主程序即可启动监控界面。如果遇到杀毒软件误报，请选择“允许运行”或加入白名单。

---

## 第二部分：操作指南

### 1. 主界面概览
软件启动后，将呈现深邃科幻的 3D 监控面板。界面支持鼠标自由拖拽旋转视角，滚轮支持模型缩放。

<div align="center">
    <img src="assets/chart.png" alt="监控上位机主界面全貌" />
   
   > <p><b>图 2：监控上位机主界面全貌</b></p>
</div>

### 2. 实时数据面板说明
界面左上角悬浮显示着当前传感器传回并经过平滑过滤的核心数据。

<div align="center">
    <img src="assets/stat.png" alt="实时数据状态面板" />
   
   > <p><b>图 3：实时数据状态面板</b></p>
</div>


*   **STATUS (当前模式)**：显示 `ORIGINAL` (绝对重力坐标) 或 `RELATIVE` (相对校准坐标)。
*   **Pitch (Y)**：俯仰角，即物体前后倾斜的角度。
*   **Roll (X)**：翻滚角，即物体左右倾斜的角度。
*   **Total Acc**：三轴合成总加速度。静止状态下应在 1.00G 左右（即标准地球重力）。
*   **Temp**：传感器芯片内部环境温度。

### 3. 校准与重置功能
在实际工程安装中，传感器固定后往往不是绝对水平的。您可以通过底部面板的控制按钮进行一键校准：

<div align="center">
    <img src="assets/button.png" alt="底部控制栏与校准按钮" />
   
   > <p><b>图 3：底部控制栏与校准按钮</b></p>
</div>


*   **Recalibrate (Set Zero) - 重新定位 (置零)**：
    点击此按钮，系统会将**当前的倾斜姿态强行定义为 0° 基准面**。3D 杆体会瞬间“回正”垂直于屏幕。此后所有的数据均基于此新基准面计算偏移量。非常适合传感器刚上墙安装完毕时的初始化操作。
*   **Reset Original - 恢复原始 (物理真实)**：
    点击此按钮，系统将清除所有的校准偏移量，完全显示传感器当前的绝对物理重力倾斜角。

### 4. 高级界面定制 (OEM / 白牌化设置)
为了满足不同项目的展示需求，软件支持免源码修改 UI 界面。
请使用“记事本”打开软件同目录下的 `config.json` 文件：

```json
{
    "languages": ["中文", "English"],
    "current_language": "中文",
    "logo_path": "assets/logo.png",
    "中文": {
        "window_title": "3D 姿态监控系统",
        "plot_title": "三维避雷针姿态监控 - 专业版 v1.1",
        "btn_reset_text": "恢复物理真实坐标"
    },
    "English": {
        "window_title": "3D Attitude Monitoring System",
        "plot_title": "3D Lightning Rod Monitor - Pro v1.1",
        "btn_reset_text": "Reset Original"
    }
}

```
<div align="center">
    <img src="assets/PIC_LOGO.png" alt="LOGO" />
   
   > <p><b>图 4：LOGO</b></p>
</div>


修改文字：您可以直接更改上述引号内的文本，保存后重新打开软件即可生效。
替换 Logo：只需将您的企业 Logo 图片命名为 logo.png (推荐使用背景透明的 PNG 图片)，并覆盖原文件，软件右下角即可展示您的专属标识。
!自定义界面效果展示

图 7：企业深度定制后的界面效果
(请在此图片中展示：修改了标题为某个假想公司名，且右下角替换为特定企业Logo后的软件界面)

---

## 第三部分：常规固件烧录指南

当需要对硬件主控 (ESP32) 进行功能升级或修复时，您可以按照以下步骤进行固件烧录操作。

### 1. 准备工作
*   **硬件连接**：使用一根**带有数据传输功能**的 USB 数据线（Type-C 或 Micro-USB，取决于开发板接口），将 ESP32 开发板与电脑直接连接。
*   **烧录软件**：下载并解压乐鑫官方烧录工具 **Flash Download Tools**（可从乐鑫官网免费获取）。
*   **固件文件**：准备好最新版本的 `.bin` 格式固件包。

### 2. 烧录步骤
1.  **打开软件**：双击运行 Flash Download Tools 目录下的 `flash_download_tool_xxx.exe`。
2.  **选择芯片**：在弹出的初始化窗口中，**Chip Type** 选择 `ESP32`，**WorkMode** 选择 `Develop`，点击 **OK**。
3.  **配置固件与地址**：
    *   在主界面中，点击第一行左侧的 `...` 按钮，选择您准备好的 `.bin` 固件文件。
    *   在文件路径右侧的输入框中，填入固件对应的烧录地址（如合并固件一般填 `0x0`，如果为单独的应用固件通常填 `0x10000`，**具体请参考获取固件时的发布说明**）。
    *   **勾选**该行最左侧的复选框，确保框内打钩。
4.  **设置端口与波特率**：
    *   **COM**：选择与开发板对应的 COM 端口（如果不确定，可拔插 USB 线观察“设备管理器”中哪个 COM 口发生变化）。
    *   **BAUD**：波特率建议选择 `460800` 或 `115200` 以保证烧录稳定性。
5.  **开始烧录**：
    *   点击左下角的 **START** 按钮，软件右侧状态栏会显示 `SYNC` 等待同步。
    *   *(注：极少数开发板可能需要此时长按板子上的 `BOOT` 按钮，直到出现下载进度条为止)*
    *   等待进度条达到 100% 且状态面板显示 `FINISH`，即表示烧录成功。
6.  **重启生效**：烧录完成后，按下开发板上的 `EN` / `RST` 按钮，或直接重新插拔 USB 线，新固件即可运行。

第四部分：常见问题解答 (FAQ)
Q: 为什么静止放置时，角度和G值依然存在 0.1 左右的轻微跳动？ A: 这是由于外部环境微震动或传感器硬件热噪声导致的。我们已在底层启用了死区(Deadzone)过滤算法，目前的微小跳动已控制在工业允许误差范围内，不影响整体趋势判断。

Q: 软件显示“串口连接失败”怎么办？ A: 请按以下步骤排查：

检查 USB 线是否具有数据传输功能（部分充电线无法传数据）。
打开电脑的“设备管理器”，检查“端口(COM和LPT)”下是否有对应的设备。
确保没有其他串口助手软件正在占用该 COM 口。
Q: 修改了 config.json 后软件无法打开？ A: 请检查 JSON 文件的格式是否正确。特别注意所有的标点符号必须是英文半角，且最后一项参数末尾不能有逗号。如果不慎改坏，直接删除 config.json，软件下次启动时会自动生成默认配置
