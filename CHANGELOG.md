# Changelog

All notable changes to the Radial Diagram Project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-02-28

### Added
- Context menu functionality for swimlanes and outcomes
- Visual feedback for hover and selection states
- Enhanced label positioning for swimlanes and outcomes

### Fixed
- Restored drag and resize functionality for swimlanes
- Fixed application crash when attempting to drag swimlanes
- Resolved TypeError in geometry calculations
- Fixed outcome positioning and swimlane snapping
- Fixed missing functionality in diagram interaction

### Changed
- Updated `Diagram.add_outcome` method to accept either an Outcome object or parameters
- Enhanced SwimlaneItem class with comprehensive mouse event handling
- Improved model-view integration with proper update mechanisms
- Strengthened model-view separation with proper event propagation

### Added (Technical)
- Added missing `get_swimlane_by_id` and `get_outcome_by_id` methods to Diagram class
- Implemented mousePressEvent, mouseMoveEvent, and mouseReleaseEvent methods for SwimlaneItem
- Added safety checks to prevent None values in calculations
- Enabled hover events for both swimlanes and outcomes

## [0.1.0] - 2025-02-27

### Added
- Initial release of Radial Diagram Project
- PyQt5-based graphical application for interactive project scope visualization
- Modular architecture with separate directories for models, views, commands, styles, and utils
- Basic functionality for creating and managing swimlanes, outcomes, and scope blobs
