# Radial Project Planning Diagram Tool

A powerful Python-based graphical application for creating interactive radial project scope diagrams. This tool allows users to visualize project components across different swimlanes, group related outcomes, and manage project scope visually.

![Radial Diagram Example](docs/radial_diagram_example.png)

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
   - Right-click on item
   - Select "Change Color" from context menu
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
- **Delete**: Remove selected item

## Architecture

The application follows a modular architecture with clear separation of concerns:

### Directory Structure

```
radial_diagram/
├── commands/              # Undo/Redo command classes
│   ├── add_blob_command.py
│   ├── change_color_command.py
│   ├── delete_blob_command.py
│   └── move_command.py
├── models/                # Data model classes
│   ├── diagram.py
│   ├── outcome.py
│   ├── scope_blob.py
│   └── swimlane.py
├── styles/                # Styling and theming
│   ├── colors.py
│   └── stylesheet.py
├── utils/                 # Utility functions
│   ├── geometry.py
│   └── id_generator.py
├── views/                 # Visual representation classes
│   └── diagram_scene.py
├── main_window.py         # Main application entry point
└── radial_diagram.py      # Legacy monolithic implementation
```

### Core Classes

#### Model Layer
- **`models.diagram.Diagram`**: Central data structure managing the entire diagram
  - Manages collections of swimlanes, outcomes, and blobs
  - Handles serialization and deserialization
  - Provides methods for adding and removing elements

- **`models.swimlane.Swimlane`**: Represents a radial line in the diagram
  - Stores angle, label, and color
  - Maintains reference to visual representation

- **`models.outcome.Outcome`**: Represents a point on a swimlane
  - Stores distance from center, label, and swimlane reference
  - Maintains list of associated blobs

- **`models.scope_blob.ScopeBlob`**: Represents a connection between outcomes
  - Stores points defining shape, color, and label
  - Maintains references to start/end swimlanes and outcomes

#### View Layer
- **`views.diagram_scene.DiagramScene`**: Manages visual elements and interactions
  - Handles mouse events and selection
  - Coordinates between model and view
  - Manages context menus and visual feedback

- **`SwimlaneItem`**: Visual representation of swimlanes
  - Renders line and label
  - Handles drag operations for adjustment

- **`OutcomeItem`**: Visual representation of outcomes
  - Renders point and label
  - Handles drag operations and selection

- **`ScopeBlobItem`**: Visual representation of blobs
  - Renders polygon and label
  - Handles selection and context menu

#### Command Layer (for Undo/Redo)
- **`commands.add_blob_command.AddBlobCommand`**: Creates new blobs with undo/redo
- **`commands.delete_blob_command.DeleteBlobCommand`**: Removes blobs with undo/redo
- **`commands.change_color_command.ChangeColorCommand`**: Changes item colors with undo/redo
- **`commands.move_command.MoveCommand`**: Moves items with undo/redo

#### Utility Layer
- **`utils.geometry`**: Geometric calculation functions
- **`utils.id_generator`**: Unique ID generation for model objects

#### Styling Layer
- **`styles.colors`**: Color definitions and palette generation
- **`styles.stylesheet`**: Application-wide stylesheet definitions

### Data Flow
1. User interactions trigger view layer events
2. Commands are created and pushed to undo stack
3. Commands modify the model layer
4. Model changes trigger view updates
5. Save/Load serializes to/from JSON

## File Format

The diagram is saved in JSON format with the following structure:
```json
{
  "center": {"x": 0, "y": 0},
  "swimlanes": [
    {
      "id": "unique_id",
      "angle": 45,
      "label": "swimlane_name",
      "color": "#RRGGBB"
    }
  ],
  "outcomes": [
    {
      "id": "unique_id",
      "swimlane_id": "swimlane_unique_id",
      "distance": 100,
      "label": "outcome_label"
    }
  ],
  "blobs": [
    {
      "id": "unique_id",
      "points": [{"x": x1, "y": y1}, {"x": x2, "y": y2}, ...],
      "color": "#RRGGBBAA",
      "label": "blob_label",
      "start_swimlane_id": "swimlane_id1",
      "end_swimlane_id": "swimlane_id2",
      "start_outcome_id": "outcome_id1",
      "end_outcome_id": "outcome_id2"
    }
  ]
}
```

## Design Principles

The application follows these key design principles:

1. **Separation of Concerns**: Clear distinction between model, view, and command layers
2. **Command Pattern**: All user actions that modify state are encapsulated in command objects
3. **Observer Pattern**: View components observe and react to model changes
4. **Single Responsibility**: Each class has a well-defined purpose and responsibility
5. **Defensive Programming**: Robust error handling to prevent crashes
6. **Progressive Disclosure**: Complex features revealed as needed

## Advanced Usage

### Custom Color Schemes

You can modify the color palette in `styles/colors.py` to create custom color schemes:

```python
COLORS = {
    'background': '#F5F5F5',
    'segment1': '#3498DB',  # Blue
    'segment2': '#2ECC71',  # Green
    'segment3': '#E74C3C',  # Red
    'segment4': '#F39C12',  # Orange
    'text': '#333333',
    'selection': '#FFC107'  # Amber
}
```

### Programmatic API

The diagram can be manipulated programmatically:

```python
from models.diagram import Diagram
from PyQt5.QtGui import QColor

# Create a new diagram
diagram = Diagram()

# Add swimlanes
swimlane1 = diagram.add_swimlane(angle=0, label="Domain 1")
swimlane2 = diagram.add_swimlane(angle=90, label="Domain 2")

# Add outcomes
outcome1 = diagram.add_outcome(swimlane1.id, distance=100, label="Outcome 1")
outcome2 = diagram.add_outcome(swimlane2.id, distance=150, label="Outcome 2")

# Save to file
diagram.save_to_file("my_diagram.json")
```

## Troubleshooting

### Common Issues

1. **Blob Creation Fails**
   - Ensure you have selected valid start and end points
   - Check that both swimlanes exist

2. **Items Not Appearing**
   - Verify zoom level is appropriate
   - Check if items are outside visible area
   - Ensure model objects are properly linked to view items

3. **Undo/Redo Not Working**
   - Confirm action was performed through command pattern
   - Check for errors in command execution

### Debugging

Enable debug logging by setting the environment variable:

```bash
export RADIAL_DIAGRAM_DEBUG=1
python main_window.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/radial-diagram.git
cd radial-diagram

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m unittest discover tests
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- PyQt5 for the powerful GUI framework
- The open-source community for inspiration and support
