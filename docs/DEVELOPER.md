# Developer Documentation

This document provides detailed technical information for developers working on the Radial Project Planning Diagram tool.

## Architecture Overview

The application follows a modular architecture with clear separation between model, view, and command layers:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Models    │◄────┤  Commands   │────►│    Views    │
└─────────────┘     └─────────────┘     └─────────────┘
       ▲                   ▲                   ▲
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                     ┌─────────────┐
                     │  MainWindow │
                     └─────────────┘
```

## Class Responsibilities

### Model Layer

#### `models.diagram.Diagram`
- **Purpose**: Central data structure managing the entire diagram
- **Responsibilities**:
  - Maintain collections of swimlanes, outcomes, and blobs
  - Provide methods for adding and removing elements
  - Handle serialization and deserialization
  - Manage relationships between elements

#### `models.swimlane.Swimlane`
- **Purpose**: Represent a radial line in the diagram
- **Responsibilities**:
  - Store angle, label, and color
  - Maintain reference to visual representation

#### `models.outcome.Outcome`
- **Purpose**: Represent a point on a swimlane
- **Responsibilities**:
  - Store distance from center, label, and swimlane reference
  - Maintain list of associated blobs

#### `models.scope_blob.ScopeBlob`
- **Purpose**: Represent a connection between outcomes
- **Responsibilities**:
  - Store points defining shape, color, and label
  - Maintain references to start/end swimlanes and outcomes

### View Layer

#### `views.diagram_scene.DiagramScene`
- **Purpose**: Manage visual elements and interactions
- **Responsibilities**:
  - Handle mouse events and selection
  - Coordinate between model and view
  - Manage context menus and visual feedback
  - Create and execute commands

#### `SwimlaneItem`
- **Purpose**: Visual representation of swimlanes
- **Responsibilities**:
  - Render line and label
  - Handle drag operations for adjustment
  - Update model on user interaction

#### `OutcomeItem`
- **Purpose**: Visual representation of outcomes
- **Responsibilities**:
  - Render point and label
  - Handle drag operations and selection
  - Maintain list of associated blob items

#### `ScopeBlobItem`
- **Purpose**: Visual representation of blobs
- **Responsibilities**:
  - Render polygon and label
  - Handle selection and context menu
  - Update model on user interaction

### Command Layer

#### `commands.add_blob_command.AddBlobCommand`
- **Purpose**: Create new blobs with undo/redo support
- **Responsibilities**:
  - Create blob model and view objects
  - Associate with outcomes and swimlanes
  - Support undo by removing created objects
  - Support redo by recreating objects

#### `commands.delete_blob_command.DeleteBlobCommand`
- **Purpose**: Remove blobs with undo/redo support
- **Responsibilities**:
  - Remove blob from scene and model
  - Store references for undo
  - Support undo by restoring blob
  - Support redo by removing blob again

#### `commands.change_color_command.ChangeColorCommand`
- **Purpose**: Change item colors with undo/redo support
- **Responsibilities**:
  - Store old and new colors
  - Apply color change to item
  - Support undo by restoring old color
  - Support redo by applying new color

#### `commands.move_command.MoveCommand`
- **Purpose**: Move items with undo/redo support
- **Responsibilities**:
  - Store old and new positions
  - Apply position change to item
  - Support undo by restoring old position
  - Support redo by applying new position

## Event Flow

1. **User Interaction**:
   - User interacts with a view item (e.g., drags an outcome)
   
2. **Command Creation**:
   - View creates appropriate command (e.g., MoveCommand)
   - Command stores initial state for undo
   
3. **Command Execution**:
   - Command is pushed to undo stack
   - Command's redo() method is called automatically
   - Command modifies model and view
   
4. **Undo/Redo**:
   - When user triggers undo, command's undo() method is called
   - When user triggers redo, command's redo() method is called

## Error Handling

The application uses defensive programming to prevent crashes:

1. **Safe Attribute Access**:
   ```python
   if hasattr(obj, 'attribute') and obj.attribute:
       # Safe to use obj.attribute
   ```

2. **Exception Handling**:
   ```python
   try:
       # Potentially risky operation
   except Exception as e:
       print(f"Error: {e}")
   ```

3. **Null Object Checks**:
   ```python
   if blob and blob.start_outcome:
       # Safe to use blob.start_outcome
   ```

## Extension Points

### Adding New Commands

1. Create a new command class in the `commands` directory
2. Inherit from `QUndoCommand`
3. Implement `redo()` and `undo()` methods
4. Create and push command instances to the undo stack

Example:
```python
class MyNewCommand(QUndoCommand):
    def __init__(self, target, old_value, new_value):
        super().__init__("My New Command")
        self.target = target
        self.old_value = old_value
        self.new_value = new_value
    
    def redo(self):
        self.target.value = self.new_value
    
    def undo(self):
        self.target.value = self.old_value
```

### Adding New View Items

1. Create a new item class in the `views` directory
2. Inherit from appropriate QGraphics class
3. Implement paint() method for custom rendering
4. Add interaction handlers as needed

Example:
```python
class MyNewItem(QGraphicsItem):
    def __init__(self, model, scene):
        super().__init__()
        self.model = model
        self.scene = scene
        self.setFlag(QGraphicsItem.ItemIsSelectable)
    
    def paint(self, painter, option, widget):
        # Custom painting logic
        pass
    
    def boundingRect(self):
        # Return item bounds
        pass
```

## Performance Considerations

1. **Lazy Loading**:
   - Create view items only when needed
   - Defer expensive calculations

2. **Efficient Rendering**:
   - Use QGraphicsItem::update() instead of scene->update()
   - Implement proper boundingRect() and shape() methods

3. **Memory Management**:
   - Clean up references when items are deleted
   - Use weak references where appropriate

## Testing Strategy

1. **Unit Tests**:
   - Test individual model classes
   - Test command undo/redo logic
   - Test utility functions

2. **Integration Tests**:
   - Test interaction between models and commands
   - Test serialization/deserialization

3. **UI Tests**:
   - Test user interactions
   - Test visual rendering

## Future Enhancements

1. **Multi-user Collaboration**:
   - Implement network synchronization
   - Add conflict resolution

2. **Advanced Visualization**:
   - Add heatmaps and analytics
   - Support custom themes

3. **Export Options**:
   - Add PDF/PNG export
   - Support integration with project management tools
