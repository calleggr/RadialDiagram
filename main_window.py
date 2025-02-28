import sys
import os
import json
import math
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,
    QGraphicsLineItem, QGraphicsPathItem, QGraphicsTextItem, QGraphicsItem,
    QVBoxLayout, QHBoxLayout, QWidget, QToolBar, QAction, QColorDialog,
    QUndoStack, QUndoCommand, QToolButton, QFrame, QInputDialog, QFileDialog,
    QMessageBox, QMenu
)
from PyQt5.QtCore import Qt, QPointF, QRectF, QSize
from PyQt5.QtGui import QPen, QBrush, QColor, QPainterPath, QIcon

# Import from models
from models.diagram import Diagram
from models.swimlane import Swimlane
from models.outcome import Outcome
from models.scope_blob import ScopeBlob

# Import from views
from views.diagram_scene import DiagramScene
from views.swimlane_item import SwimlaneItem
from views.outcome_item import OutcomeItem
from views.scope_blob_item import ScopeBlobItem

# Import from commands
from commands.add_blob_command import AddBlobCommand
from commands.delete_blob_command import DeleteBlobCommand
from commands.change_color_command import ChangeColorCommand
from commands.move_command import MoveCommand

# Import from styles
from styles.colors import get_color_palette, DEFAULT_COLORS
from styles.stylesheet import get_stylesheet

