# Radial Project Planning Diagram - User Guide

This guide provides detailed instructions for using the Radial Project Planning Diagram tool.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Concepts](#basic-concepts)
3. [Creating Your First Diagram](#creating-your-first-diagram)
4. [Working with Swimlanes](#working-with-swimlanes)
5. [Managing Outcomes](#managing-outcomes)
6. [Creating and Editing Blobs](#creating-and-editing-blobs)
7. [Saving and Loading](#saving-and-loading)
8. [Tips and Tricks](#tips-and-tricks)

## Getting Started

### Installation

1. Ensure you have Python 3.7+ installed
2. Install required dependencies:
   ```bash
   pip install PyQt5
   ```
3. Launch the application:
   ```bash
   python main_window.py
   ```

### Interface Overview

The application interface consists of:

- **Toolbar**: Contains buttons for common actions
- **Diagram View**: The main canvas where you create and edit your diagram
- **Status Bar**: Shows current status and zoom level
- **Context Menus**: Right-click on items for additional options

## Basic Concepts

The Radial Diagram consists of three main elements:

1. **Swimlanes**: Radial lines extending from the center, representing different domains or categories
2. **Outcomes**: Points along swimlanes representing specific deliverables or milestones
3. **Scope Blobs**: Colored shapes connecting outcomes, representing related work or features

## Creating Your First Diagram

### Step 1: Add Swimlanes

1. Click the "Add Swimlane" button in the toolbar
2. Enter a name for your swimlane (e.g., "Frontend", "Backend", "UX")
3. Specify an angle (0-360 degrees) or accept the default
4. Click "OK" to create the swimlane

Repeat this process to add multiple swimlanes around the diagram.

### Step 2: Add Outcomes

1. Click the "Add Outcome" button in the toolbar
2. Select the swimlane where you want to add the outcome
3. Enter a label for your outcome (e.g., "Login Page", "Database Schema")
4. Specify the distance from center or accept the default
5. Click "OK" to create the outcome

### Step 3: Connect with Blobs

1. Click the "Draw Blob" button or press 'B'
2. Click on a starting outcome
3. Drag to an ending outcome
4. Release to create the blob
5. Enter an optional label for the blob
6. The blob will be created with a color based on its position

## Working with Swimlanes

### Adjusting Swimlanes

- **Change Length**: Drag the end handle of a swimlane
- **Change Angle**: Select the swimlane and use the rotation handle
- **Change Color**: Right-click on a swimlane and select "Change Color"
- **Edit Label**: Double-click on the swimlane label to edit it

### Organizing Swimlanes

- Create swimlanes at regular intervals for a balanced diagram
- Group related domains in adjacent swimlanes
- Use consistent naming conventions for clarity

## Managing Outcomes

### Positioning Outcomes

- **Move Along Swimlane**: Drag an outcome along its swimlane
- **Adjust Distance**: Select an outcome and use the distance handle
- **Change Swimlane**: Drag an outcome to a different swimlane

### Organizing Outcomes

- Position related outcomes at similar distances from center
- Use consistent labeling for clarity
- Group outcomes by project phase or priority

## Creating and Editing Blobs

### Drawing Blobs

1. Enter blob drawing mode (button or 'B' key)
2. Click on a starting outcome
3. Drag to an ending outcome
4. Release to create the blob

### Editing Blobs

- **Move**: Drag the blob to a new position
- **Resize**: Drag the resize handles
- **Change Color**: Right-click and select "Change Color"
- **Delete**: Right-click and select "Delete Blob" or select and press Delete

### Using Blobs Effectively

- Connect related outcomes across different swimlanes
- Use colors to indicate priority or category
- Add labels to provide context
- Create overlapping blobs to show complex relationships

## Saving and Loading

### Saving Your Diagram

1. Click "Save" in the toolbar or press Ctrl+S
2. Choose a location and filename
3. Click "Save" to save your diagram as a JSON file

### Loading a Diagram

1. Click "Load" in the toolbar or press Ctrl+O
2. Navigate to your saved diagram file
3. Click "Open" to load the diagram

## Tips and Tricks

### Keyboard Shortcuts

- **Ctrl+Z**: Undo
- **Ctrl+Shift+Z**: Redo
- **B**: Start blob drawing
- **Escape**: Cancel current operation
- **Delete**: Remove selected item
- **Ctrl+S**: Save diagram
- **Ctrl+O**: Open diagram

### Efficient Workflow

1. **Plan First**: Sketch your domains and outcomes before creating the diagram
2. **Build Structure**: Add all swimlanes first
3. **Add Detail**: Add outcomes to each swimlane
4. **Connect**: Create blobs to show relationships
5. **Refine**: Adjust colors, positions, and labels for clarity

### Best Practices

- Keep labels concise and descriptive
- Use consistent color coding
- Position related items near each other
- Save your work frequently
- Use blobs sparingly to avoid visual clutter
- Maintain a clear visual hierarchy

## Troubleshooting

### Common Issues

1. **Blob Creation Fails**
   - Ensure you have selected valid start and end points
   - Check that both swimlanes exist

2. **Items Not Appearing**
   - Verify zoom level is appropriate
   - Check if items are outside visible area

3. **Selection Difficulties**
   - Click directly on the item's line or point
   - Zoom in for more precise selection
   - Use the selection tool for small items
