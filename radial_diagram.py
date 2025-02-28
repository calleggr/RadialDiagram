import sys
import math
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QGraphicsView, QGraphicsScene,
                             QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsPolygonItem,
                             QGraphicsTextItem, QMenu, QAction, QInputDialog, QMessageBox,
                             QUndoStack, QUndoCommand, QFileDialog, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QColorDialog, QDialog, QLabel, QLineEdit, QDialogButtonBox,
                             QGraphicsRectItem, QFormLayout, QSpinBox, QSlider, QGraphicsItem,
                             QGraphicsDropShadowEffect)
from PyQt5.QtGui import (QPainter, QPen, QBrush, QColor, QPolygonF, QPainterPath,
                        QLinearGradient, QIcon)
from PyQt5.QtCore import Qt, QPointF, QLineF, QRectF, QPoint, QSizeF
from styles import COLORS

# --- Utility Functions ---

def generate_unique_id():
    global _NEXT_ID
    _NEXT_ID += 1
    return _NEXT_ID

_NEXT_ID = 1

# --- Model Classes ---

class Outcome:
    def __init__(self, label, distance, swimlane, id=None):
        self.id = id or generate_unique_id()
        self.label = label
        self.distance = distance
        self.swimlane = swimlane
        self.position = QPointF()
        self.associated_blobs = [] # Blobs that contain this outcome
        self.item = None  # Reference to the OutcomeItem

    def calculate_position(self):
        angle_rad = math.radians(self.swimlane.angle)
        x = self.swimlane.diagram.center.x() + self.distance * math.cos(angle_rad)
        y = self.swimlane.diagram.center.y() + self.distance * math.sin(angle_rad)
        self.position = QPointF(x, y)

    def __repr__(self):
        return f"Outcome(id={self.id}, label='{self.label}', distance={self.distance}, swimlane='{self.swimlane.name}')"

class Swimlane:
    def __init__(self, name, angle, diagram, id=None, color=None):
        self.id = id or generate_unique_id()
        self.name = name
        self.angle = angle
        self.length = 250  # Default length
        self.outcomes = []
        self.diagram = diagram
        self.line_item = None  # QGraphicsLineItem
        self.label_item = None  # QGraphicsTextItem
        self.color = color or QColor(Qt.black)

    def add_outcome(self, outcome):
        self.outcomes.append(outcome)
        outcome.calculate_position()

    def remove_outcome(self, outcome):
        if outcome in self.outcomes:
            self.outcomes.remove(outcome)

    def __repr__(self):
        return f"Swimlane(id={self.id}, name='{self.name}', angle={self.angle})"

class ScopeBlob:
    def __init__(self, points, color=QColor(255, 0, 0, 50), id=None, outcomes=None, label=""):
        self.id = id or generate_unique_id()
        self.points = points
        self.color = color
        self.outcomes = outcomes or []
        self.polygon_item = None
        self.label = label
        self.label_item = None
        self.start_swimlane = None
        self.end_swimlane = None
        self.start_outcome = None
        self.end_outcome = None
        self.associated_blobs = []  # Initialize associated_blobs

    def add_outcome(self, outcome):
        if outcome not in self.outcomes:
            self.outcomes.append(outcome)
            outcome.associated_blobs.append(self)

    def remove_outcome(self, outcome):
        if outcome in self.outcomes:
            self.outcomes.remove(outcome)
            if self in outcome.associated_blobs:
                outcome.associated_blobs.remove(self)

    def contains_point(self, point):
        polygon = QPolygonF([QPointF(p[0], p[1]) for p in self.points])
        return polygon.containsPoint(point, Qt.OddEvenFill)

    def __repr__(self):
        return f"ScopeBlob(id={self.id}, num_outcomes={len(self.outcomes)})"