# Import from utils
from utils.geometry import calculate_point_on_line
from utils.id_generator import generate_id

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Project Scope Diagram')
        self.resize(1000, 800)
        
        # Apply modern styling
        self.setStyleSheet(get_stylesheet())
        app = QApplication.instance()
        app.setPalette(get_color_palette())

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create undo stack
        self.undo_stack = QUndoStack(self)

        # Create diagram and scene
        self.diagram = Diagram()
        self.scene = DiagramScene(self.diagram, self.undo_stack)
        
        # Create view with zoom support
        self.view = QGraphicsView(self.scene)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        layout.addWidget(self.view)
        
        # Selection mode
        self.selection_mode = False

        # Create main toolbar with modern styling
        toolbar = self.addToolBar('Tools')
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        
        # Edit toolbar
        edit_toolbar = self.addToolBar('Edit')
        edit_toolbar.setMovable(False)
        edit_toolbar.setIconSize(QSize(24, 24))
        
        # Add separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setStyleSheet(f'background-color: rgba(255,255,255,0.3)')
        edit_toolbar.addWidget(separator)
        
        # Undo/Redo actions with icons
        undo_action = self.undo_stack.createUndoAction(self)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.setIcon(QIcon.fromTheme('edit-undo'))
        undo_btn = QToolButton()
        undo_btn.setDefaultAction(undo_action)
        edit_toolbar.addWidget(undo_btn)
        
        redo_action = self.undo_stack.createRedoAction(self)
        redo_action.setShortcut('Ctrl+Shift+Z')
        redo_action.setIcon(QIcon.fromTheme('edit-redo'))
        redo_btn = QToolButton()
        redo_btn.setDefaultAction(redo_action)
        edit_toolbar.addWidget(redo_btn)
        
        # Add separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.VLine)
        separator2.setStyleSheet(f'background-color: rgba(255,255,255,0.3)')
        toolbar.addWidget(separator2)
        
        # Add swimlane action with modern button
        add_swimlane = QAction('Add Swimlane', self)
        add_swimlane.setIcon(QIcon.fromTheme('list-add'))
        add_swimlane.triggered.connect(self.add_swimlane)
        swimlane_btn = QToolButton()
        swimlane_btn.setDefaultAction(add_swimlane)
        toolbar.addWidget(swimlane_btn)

        # Add outcome action
        add_outcome = QAction('Add Outcome', self)
        add_outcome.setIcon(QIcon.fromTheme('bookmark-new'))
        add_outcome.triggered.connect(self.add_outcome)
        outcome_btn = QToolButton()
        outcome_btn.setDefaultAction(add_outcome)
        toolbar.addWidget(outcome_btn)

        # Draw blob action
        draw_blob = QAction('Draw Blob', self)
        draw_blob.setIcon(QIcon.fromTheme('draw-freehand'))
        draw_blob.triggered.connect(self.scene.start_drawing_blob)
        blob_btn = QToolButton()
        blob_btn.setDefaultAction(draw_blob)
        toolbar.addWidget(blob_btn)
        
        # Selection mode
        select_action = QAction('Select', self)
        select_action.setIcon(QIcon.fromTheme('edit-select-all'))
        select_action.setCheckable(True)
        select_action.triggered.connect(self.toggle_selection_mode)
        select_btn = QToolButton()
        select_btn.setDefaultAction(select_action)
        toolbar.addWidget(select_btn)
        
        # Add separator
        separator3 = QFrame()
        separator3.setFrameShape(QFrame.VLine)
        separator3.setStyleSheet(f'background-color: rgba(255,255,255,0.3)')
        toolbar.addWidget(separator3)
        
        # Color actions
        change_color = QAction('Change Color', self)
        change_color.setIcon(QIcon.fromTheme('color-picker'))
        change_color.triggered.connect(self.change_selected_color)
        color_btn = QToolButton()
        color_btn.setDefaultAction(change_color)
        toolbar.addWidget(color_btn)
        
        # Add separator
        separator4 = QFrame()
        separator4.setFrameShape(QFrame.VLine)
        separator4.setStyleSheet(f'background-color: rgba(255,255,255,0.3)')
        toolbar.addWidget(separator4)
        
        # Save/Load actions
        save_action = QAction('Save', self)
        save_action.setIcon(QIcon.fromTheme('document-save'))
        save_action.triggered.connect(self.save_diagram)
        save_btn = QToolButton()
        save_btn.setDefaultAction(save_action)
        toolbar.addWidget(save_btn)

        load_action = QAction('Load', self)
        load_action.setIcon(QIcon.fromTheme('document-open'))
        load_action.triggered.connect(self.load_diagram)
        load_btn = QToolButton()
        load_btn.setDefaultAction(load_action)
        toolbar.addWidget(load_btn)

    def add_swimlane(self):
        name, ok = QInputDialog.getText(self, 'Add Swimlane', 'Enter swimlane name:')
        if ok and name:
            angle, ok = QInputDialog.getDouble(self, 'Add Swimlane', 
                                             'Enter angle (degrees):', 0, -360, 360)
            if ok:
                self.scene.add_swimlane(name, angle)

    def add_outcome(self):
        swimlanes = list(self.diagram.swimlanes.keys())
        if not swimlanes:
            QMessageBox.warning(self, 'Error', 'Create a swimlane first')
            return

        swimlane, ok = QInputDialog.getItem(self, 'Add Outcome',
                                          'Select swimlane:', swimlanes, 0, False)
        if ok and swimlane:
            label, ok = QInputDialog.getText(self, 'Add Outcome', 'Enter outcome label:')
            if ok and label:
                distance, ok = QInputDialog.getDouble(self, 'Add Outcome',
                                                    'Enter distance from center:', 100, 0, 1000)
                if ok:
                    self.scene.add_outcome(swimlane, distance, label)

    def save_diagram(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'Save Diagram',
                                                '', 'JSON Files (*.json)')
        if filename:
            data = {
                'swimlanes': [
                    {
                        'id': sl.id,
                        'name': sl.name,
                        'angle': sl.angle,
                        'outcomes': [
                            {
                                'id': o.id,
                                'label': o.label,
                                'distance': o.distance
                            } for o in sl.outcomes
                        ]
                    } for sl in self.diagram.swimlanes.values()
                ],
                'blobs': [
                    {
                        'id': b.id,
                        'points': b.points,
                        'color': {
                            'r': b.color.red(),
                            'g': b.color.green(),
                            'b': b.color.blue(),
                            'a': b.color.alpha()
                        },
                        'label': b.label,
                        'outcome_ids': [o.id for o in b.outcomes]
                    } for b in self.diagram.blobs
                ]
            }
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)

    def load_diagram(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Load Diagram',
                                                '', 'JSON Files (*.json)')
        if filename:
            with open(filename, 'r') as f:
                data = json.load(f)

            # Clear existing diagram
            self.scene.clear()
            self.diagram = Diagram()
            self.scene.diagram = self.diagram

            # Create outcome lookup for blob association
            outcome_lookup = {}

            # Load swimlanes and outcomes
            for sl_data in data['swimlanes']:
                swimlane = self.scene.add_swimlane(sl_data['name'], sl_data['angle'])
                swimlane.id = sl_data['id']
                
                for o_data in sl_data['outcomes']:
                    outcome = self.scene.add_outcome(sl_data['name'],
                                                   o_data['distance'],
                                                   o_data['label'])
                    outcome.id = o_data['id']
                    outcome_lookup[o_data['id']] = outcome

            # Load blobs
            for b_data in data['blobs']:
                color = QColor(b_data['color']['r'],
                             b_data['color']['g'],
                             b_data['color']['b'],
                             b_data['color']['a'])
                
                blob = ScopeBlob(b_data['points'], color, b_data['id'],
                                label=b_data.get('label', ''))
                
                # Associate outcomes
                for outcome_id in b_data['outcome_ids']:
                    if outcome_id in outcome_lookup:
                        blob.add_outcome(outcome_lookup[outcome_id])
                
                self.diagram.blobs.append(blob)
                blob_item = ScopeBlobItem(blob, self.scene)
                self.scene.addItem(blob_item)


    def toggle_selection_mode(self, checked):
        self.selection_mode = checked
        if checked:
            self.view.setDragMode(QGraphicsView.RubberBandDrag)
        else:
            self.view.setDragMode(QGraphicsView.NoDrag)
    
    def change_selected_color(self):
        items = self.scene.selectedItems()
        if not items:
            return
            
        color = QColorDialog.getColor(initial=Qt.red, parent=self)
        if color.isValid():
            command = ChangeColorCommand(items, color)
            self.undo_stack.push(command)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # Create some example data
    # Add swimlanes first
    window.scene.add_swimlane('DevOps', 0)
    window.scene.add_swimlane('Channel', 45)
    window.scene.add_swimlane('Infrastructure', 90)
    window.scene.add_swimlane('Features', 135)
    
    # Then add outcomes
    window.scene.add_outcome('DevOps', 100, 'CI/CD')
    window.scene.add_outcome('DevOps', 200, 'Monitoring')
    window.scene.add_outcome('Channel', 100, 'Web')
    window.scene.add_outcome('Channel', 200, 'Mobile')
    window.scene.add_outcome('Channel', 300, 'In-Person')
    
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
