# Python Core Code Encryption and EXE Packaging Guide

This document records the entire process of compiling Python core algorithm code (`.py`) into low-level binary files (`.pyd`) to prevent source code leakage from decompilation, and finally packaging it into a portable single-file `.exe`.

---

## Phase 1: Prepare C++ Compilation Environment (The Most Critical Step)

Because Cython's encryption principle is to first translate Python code into C language and then compile it into machine code, Windows computers must install Microsoft's C++ compiler, otherwise it will report an error: `Microsoft Visual C++ 14.0 or greater is required`.

1. **Download Official Tools**:
   Visit the official Microsoft download page to get **Microsoft C++ Build Tools**:
   🔗 https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. **Install Core Components**:
   Run the downloaded `vs_buildtools.exe`.
   In the installation interface that pops up, **be sure to check** the following in the top left corner:
   ✅ **Desktop development with C++**
   *(After checking, core components such as MSVC and Windows SDK will be automatically selected on the right, requiring about 6~8 GB of space)*.
3. **Restart Terminal**:
   After installation is complete, you **must close and reopen the CMD/terminal window** to ensure the compiler's environment variables take effect.

---

## Phase 2: Encrypt and Compile Python Source Code to Binary (.pyd)

1. **Install Required Python Libraries for Compilation**:
   Run the following command in the terminal:
   ```bash
   pip install cython setuptools
   ```

2. **Create Compilation Script**:
   Create a new file named `compile_algo.py` in the project root directory and fill in the following code:
   ```python
   from setuptools import setup
   from Cython.Build import cythonize

   # Place the core algorithm files that need encryption protection here
   compile_files = [
       "filter_algo.py",
       "pose_algo.py"
   ]

   setup(
       ext_modules=cythonize(compile_files, compiler_directives={'language_level': "3"})
   )
   ```

3. **Execute Compilation Command**:
   Run in the terminal:
   ```bash
   python compile_algo.py build_ext --inplace
   ```
   *After successful compilation, binary files like `filter_algo.cp310-win_amd64.pyd` will be generated in the project directory.*

4. **⚠️ Extremely Important: Remove Original Source Code**:
   To prevent the plaintext source code from being packaged, **you must rename and backup the original `filter_algo.py` and `pose_algo.py`, or move them to another folder!**
   *(When running and packaging, Python will automatically recognize and call the generated `.pyd` black-box files without affecting functionality at all)*.

---

## Phase 3: Package the Program as a Standalone EXE Executable

After the core algorithms have been protected by binarization, we can package the main program (UI interface) into an EXE.

1. **Install PyInstaller Packaging Tool**:
   ```bash
   pip install pyinstaller
   ```

2. **Execute Streamlined Packaging Command (Keep External Config File)**:
   To allow end-users to freely modify `config.json` and replace the Logo, we **should not** package these resources inside the EXE, but keep them in the same directory as the EXE.
   Run in the terminal:
   ```bash
   pyinstaller -F -w monitor_3d.py
   ```
   **Parameter Explanation**:
   *   `-F`: Package into a standalone single-file EXE.
   *   `-w`: Windowed mode (hides the black CMD command line window behind it when running).

3. **Get the Final Result**:
   After packaging is complete, you can find the final `monitor_3d.exe` in the generated `dist` folder in the project.
   
   **Final Release Structure**: Take `monitor_3d.exe` out of `dist`, place it in the same directory as the external `config.json` and `assets` folders, and compress them into a zip file to send to customers. This not only protects the core algorithms (sealed in the EXE) but also allows customers to customize the OEM interface.

---
> **Summary Note**:
> If you only modify the UI logic in `monitor_3d.py` in the future, you don't need to repeat Phase 1 and Phase 2. Just run the PyInstaller command in Phase 3 to repackage.
> Only when you modify `pose_algo.py` or `filter_algo.py` do you need to rerun `python compile_algo.py build_ext --inplace` to regenerate the `.pyd` files.