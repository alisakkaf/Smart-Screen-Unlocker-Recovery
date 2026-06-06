<div align="center">
  
<img src="https://github.com/alisakkaf/Smart-Screen-Unlocker-Recovery/blob/main/icon.png?raw=true" alt="Smart Screen Unlocker Logo" width="150"/> 


# 🔓 Smart Screen Unlocker Recovery v1.0

[![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg?style=for-the-badge&logo=windows&logoColor=black)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge&logo=opensourceinitiative&logoColor=white)](https://opensource.org/licenses/MIT)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-brightgreen.svg?style=for-the-badge)]()


**Smart Screen Unlocker Recovery** is an advanced, automation-driven forensic and accessibility framework. It is specifically engineered to help mobile technicians, forensic experts, and everyday users recover access to Android devices with **completely broken displays, dead touch digitizers, or inaccessible screens**. 

By injecting raw kernel-level touch gestures via an authorized ADB (Android Debug Bridge) interface, this tool acts as a synthetic hardware digitizer, allowing you to input your known pattern and recover your data.

</div>

> **⚠️ CRITICAL NOTICE:** This is **NOT** a cracking, brute-forcing, or bypassing tool. It requires the device to have USB Debugging enabled, an authorized RSA fingerprint with the host PC, and the user MUST know the correct lock screen pattern.

---

## 🔥 Unrivaled Features & Capabilities

* **🛡️ Multi-State Awareness (AFU/BFU):** Dynamically detects if the device is in *Before First Unlock (BFU)* or *After First Unlock (AFU)* states and adjusts the vertical matrix geometry accordingly.
* **📐 Smart XML Container Bypassing:** Intelligently ignores fake, full-screen transparent containers deployed by modern security patches (e.g., Samsung OneUI 8+) to locate the true lock screen grid.
* **🎨 Interactive Visual GUI:** Features a sleek, terminal-spawned graphical canvas allowing the technician to visually draw the pattern using a mouse, mirroring physical device interaction.
* **⏱️ Auto-Timeout Prevention:** Automatically boosts the device's `screen_off_timeout` to 5 minutes during the operation to prevent screen sleep, seamlessly restoring the original settings post-injection.
* **✅ Deep Kernel Verification:** Interrogates the Android OS (`dumpsys window` & `dumpsys keyguard`) to mathematically verify a successful unlock without relying on visual screen feedback.

---
## 📸 Interface & Execution Preview

| 🎛️ Live Interactive Drawer | 📊 Deep Telemetry & Execution Log |
| :---: | :---: |
| <img src="https://raw.githubusercontent.com/alisakkaf/Smart-Screen-Unlocker-Recovery/main/images/Unlock_Screen1.png" width="450" alt="Unlock Screen Custom Matrix"> | <img src="https://raw.githubusercontent.com/alisakkaf/Smart-Screen-Unlocker-Recovery/main/images/Unlock_Screen2.png" width="450" alt="Engine Execution and Verification"> |
| <img src="https://raw.githubusercontent.com/alisakkaf/Smart-Screen-Unlocker-Recovery/main/images/Unlock_Screen3.png.png" width="450" alt="Live Hardware Touch Inference"> | <img src="https://raw.githubusercontent.com/alisakkaf/Smart-Screen-Unlocker-Recovery/main/images/ADB_Screen_Lock.png" width="450" alt="Device Connection & Handshake"> |

---
## ⚙️ The 6-Engine Multi-Attack Strategy

To account for fragmentation across Android OEMs, DPI scaling, and custom UIs, this tool utilizes a sequential cascade of mathematical engines. If one fails, the script dynamically adjusts its geometry and fires the next!

| Engine | Strategy Name | Description | Target Devices |
| :---: | :--- | :--- | :--- |
| **1** | `Dynamic XML Hierarchy` | Attempts to pull the exact pixel bounds directly from the UI Automator tree. | Universal (If not blocked) |
| **2** | `Golden Ratio Base Matrix`| Uses empirical OEM aspect ratios to calculate a mathematically perfect square or rectangle grid. | Samsung & Generic AOSP |
| **3** | `DPI Shifted Matrix` | Compensates for users who have altered their display scaling (Small/Large UI sizes). | Universal |
| **4** | `Custom High Matrix` | Targets shifted notification shade layouts, commonly found in Android 13+ environments. | Samsung & Custom ROMs |
| **5** | `Custom Extreme Matrix` | Built from extreme-case hardware telemetry for unique screen resolutions. | Tall Aspect Ratios (21:9) |
| **6** | `Cross-Over Failsafe` | Tests BFU matrices on AFU states (and vice-versa) in case of Knox or SystemUI desynchronization. | Universal |

---

## 📱 Supported & Tested Devices

This framework calculates screen matrices dynamically, making it theoretically compatible with **any Android device**. However, it has been rigorously tested and optimized for the following architectures:

| OEM / Brand | Tested Models (Examples) | UI Environment | Success Rate |
| :--- | :--- | :--- | :---: |
| **Samsung** | Galaxy S24 (SM-S921U), Galaxy S23 (SM-S911U) | OneUI 5.0 - 8.5 | 🟢 100% |
| **TCL** | T609DL, 30 SE, 40 XL | TCL UI / AOSP 12-13 | 🟢 100% |
| **Xiaomi / POCO**| Redmi Note 12, POCO X5 | MIUI 14 / HyperOS | 🟢 High |
| **Motorola** | Moto G Stylus, Edge series | MyUX / AOSP | 🟢 High |
| **Google** | Pixel 6, Pixel 7, Pixel 8 | Pixel UI | 🟢 High |

---

## 🚀 Installation & Usage

### 📦 Option 1: Standalone Windows Executable (Recommended)
You do not need Python installed. Simply download the standalone `.exe` from the [Releases](https://github.com/alisakkaf/Smart-Screen-Unlocker-Recovery/releases) tab.

1. Ensure **USB Debugging** is enabled on the target Android device.
2. Connect the device to your PC and authorize the connection.
3. Run `Smart_Screen_Unlocker.exe`.
4. Draw your pattern on the interactive GUI and watch the terminal automate the injection!

### 💻 Option 2: Running from Source

```bash
# Clone the repository
git clone [https://github.com/alisakkaf/Smart-Screen-Unlocker-Recovery.git](https://github.com/alisakkaf/Smart-Screen-Unlocker-Recovery.git)
cd Smart-Screen-Unlocker-Recovery

# Install build dependencies (optional, for compiling)
pip install -r requirements.txt

# Execute the script
python main.py 

```
## ✅ Post-Unlock Success: Complete Control via Scrcpy

Once **Smart Screen Unlocker Recovery** successfully injects the kernel gestures and bypasses the secure BFU/AFU lockscreen state, your Android device is now fully unlocked and responsive to external display utilities. 

You can immediately transition to [scrcpy](https://github.com/genymobile/scrcpy) to achieve full low-latency screen mirroring, audio forwarding, and peripheral control to safely back up your system data.

### 🚀 Quick Execution Guide:

1. Keep your device connected via the authorized USB/Wireless ADB interface.
2. Download and extract the latest version of `scrcpy` onto your host machine.
3. Execute the following terminal commands depending on your recovery workflow:

```bash
# Standard high-performance mirroring with the physical device screen off
scrcpy --always-on-top --turn-screen-off --stay-awake

# Advanced forensic stream optimized for backup operations
scrcpy --max-fps=30 --video-bit-rate=4M --audio-bit-rate=128k --window-title="Recovered Device Screen"

---

## 🛠️ Compiling to .exe (For Developers)

To bundle the utility into a portable runtime executable with your custom icon (`6437133.png`), execute this command in your PowerShell/CMD:

```powershell
python -c "from PIL import Image; img = Image.open('6437133.png'); img.save('icon.ico', format='ICO')" ; pyinstaller --noconfirm --onefile --console --icon="icon.ico" --name="Smart_Screen_Unlocker" --clean main.py 

```

---

## 🌟 Support the Project

If this digital forensics asset saved your data or assisted your mobile repair workflow, please consider giving the repository a ⭐ **Star** to increase its distribution visibility across developer channels!

### 👨‍💻 Developer & Contact Portfolio

* **Lead Engineer:** Ali Sakkaf
* **🌐 Official Website:** [alisakkaf.com](https://alisakkaf.com)
* **💻 GitHub:** [@alisakkaf](https://www.google.com/search?q=https://github.com/alisakkaf)
* **🟦 Facebook:** [AliSakkaf.Dev](https://www.google.com/search?q=https://facebook.com/AliSakkaf.Dev)

### 💡 Support the Developer

<div align="center">
  <i>If you find my tools and projects useful, consider supporting my work. Your support helps keep these projects completely free!</i>
</div>

<br>

<div align="center">

| Crypto Asset | Network | Wallet Address (Copy) | Quick Scan |
| :--- | :--- | :--- | :---: |
| ![USDT](https://img.shields.io/badge/USDT-Tether-26A17B?style=for-the-badge&logo=tether&logoColor=white) | **TRC20** | `TYLBeDA5aGNcc3WkVqf3xWPHXmsZzs2p28` | <a href="https://api.qrserver.com/v1/create-qr-code/?size=300x300&margin=10&data=TYLBeDA5aGNcc3WkVqf3xWPHXmsZzs2p28" target="_blank"><img src="https://img.shields.io/badge/Show_QR-Click_Here-black?style=flat-square&logo=qr-code" alt="QR"></a> |
| ![USDT](https://img.shields.io/badge/USDT-Tether-26A17B?style=for-the-badge&logo=tether&logoColor=white) | **BEP20** | `0x67cf27f33c80479ea96372810f9e2ee4c3b095c5` | <a href="https://api.qrserver.com/v1/create-qr-code/?size=300x300&margin=10&data=0x67cf27f33c80479ea96372810f9e2ee4c3b095c5" target="_blank"><img src="https://img.shields.io/badge/Show_QR-Click_Here-black?style=flat-square&logo=qr-code" alt="QR"></a> |
| ![BTC](https://img.shields.io/badge/BTC-Bitcoin-F7931A?style=for-the-badge&logo=bitcoin&logoColor=white) | **Bitcoin** | `bc1q97dr37h37npzarmmrv0tjz2nm50htqc7pfpzj6` | <a href="https://api.qrserver.com/v1/create-qr-code/?size=300x300&margin=10&data=bitcoin:bc1q97dr37h37npzarmmrv0tjz2nm50htqc7pfpzj6" target="_blank"><img src="https://img.shields.io/badge/Show_QR-Click_Here-black?style=flat-square&logo=qr-code" alt="QR"></a> |
| ![ETH](https://img.shields.io/badge/ETH-Ethereum-3C3C3D?style=for-the-badge&logo=ethereum&logoColor=white) | **ERC20** | `0x67cf27f33c80479ea96372810F9e2EE4C3b095C5` | <a href="https://api.qrserver.com/v1/create-qr-code/?size=300x300&margin=10&data=ethereum:0x67cf27f33c80479ea96372810F9e2EE4C3b095C5" target="_blank"><img src="https://img.shields.io/badge/Show_QR-Click_Here-black?style=flat-square&logo=qr-code" alt="QR"></a> |
| ![SOL](https://img.shields.io/badge/SOL-Solana-9945FF?style=for-the-badge&logo=solana&logoColor=white) | **Solana** | `Cbesgr4tvo4T1inNMFe46GSym2qMYjkmofbXFc77rDNK` | <a href="https://api.qrserver.com/v1/create-qr-code/?size=300x300&margin=10&data=solana:Cbesgr4tvo4T1inNMFe46GSym2qMYjkmofbXFc77rDNK" target="_blank"><img src="https://img.shields.io/badge/Show_QR-Click_Here-black?style=flat-square&logo=qr-code" alt="QR"></a> |
| ![USDC](https://img.shields.io/badge/USDC-USD_Coin-2775CA?style=for-the-badge&logo=usd-coin&logoColor=white) | **ERC20** | `0x67cf27f33c80479ea96372810f9e2ee4c3b095c5` | <a href="https://api.qrserver.com/v1/create-qr-code/?size=300x300&margin=10&data=0x67cf27f33c80479ea96372810f9e2ee4c3b095c5" target="_blank"><img src="https://img.shields.io/badge/Show_QR-Click_Here-black?style=flat-square&logo=qr-code" alt="QR"></a> |
| ![USDC](https://img.shields.io/badge/USDC-USD_Coin-2775CA?style=for-the-badge&logo=usd-coin&logoColor=white) | **SPL** | `Cbesgr4tvo4T1inNMFe46GSym2qMYjkmofbXFc77rDNK` | <a href="https://api.qrserver.com/v1/create-qr-code/?size=300x300&margin=10&data=solana:Cbesgr4tvo4T1inNMFe46GSym2qMYjkmofbXFc77rDNK" target="_blank"><img src="https://img.shields.io/badge/Show_QR-Click_Here-black?style=flat-square&logo=qr-code" alt="QR"></a> |
| ![USDC](https://img.shields.io/badge/USDC-USD_Coin-2775CA?style=for-the-badge&logo=usd-coin&logoColor=white) | **BEP20** | `0x67cf27f33c80479ea96372810F9e2EE4C3b095C5` | <a href="https://api.qrserver.com/v1/create-qr-code/?size=300x300&margin=10&data=0x67cf27f33c80479ea96372810F9e2EE4C3b095C5" target="_blank"><img src="https://img.shields.io/badge/Show_QR-Click_Here-black?style=flat-square&logo=qr-code" alt="QR"></a> |

</div>

---



**Developed By : Ali Sakkaf © 2026. All Rights Reserved.**
