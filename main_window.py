import sys
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QGraphicsView, QUndoCommand,
                             QWidget, QVBoxLayout, QAction, QInputDialog,
                             QMessageBox, QUndoStack, QFileDialog, QColorDialog)
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush
from PyQt5.QtCore import Qt
from radial_diagram import Diagram, DiagramScene, DiagramView, ScopeBlob, ScopeBlobItem, OutcomeItem, SwimlaneItem

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Project Scope Diagram')
        self.resize(1000, 800)

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
        self.view = DiagramView(self.scene)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        layout.addWidget(self.view)
        
        # Selection mode
        self.selection_mode = False

        # Create toolbar
        toolbar = self.addToolBar('Tools')
        
        # Edit toolbar
        edit_toolbar = self.addToolBar('Edit')
        
        # Undo/Redo actions
        undo_action = self.undo_stack.createUndoAction(self)
        undo_action.setShortcut('Ctrl+Z')
        edit_toolbar.addAction(undo_action)
        
        redo_action = self.undo_stack.createRedoAction(self)
        redo_action.setShortcut('Ctrl+Shift+Z')
        edit_toolbar.addAction(redo_action)
        
        # Add swimlane action
        add_swimlane = QAction('Add Swimlane', self)
        add_swimlane.triggered.connect(self.add_swimlane)
        toolbar.addAction(add_swimlane)

        # Add outcome action
        add_outcome = QAction('Add Outcome', self)
        add_outcome.triggered.connect(self.add_outcome)
        toolbar.addAction(add_outcome)

        # Draw blob action
        draw_blob = QAction('Draw Blob', self)
        draw_blob.triggered.connect(self.scene.start_drawing_blob)
        toolbar.addAction(draw_blob)
        
        # Selection mode
        select_action = QAction('Select', self)
        select_action.setCheckable(True)
        select_action.triggered.connect(self.toggle_selection_mode)
        toolbar.addAction(select_action)
        
        # Color actions
        color_toolbar = self.addToolBar('Colors')
        
        change_color = QAction('Change Color', self)
        change_color.triggered.connect(self.change_selected_color)
        color_toolbar.addAction(change_color)
        
        # Save/Load actions
        save_action = QAction('Save', self)
        save_action.triggered.connect(self.save_diagram)
        toolbar.addAction(save_action)

        load_action = QAction('Load', self)
        load_action.triggered.connect(self.load_diagram)
        toolbar.addAction(load_action)

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


class ChangeColorCommand(QUndoCommand):
    def __init__(self, items, new_color):
        super().__init__("Change Color")
        self.items = items
        self.new_color = new_color
        self.old_colors = []
        
        for item in items:
            if isinstance(item, ScopeBlobItem):
                self.old_colors.append((item, item.blob.color))
            elif isinstance(item, OutcomeItem):
                self.old_colors.append((item, item.brush().color()))
            elif isinstance(item, SwimlaneItem):
                self.old_colors.append((item, item.pen().color()))
    
    def redo(self):
        for item in self.items:
            if isinstance(item, ScopeBlobItem):
                item.blob.color = self.new_color
                item.setBrush(QBrush(self.new_color))
            elif isinstance(item, OutcomeItem):
                item.setBrush(QBrush(self.new_color))
            elif isinstance(item, SwimlaneItem):
                item.swimlane.color = self.new_color  # Update swimlane's color
                item.normal_pen = QPen(self.new_color, 2)  # Update normal pen
                item.setPen(item.normal_pen)  # Apply the pen
    
    def undo(self):
        for item, old_color in self.old_colors:
            if isinstance(item, ScopeBlobItem):
                item.blob.color = old_color
                item.setBrush(QBrush(old_color))
            elif isinstance(item, OutcomeItem):
                item.setBrush(QBrush(old_color))
            elif isinstance(item, SwimlaneItem):
                item.swimlane.color = old_color  # Restore swimlane's color
                item.normal_pen = QPen(old_color, 2)  # Restore normal pen
                item.setPen(item.normal_pen)  # Apply the pen


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # Create some example data
    window.scene.add_swimlane('DevOps', 0)
    window.scene.add_swimlane('Channel', 45)
    window.scene.add_swimlane('Infrastructure', 90)
    window.scene.add_swimlane('Features', 135)
    
    window.scene.add_outcome('DevOps', 100, 'CI/CD')
    window.scene.add_outcome('DevOps', 200, 'Monitoring')
    window.scene.add_outcome('Channel', 100, 'Web')
    window.scene.add_outcome('Channel', 200, 'Mobile')
    window.scene.add_outcome('Channel', 300, 'In-Person')
    
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
