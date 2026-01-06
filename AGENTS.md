# AGENTS.md - Glassnotes Development Guide

This file provides guidelines and commands for agentic coding assistants working on the Glassnotes project.

## Project Overview

Glassnotes is a modern PyQt6-based notepad application featuring a glassmorphism design inspired by Windows 11. The project uses a modular architecture with clear separation between UI (`src/ui/`) and business logic (`src/logic/`).

## Build Commands

### Running the Application
```bash
python run.py
```

### Building Windows Executable
```bash
build_exe.bat
```
This creates a standalone `.exe` in the `dist/` folder using PyInstaller.

### Manual PyInstaller Build
```bash
pyinstaller --noconsole --onefile --name "Glassnotes" --clean --noconfirm ^
  --icon="assets/icon.ico" ^
  --add-data "src;src" ^
  --add-data "assets;assets" ^
  --hidden-import="PyQt6" ^
  --hidden-import="qfluentwidgets" ^
  run.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

## Code Style Guidelines

### Imports
Organize imports in three sections with blank lines between them:
1. Standard library imports (sys, os, json, etc.)
2. Third-party imports (PyQt6, qfluentwidgets, etc.)
3. Local imports (from src.ui.*, src.logic.*)

Example:
```python
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from src.ui.main_window import MainWindow
from src.logic.config import config
```

### File Structure
- Each module should have a module-level docstring at the top
- Use `_` prefix for private methods and internal functions
- Initialize global service instances at module level (e.g., `config = Config()`)
- Keep the `run.py` file minimal - just import and call main()

### Class Design
- Use PyQt6 signal-slot mechanism for UI events
- Define custom signals using `pyqtSignal` at class level
- Connect signals in `_init_*` methods (e.g., `_init_components`, `_init_navigation`)
- Use `super()` without arguments for Python 3 style
- Private helper methods should be prefixed with `_`

### Naming Conventions
- **Classes**: PascalCase (e.g., `MainWindow`, `Config`, `Editor`)
- **Methods/Variables**: snake_case (e.g., `save_current_note`, `get_resource_path`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `APP_NAME`, `CONFIG_FILE`)
- **Signals**: snake_case (e.g., `word_count_changed`, `cursor_position_changed`)
- **Qt Widget Object Names**: CamelCase with descriptive names (e.g., `EditorTabs`, `status_bar_frame`)

### Error Handling
- Wrap file I/O and external operations in try/except blocks
- Log errors with descriptive messages using `print(f"Error: {e}")`
- Show user-facing errors with InfoBar dialogs:
  ```python
  InfoBar.error("Title", "Error message", duration=3000, parent=self)
  InfoBar.success("Title", "Success message", duration=2000, parent=self)
  ```
- Handle Qt import errors gracefully (e.g., `try: ... except ImportError: pass`)

### Configuration Management
- Use the `Config` class from `src.logic.config` for all settings
- Access settings via `config.get("key", default)` and `config.set("key", value)`
- The config file is stored at `~/.glassnotes/config.json`
- Settings include: theme, accent_color, font_size, window dimensions, recent files, session state

### UI Components
- Use `qfluentwidgets` for premium UI elements (MSFluentWindow, FluentIcon, etc.)
- Apply glassmorphism styling via `src/ui/styles.py` and `GlassColors` constants
- Use `InfoBar` for user notifications (success/info/warning/error)
- Support keyboard shortcuts using `QShortcut` with `QKeySequence`
- Implement drag-and-drop by overriding `dragEnterEvent` and `dropEvent`

### Resources and Paths
- Use `Config.get_resource_path("relative/path")` for asset paths
- Resources work both in development and PyInstaller-built executables
- Store icons in `assets/` folder
- Access config directories via `config.NOTES_DIR`, `config.BACKUP_DIR`, etc.

### Threading and Signals
- PyQt UI operations must run on the main thread
- For async operations, use QTimer for simple delays or QtConcurrent for background work
- Never block the main event loop with long-running operations

### Window Management
- Set window minimum size with `setMinimumSize(width, height)`
- Center window on screen using `QApplication.primaryScreen().availableGeometry()`
- Save window dimensions to config on resize/close
- Handle high DPI displays with `QApplication.setHighDpiScaleFactorRoundingPolicy`

### File Operations
- Use `FileManager` from `src.logic.file_manager` for file I/O
- Always use UTF-8 encoding: `open(path, 'r', encoding='utf-8')`
- Track recent files via `config.add_recent_file(path)` and `config.get("recent_files", [])`

### Testing
- This project does not currently have automated tests
- When adding tests, use pytest and place test files in a `tests/` directory
- Run tests with: `pytest tests/`
- Run a single test: `pytest tests/test_file.py::TestClass::test_method`

### Linting
- No formal linting is configured
- When adding linting, use ruff for Python linting:
  ```bash
  ruff check .
  ruff check src/ --fix
  ```

### Key Files to Understand
- `src/main.py`: Application entry point, Qt app initialization
- `src/ui/main_window.py`: Main window, navigation, tab management
- `src/ui/editor.py`: Text editor with line numbers, syntax highlighting
- `src/ui/hub.py`: Dashboard view for recent files and cloud notes
- `src/ui/settings.py`: Settings panel with theme/color options
- `src/logic/config.py`: Settings management and persistence
- `src/logic/file_manager.py`: Local file operations
- `src/logic/drive_service.py`: Google Drive integration

### Common Patterns
- Global instances: `config`, `file_manager`, `drive_service` are singletons
- Signal connections: Connect in `_init_*` methods, disconnect carefully in `_on_*` handlers
- Status updates: Use StatusBarWidget for word count, cursor position, save status
- Session restore: Save/restore tabs via `config.set("session_tabs", [...])`

### Resources
- PyQt6 Documentation: https://www.riverbankcomputing.com/static/Docs/PyQt6/
- qfluentwidgets: https://qfluentwidgets.com/
- PyInstaller: https://pyinstaller.org/