class Diagram:
    def __init__(self, center_x=400, center_y=300):
        self.swimlanes = {}  # name: Swimlane object
        self.blobs = []
        self.center = QPointF(center_x, center_y)

    def add_swimlane(self, name, angle, color=None):
        if name in self.swimlanes:
            raise ValueError(f"Swimlane with name '{name}' already exists.")
        swimlane = Swimlane(name, angle, self, color=color)
        self.swimlanes[name] = swimlane
        return swimlane

    def remove_swimlane(self, name):
        if name in self.swimlanes:
            swimlane = self.swimlanes.pop(name)
            for outcome in swimlane.outcomes:
                for blob in self.blobs:
                    blob.remove_outcome(outcome)
            return swimlane
        return None

    def add_outcome(self, swimlane_name, distance, label):
        swimlane = self.swimlanes.get(swimlane_name)
        if not swimlane:
            raise ValueError(f"Swimlane '{swimlane_name}' not found.")
        outcome = Outcome(label, distance, swimlane)
        swimlane.add_outcome(outcome)
        return outcome

    def add_blob(self, points, color=QColor(255, 0, 0, 50), label=""):
        blob = ScopeBlob(points, color, label=label)
        self.blobs.append(blob)
        return blob

    def remove_blob(self, blob):
        if blob in self.blobs:
            # Safe removal from outcomes
            try:
                if hasattr(blob, 'start_outcome') and blob.start_outcome:
                    if hasattr(blob.start_outcome, 'associated_blobs'):
                        if blob in blob.start_outcome.associated_blobs:
                            blob.start_outcome.associated_blobs.remove(blob)
            except Exception as e:
                print(f"Error removing from start outcome: {e}")
                
            try:
                if hasattr(blob, 'end_outcome') and blob.end_outcome:
                    if hasattr(blob.end_outcome, 'associated_blobs'):
                        if blob in blob.end_outcome.associated_blobs:
                            blob.end_outcome.associated_blobs.remove(blob)
            except Exception as e:
                print(f"Error removing from end outcome: {e}")
                
            self.blobs.remove(blob)
    def find_outcomes_in_blob(self, blob):
        for swimlane in self.swimlanes.values():
            for outcome in swimlane.outcomes:
                if blob.contains_point(outcome.position):
                    blob.add_outcome(outcome)

    def get_outcome_by_id(self, outcome_id):
        for swimlane in self.swimlanes.values():
            for outcome in swimlane.outcomes:
                if outcome.id == outcome_id:
                    return outcome
        return None
    def get_blob_by_id(self, blob_id):
        for blob in self.blobs:
            if blob.id == blob_id:
                return blob
        return None

    def get_swimlane_by_id(self, swimlane_id):
        for name, swimlane in self.swimlanes.items():
            if swimlane.id == swimlane_id:
                return swimlane
        return None

    def to_dict(self):
      """Serializes the Diagram object to a dictionary for saving."""
      return {
          'swimlanes': {name: {'name': s.name, 'angle': s.angle, 'id': s.id,
                                'color': [s.color.red(), s.color.green(), s.color.blue(), s.color.alpha()],
                                'outcomes': [{'id': o.id, 'label': o.label, 'distance': o.distance, 'swimlane_id': s.id}
                                              for o in s.outcomes]}
                         for name, s in self.swimlanes.items()},
          'blobs': [{'id': b.id, 'points': b.points, 'color': [b.color.red(), b.color.green(), b.color.blue(), b.color.alpha()], 'label':b.label,
                      'outcome_ids': [o.id for o in b.outcomes]} for b in self.blobs]
      }
    @classmethod
    def from_dict(cls, data, diagram):
        """Creates a Diagram object from a dictionary loaded from a file."""

        for swimlane_data in data['swimlanes'].values():
            color = QColor(*swimlane_data.get('color', [0, 0, 0, 255]))
            swimlane = diagram.add_swimlane(swimlane_data['name'], swimlane_data['angle'], color=color)
            swimlane.id = swimlane_data['id']  # Restore the original ID
            for outcome_data in swimlane_data['outcomes']:
                outcome = diagram.add_outcome(swimlane.name, outcome_data['distance'], outcome_data['label'])
                outcome.id = outcome_data['id']

        for blob_data in data['blobs']:
            color = QColor(*blob_data['color'])
            blob = diagram.add_blob(blob_data['points'], color, label=blob_data.get('label', ""))
            blob.id = blob_data['id']
            #Restore outcomes to blob
            for outcome_id in blob_data['outcome_ids']:
                outcome = diagram.get_outcome_by_id(outcome_id)
                if outcome:
                    blob.add_outcome(outcome)
        return diagram

# --- View and Controller Classes ---

class MoveCommand(QUndoCommand):
    def __init__(self, item, old_pos, new_pos):
        super().__init__("Move Item")
        self.item = item
        self.old_pos = old_pos
        self.new_pos = new_pos
    
    def undo(self):
        self.item.setPos(self.old_pos)
        if isinstance(self.item, OutcomeItem):
            self.item.outcome.position = self.old_pos
    
    def redo(self):
        self.item.setPos(self.new_pos)
        if isinstance(self.item, OutcomeItem):
            self.item.outcome.position = self.new_pos


