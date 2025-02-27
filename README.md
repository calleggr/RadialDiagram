# Radial Project Planning Diagram Tool

A powerful Python-based graphical application for creating interactive radial project scope diagrams. This tool allows users to visualize project components across different swimlanes, group related outcomes, and manage project scope visually.

## Features

### Core Components
- **Swimlanes**: Radial lines representing different project areas/domains
  - Customizable names and angles
  - Adjustable length via drag handles
  - Color customization with undo/redo support
  - Visual feedback on hover and selection

- **Outcomes**: Points along swimlanes representing deliverables
  - Adjustable distance from center
  - Customizable labels
  - Draggable positioning
  - Visual selection and hover states

- **Scope Blobs**: Freeform shapes to group related outcomes
  - Interactive drawing mode
  - Customizable colors and transparency
  - Optional labels
  - Automatic outcome association

### Interface Features
- **Zoom Control**
  - Mouse wheel zoom (10-200%)
  - Zoom slider with percentage display
  - Zoom anchored at mouse cursor
  - Anti-aliasing for smooth rendering

- **Selection and Editing**
  - Single and multi-select capabilities
  - Rubber band selection
  - Context menus for item editing
  - Color customization for all elements

- **Project Management**
  - Save/Load functionality (JSON format)
  - Undo/Redo support for all operations
  - State preservation across sessions

## Installation

1. Ensure you have Python 3.7+ installed
2. Install required dependencies:
```bash
pip install PyQt5
```

## Usage

### Starting the Application
```bash
python main_window.py
```

### Basic Operations

1. **Creating Swimlanes**
   - Click "Add Swimlane" in toolbar
   - Enter name and angle (0-360 degrees)
   - Adjust length using the end handle

2. **Adding Outcomes**
   - Click "Add Outcome" in toolbar
   - Select target swimlane
   - Enter label and distance from center
   - Drag to adjust position

3. **Drawing Scope Blobs**
   - Click "Draw Blob" or press 'B'
   - Click and drag to draw shape
   - Release to complete
   - Enter optional label
   - Press Escape to cancel

4. **Customizing Colors**
   - Select item(s)
   - Click "Change Color"
   - Choose color from dialog
   - Colors persist across sessions

5. **Saving/Loading**
   - Click "Save" to export to JSON
   - Click "Load" to import existing diagram
   - All properties are preserved

### Keyboard Shortcuts
- **Ctrl+Z**: Undo
- **Ctrl+Shift+Z**: Redo
- **B**: Start blob drawing
- **Escape**: Cancel current operation

## Architecture

### Core Classes

1. **Model Layer**
   - `Diagram`: Central data structure
   - `Swimlane`: Manages swimlane properties and outcomes
   - `Outcome`: Represents individual deliverables
   - `ScopeBlob`: Groups related outcomes

2. **View Layer**
   - `DiagramScene`: Manages visual elements and interactions
   - `DiagramView`: Handles zoom and viewport
   - `SwimlaneItem`: Visual representation of swimlanes
   - `OutcomeItem`: Visual representation of outcomes
   - `ScopeBlobItem`: Visual representation of blobs

3. **Controller Layer**
   - `MainWindow`: Main application window and toolbar
   - `ChangeColorCommand`: Color change with undo/redo
   - `AddBlobCommand`: Blob creation with undo/redo

### Data Flow
1. User interactions trigger view layer events
2. View layer updates model layer
3. Model changes trigger view updates
4. Commands handle state changes with undo/redo
5. Save/Load serializes to/from JSON

## File Format

The diagram is saved in JSON format with the following structure:
```json
{
  "swimlanes": {
    "name": {
      "id": "unique_id",
      "name": "swimlane_name",
      "angle": 45,
      "color": [r, g, b, a],
      "outcomes": [
        {
          "id": "unique_id",
          "label": "outcome_label",
          "distance": 100
        }
      ]
    }
  },
  "blobs": [
    {
      "id": "unique_id",
      "points": [[x1, y1], [x2, y2], ...],
      "color": [r, g, b, a],
      "label": "blob_label",
      "outcome_ids": ["id1", "id2", ...]
    }
  ]
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
