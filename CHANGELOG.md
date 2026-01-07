# Changelog

All notable changes to Glassnotes will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2025-01-08

### Added

- **Virtualized Note List** (`src/ui/virtual_note_list.py`): New memory-efficient note list widget using `QListWidget` with custom items. Supports:
  - Animated hover effects on note items
  - Preview text with line truncation
  - Metadata display (modified time, character/word counts)
  - Delete and unlink action buttons with hover animations
  - Cloud/local indicator icons
  - Placeholder for future Google Drive integration (`is_cloud` parameter)

- **File Preview Caching** (`src/logic/file_manager.py`): Added `@lru_cache` decorated preview function for efficient note previews:
  - `_get_file_preview_cached()`: Cached file preview with 128-entry LRU cache
  - `get_file_preview()`: Public API for getting note previews
  - `clear_preview_cache()`: Cache invalidation for when files change

### Changed

- **Hub View Architecture** (`src/ui/hub.py`): Complete refactor to match Settings interface pattern:
  - Changed base class from `QWidget` to `QFrame` with `QScrollArea` wrapper
  - Section headers now positioned **outside** glass cards (like Settings)
  - Note list content rendered **inside** glass cards
  - Header and search bar stay fixed while notes scroll
  - Removed legacy `NoteCard` class (replaced by `VirtualNoteList`)
  - Simplified layout structure with consistent spacing

- **Settings View Architecture** (`src/ui/settings.py`): Refactored to match new Hub pattern:
  - `SettingsSection` class refactored from `CardWidget` to `QWidget`
  - Header layout separated from content card
  - Added `#SettingsCard` object name for shared styling with Hub
  - Consistent `#SectionHeader` object name between Hub and Settings

- **Styles Refactor** (`src/ui/styles.py`):
  - New `#HubView` wrapper styles with glassmorphism border
  - New `#SettingsView` wrapper styles (renamed from `#SettingsPanel`)
  - New `#SettingsCard` style for content containers (shared between Hub and Settings)
  - New `#SettingsSection` style for section layout
  - Consistent styling patterns between Hub and Settings views
  - Updated search bar, badges, and empty state styles

- **Main Window** (`src/ui/main_window.py`):
  - Refactored status bar from grouped blocks to direct layout
  - Simplified spacing with `layout.addSpacing()` instead of spacer widgets
  - Added signal disconnection helper `_disconnect_editor_signals()`
  - Cloud features now conditional on `ENABLE_CLOUD` flag
  - Better signal connection/disconnection handling for tab switching

- **Status Bar** (`src/ui/main_window.py`):
  - Streamlined layout with direct widget placement
  - Simplified spacing using `addSpacing()` calls
  - Removed `_create_block()` helper (no longer needed)
  - Cleaner visual hierarchy with consistent margins

- **Editor Find All** (`src/ui/editor.py`):
  - Refactored `_find_all_matches()` to use `re.finditer()` for cleaner implementation
  - Reduced code complexity while maintaining functionality
  - Import moved to function top level for clarity

### Removed

- **Legacy NoteCard Class**: Removed `NoteCard` class from `hub.py` (replaced by `VirtualNoteList`)
- **Status Bar Block Helper**: Removed `_create_block()` method from `StatusBarWidget`

### Fixed

- **Memory Management**: Fixed potential garbage collection issue where container widgets were being collected prematurely
- **Layout Consistency**: Hub and Settings now share identical structural patterns
- **Signal Disconnection**: Added proper signal disconnection to prevent duplicate connections on tab switches

### Future (Hidden Behind `ENABLE_CLOUD = False`)

The following cloud features are implemented but hidden until `ENABLE_CLOUD = True` in `config.py`:

- Google Drive authentication and OAuth2 flow
- Cloud note listing, upload, and download
- Cloud settings UI in Settings panel
- Cloud login button in Hub view
- Cloud note count badges and indicators

To enable cloud features:
1. Set `ENABLE_CLOUD = True` in `src/logic/config.py`
2. Implement stub methods in `src/logic/drive_service.py`
3. Uncomment cloud sections in `src/ui/settings.py`

### Technical Debt

- Drive service stub improved with `NotImplementedError` and type hints
- Editor find functionality simplified but maintains feature parity
- Various pre-existing type-checking warnings remain (IDE/linter only, not runtime errors)

[Unreleased]: https://github.com/marodriguezd/Glassnotes/compare/main...perf/refactor-memory-optimization
[2.0.0]: https://github.com/marodriguezd/Glassnotes/releases/tag/v2.0.0