class OutcomeItem(QGraphicsEllipseItem):
    def __init__(self, outcome, diagram_scene):
        super().__init__(0, 0, 10, 10)
        self.outcome = outcome
        self.diagram_scene = diagram_scene
        self.setPos(outcome.position - QPointF(5, 5))
        self.setBrush(QBrush(Qt.blue))
        self.setPen(QPen(Qt.black))
        self.setFlag(QGraphicsEllipseItem.ItemIsSelectable)
        self.setFlag(QGraphicsEllipseItem.ItemIsMovable)
        self.setFlag(QGraphicsEllipseItem.ItemSendsGeometryChanges)
        self.text_item = QGraphicsTextItem(str(outcome.label), self)
        self.text_item.setDefaultTextColor(Qt.black)
        self.text_item.setPos(15, -5)
        self.start_pos = None
        self.setAcceptHoverEvents(True)
        
        # Track associated blobs
        self.associated_blobs = []

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Create dialog
            dialog = QDialog()
            dialog.setWindowTitle('Edit Outcome')
            dialog.setModal(True)
            
            # Create layout
            layout = QVBoxLayout(dialog)
            
            # Add form layout for inputs
            form = QFormLayout()
            
            # Label input
            label_input = QLineEdit(str(self.outcome.label))
            form.addRow('Label:', label_input)
            
            # Distance input
            distance_input = QSpinBox()
            distance_input.setMinimum(50)
            distance_input.setMaximum(500)
            distance_input.setValue(int(float(self.outcome.distance)))
            form.addRow('Distance from center:', distance_input)
            
            layout.addLayout(form)
            
            # Add buttons
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)
            
            # Show dialog
            if dialog.exec_() == QDialog.Accepted:
                try:
                    # Update outcome properties
                    self.outcome.label = label_input.text()
                    self.outcome.distance = float(distance_input.value())
                    
                    # Update visual elements
                    self.text_item.setPlainText(self.outcome.label)
                    self.outcome.calculate_position()
                    self.setPos(self.outcome.position - QPointF(5, 5))
                    
                    # Update scene
                    if self.scene():
                        self.scene().update()
                except Exception as e:
                    QMessageBox.warning(None, 'Error', f'Failed to update outcome: {str(e)}')
            
            event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = self.pos()
            # Store initial distance for calculating new distance during drag
            self.start_distance = self.outcome.distance
        elif event.button() == Qt.RightButton:
            self.diagram_scene.show_outcome_context_menu(event.screenPos(), self)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.isSelected():
            super().mouseMoveEvent(event)
            # Calculate new distance based on position relative to center
            center = self.diagram_scene.diagram.center
            pos = self.pos() + QPointF(5, 5)  # Center of outcome
            new_distance = math.sqrt((pos.x() - center.x())**2 + (pos.y() - center.y())**2)
            
            # Update outcome position and distance
            self.outcome.position = pos
            self.outcome.distance = new_distance
            
            # Update associated blobs
            for blob_item in self.associated_blobs:
                if blob_item and blob_item.blob:
                    # Recalculate blob points
                    points = self.diagram_scene.calculate_blob_points(
                        blob_item.blob.start_swimlane,
                        blob_item.blob.end_swimlane,
                        blob_item.blob.start_outcome,
                        blob_item.blob.end_outcome
                    )
                    if points:
                        polygon = QPolygonF(points)
                        blob_item.setPolygon(polygon)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.start_pos is not None:
            new_pos = self.pos()
            if new_pos != self.start_pos:
                command = MoveCommand(self, self.start_pos, new_pos)
                self.diagram_scene.undo_stack.push(command)
            self.start_pos = None
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if not (self.flags() & QGraphicsEllipseItem.ItemIsMovable):
            return
            
        # Get the line of the swimlane
        line = QLineF(self.outcome.swimlane.line_item.line())
        start = line.p1()
        end = line.p2()
        mouse_pos = event.scenePos()

        # Calculate vector from start to end
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        
        # If line has no length, keep outcome at start
        if dx == 0 and dy == 0:
            new_pos = start
        else:
            # Project mouse position onto line
            t = ((mouse_pos.x() - start.x()) * dx + (mouse_pos.y() - start.y()) * dy) / (dx * dx + dy * dy)
            t = max(0, min(1, t))  # Clamp t between 0 and 1
            
            # Calculate new position
            new_x = start.x() + t * dx
            new_y = start.y() + t * dy
            
            # Calculate distance from center
            center = self.outcome.swimlane.diagram.center
            distance = math.sqrt((new_x - center.x()) ** 2 + (new_y - center.y()) ** 2)
            
            # Update outcome distance and position
            self.outcome.distance = distance
            self.outcome.position = QPointF(new_x, new_y)
            
            # Move the outcome item
            super().setPos(new_x - 5, new_y - 5)
            
            # Update scene
            if self.scene():
                self.scene().update()
        
        event.accept()





class ResizeHandle(QGraphicsRectItem):
    def __init__(self, parent=None):
        super().__init__(0, 0, 10, 10, parent)
        self.setBrush(QBrush(Qt.white))
        self.setPen(QPen(Qt.black))
        self.setCursor(Qt.CrossCursor)
        self.parent_item = parent
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable)
        self.setFlag(QGraphicsRectItem.ItemSendsGeometryChanges)
        self.dragging = False

    def hoverEnterEvent(self, event):
        self.setCursor(Qt.CrossCursor)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.dragging:
            self.dragging = False
            self.setCursor(Qt.CrossCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if not self.dragging:
            return

        # Get scene position of mouse
        scene_pos = event.scenePos()
        center = self.parent_item.swimlane.diagram.center

        # Calculate new angle and length
        dx = scene_pos.x() - center.x()
        dy = scene_pos.y() - center.y()
        
        # Update swimlane properties
        new_angle = math.degrees(math.atan2(dy, dx))
        new_length = max(50, math.sqrt(dx * dx + dy * dy))  # Minimum length of 50
        
        if new_angle != self.parent_item.swimlane.angle or new_length != self.parent_item.swimlane.length:
            self.parent_item.swimlane.angle = new_angle
            self.parent_item.swimlane.length = new_length
            
            # Update the line and handle
            self.parent_item.update_line_and_label()
            
            # Update all outcomes on this swimlane
            for outcome in self.parent_item.swimlane.outcomes:
                outcome.calculate_position()
                if outcome.item:
                    outcome.item.setPos(outcome.position - QPointF(5, 5))
                    outcome.item.text_item.setPos(15, -5)
            
            # Update the scene
            self.parent_item.scene().update()
        
        event.accept()


class SwimlaneItem(QGraphicsLineItem):
    def __init__(self, swimlane, diagram_scene):
        super().__init__()
        self.swimlane = swimlane
        self.diagram_scene = diagram_scene
        self.normal_pen = QPen(self.swimlane.color, 2)
        self.selected_pen = QPen(QColor(0, 120, 215), 4)  # Blue, thicker pen for selection
        self.setPen(self.normal_pen)
        self.label_item = QGraphicsTextItem(swimlane.name)
        self.diagram_scene.addItem(self.label_item)  # Add to scene immediately
        
        # Create resize handle
        self.resize_handle = ResizeHandle(self)
        self.resize_handle.setVisible(False)
        
        self.update_line_and_label()
        self.setFlag(QGraphicsLineItem.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)  # Enable hover events


    def update_line_and_label(self):
        # Get current properties
        length = self.swimlane.length
        angle_rad = math.radians(self.swimlane.angle)
        
        # Calculate end point
        x = self.swimlane.diagram.center.x() + length * math.cos(angle_rad)
        y = self.swimlane.diagram.center.y() + length * math.sin(angle_rad)
        
        # Update line
        self.setLine(self.swimlane.diagram.center.x(), self.swimlane.diagram.center.y(), x, y)
        
        # Update label position
        label_offset = 10
        self.label_item.setPos(x + label_offset * math.cos(angle_rad),
                              y + label_offset * math.sin(angle_rad))
        
        # Update handle position to the end of the line
        if hasattr(self, 'resize_handle') and self.resize_handle:
            self.resize_handle.setPos(x - 5, y - 5)
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Clear scene selection first
            self.scene().clearSelection()
            
            # Select this swimlane
            self.setSelected(True)
            self.update_selection_state()
            
        elif event.button() == Qt.RightButton:
            self.diagram_scene.show_swimlane_context_menu(event.screenPos(), self.swimlane)
        
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.update_selection_state()

    def hoverEnterEvent(self, event):
        if not self.isSelected():
            # Create a slightly thicker version of the normal pen
            hover_pen = QPen(self.swimlane.color, 3)
            self.setPen(hover_pen)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        if not self.isSelected():
            # Use swimlane's current color
            self.normal_pen = QPen(self.swimlane.color, 2)
            self.setPen(self.normal_pen)
        super().hoverLeaveEvent(event)

    def update_selection_state(self):
        if self.isSelected():
            self.setPen(self.selected_pen)
            self.label_item.setDefaultTextColor(self.selected_pen.color())
            self.resize_handle.setVisible(True)
        else:
            # Use swimlane's color for both pen and label
            self.normal_pen = QPen(self.swimlane.color, 2)  # Recreate pen with current color
            self.setPen(self.normal_pen)
            self.label_item.setDefaultTextColor(self.swimlane.color)
            self.resize_handle.setVisible(False)

class AddBlobCommand(QUndoCommand):
    def __init__(self, scene, points, label):
        super().__init__("Add Blob")
        self.scene = scene
        self.points = points
        self.label = label
        self.blob = None
        self.blob_item = None

    def redo(self):
        try:
            # Get next segment color
            segment_num = len(self.scene.diagram.blobs) % 4 + 1
            color_key = f'segment{segment_num}'
            
            # Create blob with segment color
            color = QColor(COLORS[color_key])
            color.setAlpha(80)
            self.blob = self.scene.diagram.add_blob(self.points, color=color, label=self.label)
            
            # Store swimlanes and outcomes
            self.blob.start_swimlane = self.scene.start_swimlane
            self.blob.end_swimlane = self.scene.end_swimlane
            self.blob.start_outcome = self.scene.start_outcome
            self.blob.end_outcome = self.scene.end_outcome
            
            # Create and add blob item
            self.blob_item = ScopeBlobItem(self.blob, self.scene)
            self.scene.addItem(self.blob_item)
            self.blob.polygon_item = self.blob_item
            
            # Associate blob with outcomes safely
            if self.blob.start_outcome and hasattr(self.blob.start_outcome, 'item'):
                if hasattr(self.blob.start_outcome.item, 'associated_blobs'):
                    self.blob.start_outcome.item.associated_blobs.append(self.blob_item)
            
            if self.blob.end_outcome and hasattr(self.blob.end_outcome, 'item'):
                if hasattr(self.blob.end_outcome.item, 'associated_blobs'):
                    self.blob.end_outcome.item.associated_blobs.append(self.blob_item)
        except Exception as e:
            print(f"Error in AddBlobCommand.redo: {e}")

    def undo(self):
        try:
            # Remove blob from associated outcomes
            if self.blob.start_outcome:
                self.blob.start_outcome.item.associated_blobs.remove(self.blob_item)
            if self.blob.end_outcome:
                self.blob.end_outcome.item.associated_blobs.remove(self.blob_item)
            
            # Remove blob from scene
            if self.blob_item:
                self.scene.removeItem(self.blob_item)
            if self.blob:
                self.scene.diagram.remove_blob(self.blob)
        except Exception as e:
            print(f"Error in AddBlobCommand.undo: {e}")

class ScopeBlobItem(QGraphicsPolygonItem):
    def __init__(self, blob, diagram_scene):
        super().__init__()
        self.blob = blob
        self.diagram_scene = diagram_scene
        self.dragging = False
        self.start_pos = None
        
        # Get segment color based on position
        segment_num = len(self.diagram_scene.diagram.blobs) % 4 + 1
        self.color_key = f'segment{segment_num}'
        self.light_key = f'segment{segment_num}_light'
        
        # Set fill color with transparency
        self.update_colors()
        
        self.update_polygon()
        self.setFlag(QGraphicsPolygonItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsPolygonItem.ItemIsMovable, True)
        self.setAcceptHoverEvents(True)
        
        # Modern label styling
        self.label_item = QGraphicsTextItem(self.blob.label, self)
        self.label_item.setDefaultTextColor(QColor(COLORS['text']))
        if self.blob.points:
            self.update_label_position()
    
    def update_colors(self):
        color = QColor(COLORS[self.color_key])
        color.setAlpha(80)
        self.setBrush(QBrush(color))
        
        gradient = QLinearGradient(0, 0, 10, 10)
        gradient.setColorAt(0, QColor(COLORS[self.color_key]))
        gradient.setColorAt(1, QColor(COLORS[self.light_key]))
        pen = QPen(QBrush(gradient), 2)
        pen.setStyle(Qt.SolidLine)
        self.setPen(pen)
    
    def update_label_position(self):
        br = self.boundingRect()
        label_br = self.label_item.boundingRect()
        self.label_item.setPos(
            br.center().x() - label_br.width() / 2,
            br.center().y() - label_br.height() / 2
        )
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.start_pos = event.pos()
        elif event.button() == Qt.RightButton:
            self.show_context_menu(event.screenPos())
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        self.dragging = False
        super().mouseReleaseEvent(event)
    
    def mouseMoveEvent(self, event):
        if self.dragging:
            super().mouseMoveEvent(event)
            self.update_label_position()
    
    def hoverEnterEvent(self, event):
        # Highlight on hover
        color = QColor(COLORS[self.color_key])
        color.setAlpha(120)  # More opaque when hovering
        self.setBrush(QBrush(color))
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        if not self.isSelected():
            color = QColor(COLORS[self.color_key])
            color.setAlpha(80)  # Return to normal opacity
            self.setBrush(QBrush(color))
        super().hoverLeaveEvent(event)
    
    def show_context_menu(self, pos):
        menu = QMenu()
        
        # Color submenu
        color_menu = menu.addMenu("Change Color")
        for i in range(1, 5):
            color_key = f'segment{i}'
            action = color_menu.addAction(f"Color {i}")
            action.triggered.connect(lambda checked, k=color_key: self.change_color(k))
        
        # Delete action
        delete_action = menu.addAction("Delete")
        delete_action.triggered.connect(self.delete_blob)
        
        menu.exec_(pos.toPoint())
    
    def change_color(self, new_color_key):
        self.color_key = new_color_key
        self.light_key = f"{new_color_key}_light"
        self.update_colors()
    
    def delete_blob(self):
        # Remove from associated outcomes safely
        try:
            if self.blob.start_outcome and hasattr(self.blob.start_outcome, 'item'):
                if hasattr(self.blob.start_outcome.item, 'associated_blobs'):
                    if self in self.blob.start_outcome.item.associated_blobs:
                        self.blob.start_outcome.item.associated_blobs.remove(self)
        except Exception as e:
            print(f"Error removing from start outcome: {e}")
        
        try:
            if self.blob.end_outcome and hasattr(self.blob.end_outcome, 'item'):
                if hasattr(self.blob.end_outcome.item, 'associated_blobs'):
                    if self in self.blob.end_outcome.item.associated_blobs:
                        self.blob.end_outcome.item.associated_blobs.remove(self)
        except Exception as e:
            print(f"Error removing from end outcome: {e}")
        
        # Remove from scene and diagram
        self.diagram_scene.removeItem(self)
        self.diagram_scene.diagram.remove_blob(self.blob)
    def update_polygon(self):
        polygon = QPolygonF([QPointF(p[0], p[1]) for p in self.blob.points])
        self.setPolygon(polygon)
        super().mousePressEvent(event)

class DiagramView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setMinimumSize(800, 600)
        
        # Add zoom slider
        self.zoom_slider = QSlider(Qt.Horizontal, self)
        self.zoom_slider.setMinimum(10)
        self.zoom_slider.setMaximum(200)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setTickPosition(QSlider.TicksBelow)
        self.zoom_slider.setTickInterval(10)
        self.zoom_slider.valueChanged.connect(self.set_zoom)
        
        # Position slider at bottom center
        self.zoom_slider.setFixedWidth(200)
        self.zoom_slider.move(
            (self.width() - self.zoom_slider.width()) // 2,
            self.height() - self.zoom_slider.height() - 10
        )
        
        # Add zoom percentage label
        self.zoom_label = QLabel(self)
        self.zoom_label.setAlignment(Qt.AlignCenter)
        self.update_zoom_label(100)
        self.zoom_label.move(
            (self.width() - self.zoom_label.width()) // 2,
            self.height() - self.zoom_slider.height() - 30
        )
        
        self.scale(1, 1)
    
    def wheelEvent(self, event):
        # Get the current scale factor
        current_scale = self.transform().m11()
        
        # Calculate zoom factor - adjust 1.2 to change zoom sensitivity
        factor = 1.2
        if event.angleDelta().y() < 0:
            factor = 1.0 / factor
        
        # Calculate new scale
        new_scale = current_scale * factor
        
        # Limit zoom range
        if 0.1 <= new_scale <= 2.0:
            self.scale(factor, factor)
            # Update slider to match wheel zoom
            self.zoom_slider.setValue(int(new_scale * 100))
    
    def set_zoom(self, value):
        # Convert slider value to scale factor
        new_scale = value / 100.0
        
        # Get current scale
        current_scale = self.transform().m11()
        
        # Calculate factor needed to reach new scale
        factor = new_scale / current_scale
        
        # Apply zoom
        self.scale(factor, factor)
        self.update_zoom_label(value)
    
    def update_zoom_label(self, value):
        self.zoom_label.setText(f"{value}%")
        self.zoom_label.adjustSize()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Update slider position on window resize
        self.zoom_slider.move(
            (self.width() - self.zoom_slider.width()) // 2,
            self.height() - self.zoom_slider.height() - 10
        )
        self.zoom_label.move(
            (self.width() - self.zoom_label.width()) // 2,
            self.height() - self.zoom_slider.height() - 30
        )

class DiagramScene(QGraphicsScene):
    def __init__(self, diagram, undo_stack, parent=None):
        super().__init__(parent)
        self.diagram = diagram
        self.undo_stack = undo_stack
        self.drawing_blob = False
        self.start_swimlane = None
        self.start_outcome = None
        self.end_swimlane = None
        self.end_outcome = None
        self.preview_rect = None
        self.setSceneRect(-400, -300, 1600, 1200)  # Larger scene rect for zooming
        
    def find_closest_swimlane(self, pos):
        """Find the closest swimlane to a given position"""
        min_dist = float('inf')
        closest_swimlane = None
        point = QPointF(pos.x(), pos.y())
        
        for swimlane in self.diagram.swimlanes.values():
            # Get the line of the swimlane
            start = self.diagram.center
            end = QPointF(
                self.diagram.center.x() + swimlane.length * math.cos(math.radians(swimlane.angle)),
                self.diagram.center.y() + swimlane.length * math.sin(math.radians(swimlane.angle))
            )
            line = QLineF(start, end)
            
            # Calculate distance from point to line
            dist = abs((end.y() - start.y()) * point.x() - 
                      (end.x() - start.x()) * point.y() + 
                      end.x() * start.y() - 
                      end.y() * start.x()) / line.length()
            
            if dist < min_dist:
                min_dist = dist
                closest_swimlane = swimlane
        
        return closest_swimlane
    
    def calculate_curved_rect_points(self, start_swimlane, end_swimlane):
        """Calculate points for a curved rectangle between swimlanes"""
        if not (start_swimlane and end_swimlane):
            return None
            
        # Get angles in radians
        start_angle = math.radians(start_swimlane.angle)
        end_angle = math.radians(end_swimlane.angle)
        
        # Ensure angles are in correct order
        if end_angle < start_angle:
            start_angle, end_angle = end_angle, start_angle
            start_swimlane, end_swimlane = end_swimlane, start_swimlane
        
        # Calculate points
        points = []
        num_points = 20  # Number of points for smooth curve
        
        # Inner curve (closer to center)
        inner_radius = 50  # Distance from center
        for i in range(num_points):
            t = i / (num_points - 1)
            angle = start_angle + t * (end_angle - start_angle)
            x = self.diagram.center.x() + inner_radius * math.cos(angle)
            y = self.diagram.center.y() + inner_radius * math.sin(angle)
            points.append(QPointF(x, y))
        
        # Outer curve
        outer_radius = start_swimlane.length * 0.8  # 80% of swimlane length
        for i in range(num_points - 1, -1, -1):
            t = i / (num_points - 1)
            angle = start_angle + t * (end_angle - start_angle)
            x = self.diagram.center.x() + outer_radius * math.cos(angle)
            y = self.diagram.center.y() + outer_radius * math.sin(angle)
            points.append(QPointF(x, y))
        
        return points

    def find_closest_outcome(self, pos, swimlane):
        """Find the closest outcome on a swimlane to a given position"""
        min_dist = float('inf')
        closest_outcome = None
        point = QPointF(pos.x(), pos.y())
        
        for outcome in swimlane.outcomes:
            outcome_pos = outcome.item.pos() + QPointF(5, 5)  # Center of outcome
            dist = math.sqrt((point.x() - outcome_pos.x())**2 + (point.y() - outcome_pos.y())**2)
            if dist < min_dist:
                min_dist = dist
                closest_outcome = outcome
        
        return closest_outcome

    def calculate_blob_points(self, start_swimlane, end_swimlane, start_outcome, end_outcome):
        """Calculate points for a pie-chart like segment"""
        if not (start_swimlane and end_swimlane):
            return None
            
        # Get angles in radians
        start_angle = math.radians(start_swimlane.angle)
        end_angle = math.radians(end_swimlane.angle)
        
        # Ensure proper angle order for arc drawing
        if end_angle < start_angle:
            end_angle += 2 * math.pi
        
        # Calculate radii
        inner_radius = 30  # Minimum distance from center
        outer_radius = max(start_outcome.distance if start_outcome else 200,
                          end_outcome.distance if end_outcome else 200)
        
        points = []
        num_points = 30  # More points for smoother curves
        
        # Start from center
        points.append(self.diagram.center)
        
        # Draw line from center to inner arc at start angle
        x = self.diagram.center.x() + inner_radius * math.cos(start_angle)
        y = self.diagram.center.y() + inner_radius * math.sin(start_angle)
        points.append(QPointF(x, y))
        
        # Draw outer arc from start to end angle
        for i in range(num_points + 1):
            t = i / num_points
            angle = start_angle * (1 - t) + end_angle * t
            x = self.diagram.center.x() + outer_radius * math.cos(angle)
            y = self.diagram.center.y() + outer_radius * math.sin(angle)
            points.append(QPointF(x, y))
        
        # Draw line back to center
        x = self.diagram.center.x() + inner_radius * math.cos(end_angle)
        y = self.diagram.center.y() + inner_radius * math.sin(end_angle)
        points.append(QPointF(x, y))
        points.append(self.diagram.center)
        
        return points

    def mousePressEvent(self, event):
        try:
            if self.drawing_blob:
                pos = event.scenePos()
                if not self.start_swimlane:
                    # First click - find starting swimlane and outcome
                    self.start_swimlane = self.find_closest_swimlane(pos)
                    if self.start_swimlane:
                        self.start_outcome = self.find_closest_outcome(pos, self.start_swimlane)
                        # Create preview polygon
                        self.preview_rect = QGraphicsPolygonItem()
                        # Get next segment color
                        segment_num = len(self.diagram.blobs) % 4 + 1
                        color_key = f'segment{segment_num}'
                        light_key = f'segment{segment_num}_light'
                        
                        color = QColor(COLORS[color_key])
                        color.setAlpha(40)
                        self.preview_rect.setBrush(QBrush(color))
                        gradient = QLinearGradient(0, 0, 10, 10)
                        gradient.setColorAt(0, QColor(COLORS[color_key]))
                        gradient.setColorAt(1, QColor(COLORS[light_key]))
                        pen = QPen(QBrush(gradient), 2, Qt.DashLine)
                        self.preview_rect.setPen(pen)
                        self.addItem(self.preview_rect)
            else:
                super().mousePressEvent(event)
        except Exception as e:
            print(f"Error in mousePressEvent: {e}")
            self.cleanup_blob_drawing()

    def mouseMoveEvent(self, event):
        try:
            if self.drawing_blob and self.start_swimlane and self.preview_rect:
                pos = event.scenePos()
                self.end_swimlane = self.find_closest_swimlane(pos)
                if self.end_swimlane:
                    # Find closest outcome on hover swimlane
                    self.end_outcome = self.find_closest_outcome(pos, self.end_swimlane)
                    
                    # Calculate points for preview
                    points = self.calculate_blob_points(
                        self.start_swimlane,
                        self.end_swimlane,
                        self.start_outcome,
                        self.end_outcome
                    )
                    if points:
                        self.preview_rect.setPolygon(QPolygonF(points))
            else:
                super().mouseMoveEvent(event)
        except Exception as e:
            print(f"Error in mouseMoveEvent: {e}")
            self.cleanup_blob_drawing()

    def mouseReleaseEvent(self, event):
        try:
            if self.drawing_blob and self.start_swimlane:
                pos = event.scenePos()
                self.end_swimlane = self.find_closest_swimlane(pos)
                
                if self.end_swimlane and self.end_swimlane != self.start_swimlane:
                    # Find closest outcome on end swimlane
                    self.end_outcome = self.find_closest_outcome(pos, self.end_swimlane)
                    
                    # Calculate final points
                    points = self.calculate_blob_points(
                        self.start_swimlane,
                        self.end_swimlane,
                        self.start_outcome,
                        self.end_outcome
                    )
                    
                    if points:
                        # Create the blob
                        points_list = [(p.x(), p.y()) for p in points]
                        self.undo_stack.push(AddBlobCommand(self, points_list, ""))
                
                # Clean up
                self.cleanup_blob_drawing()
            else:
                super().mouseReleaseEvent(event)
        except Exception as e:
            print(f"Error in mouseReleaseEvent: {e}")
            self.cleanup_blob_drawing()

    def keyPressEvent(self, event):
        try:
            if event.key() == Qt.Key_Escape and self.drawing_blob:
                self.cleanup_blob_drawing()
            else:
                super().keyPressEvent(event)
        except Exception as e:
            print(f"Error in keyPressEvent: {e}")
            self.cleanup_blob_drawing()

    def add_swimlane(self, name, angle):
        try:
            swimlane = self.diagram.add_swimlane(name, angle)
            swimlane_item = SwimlaneItem(swimlane, self)
            self.addItem(swimlane_item)
            swimlane.line_item = swimlane_item
            return swimlane
        except ValueError as e:
            QMessageBox.warning(None, "Error", str(e))
            return None

    def add_outcome(self, swimlane_name, distance, label):
        try:
            outcome = self.diagram.add_outcome(swimlane_name, distance, label)
            outcome_item = OutcomeItem(outcome, self)
            outcome.item = outcome_item  # Store reference to the item
            self.addItem(outcome_item)
            return outcome_item
        except ValueError as e:
            QMessageBox.warning(None, "Error", str(e))
            return None

    def cleanup_blob_drawing(self):
        """Clean up all blob drawing state"""
        if self.preview_rect:
            self.removeItem(self.preview_rect)
            self.preview_rect = None
        self.start_swimlane = None
        self.start_outcome = None
        self.end_swimlane = None
        self.end_outcome = None
        self.drawing_blob = False
        
        # Re-enable selection
        for item in self.items():
            if isinstance(item, (SwimlaneItem, OutcomeItem)):
                item.setFlag(QGraphicsItem.ItemIsSelectable, True)
                if isinstance(item, SwimlaneItem):
                    item.update_selection_state()
    
    def start_drawing_blob(self):
        try:
            # Clean up any existing state
            self.cleanup_blob_drawing()
            
            # Start new blob drawing
            self.drawing_blob = True
            
            # Disable selection
            for item in self.items():
                if isinstance(item, (SwimlaneItem, OutcomeItem)):
                    item.setFlag(QGraphicsItem.ItemIsSelectable, False)
                    if isinstance(item, SwimlaneItem):
                        item.setSelected(False)
                        item.update_selection_state()
        except Exception as e:
            print(f"Error in start_drawing_blob: {e}")
            self.cleanup_blob_drawing()

    def finish_drawing_blob(self, points):
        try:
            if points:
                label, ok = QInputDialog.getText(None, "Add Blob", "Enter blob label (optional):")
                if ok:  # User clicked OK
                    # Convert QPointF to [x,y] list format
                    point_list = [[p.x(), p.y()] for p in points]
                    # Create and add the blob
                    command = AddBlobCommand(self, point_list, label)
                    self.undo_stack.push(command)
        except Exception as e:
            print(f"Error creating blob: {e}")
        finally:
            self.cleanup_blob_drawing()