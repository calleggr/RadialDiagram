"""
DiagramScene class for managing the visual representation of the diagram.
"""

import math
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsLineItem, QGraphicsEllipseItem, QMenu, QAction
from PyQt5.QtCore import Qt, QPointF, pyqtSignal
from PyQt5.QtGui import QPen, QColor, QBrush

from utils.geometry import calculate_point_on_line
from commands.add_blob_command import AddBlobCommand
from commands.delete_blob_command import DeleteBlobCommand
from commands.change_color_command import ChangeColorCommand


class DiagramScene(QGraphicsScene):
    """
    Scene for managing the visual representation of the diagram.
    
    Attributes:
        diagram (Diagram): The diagram model
        undo_stack (QUndoStack): Stack for undo/redo commands
        center (QPointF): Center point of the diagram
        radius (float): Radius of the diagram
        selected_item: Currently selected item
        start_swimlane: Starting swimlane for blob creation
        end_swimlane: Ending swimlane for blob creation
        start_outcome: Starting outcome for blob creation
        end_outcome: Ending outcome for blob creation
    """
    
    blob_created = pyqtSignal(object)
    blob_deleted = pyqtSignal(object)
    
    def __init__(self, diagram, undo_stack, parent=None):
        """
        Initialize a new DiagramScene.
        
        Args:
            diagram (Diagram): The diagram model
            undo_stack (QUndoStack): Stack for undo/redo commands
            parent (QObject, optional): Parent object. Defaults to None.
        """
        super().__init__(parent)
        self.diagram = diagram
        self.undo_stack = undo_stack
        self.center = diagram.center
        # Keep radius for other calculations but not for swimlane length
        self.radius = 300  # Default radius
        self.selected_item = None
        
        # For blob creation
        self.start_swimlane = None
        self.end_swimlane = None
        self.start_outcome = None
        self.end_outcome = None
        
        # Initialize the scene
        self.init_scene()
    
    def init_scene(self):
        """
        Initialize the scene with visual elements from the diagram model.
        """
        # Clear the scene
        self.clear()
        
        # Add center point indicator
        center_point = QGraphicsEllipseItem(self.center.x() - 5, self.center.y() - 5, 10, 10)
        center_point.setBrush(QBrush(Qt.black))
        self.addItem(center_point)
        
        # Add swimlanes
        for swimlane in self.diagram.swimlanes.values():
            self.add_swimlane_visual(swimlane)
        
        # Add outcomes
        for outcome in self.diagram.outcomes.values():
            self.add_outcome_visual(outcome)
        
        # Add blobs
        for blob in self.diagram.blobs:
            self.add_blob_visual(blob)
    
    def add_swimlane_visual(self, swimlane):
        """
        Add visual representation of a swimlane.
        
        Args:
            swimlane (Swimlane): The swimlane model
        """
        from views.swimlane_item import SwimlaneItem
        
        # Create swimlane item
        swimlane_item = SwimlaneItem(swimlane, self)
        self.addItem(swimlane_item)
        swimlane.item = swimlane_item
    
    def add_outcome_visual(self, outcome):
        """
        Add visual representation of an outcome.
        
        Args:
            outcome (Outcome): The outcome model
        """
        from views.outcome_item import OutcomeItem
        
        # Create outcome item
        outcome_item = OutcomeItem(outcome, self)
        self.addItem(outcome_item)
        outcome.item = outcome_item
    
    def add_blob_visual(self, blob):
        """
        Add visual representation of a blob.
        
        Args:
            blob (ScopeBlob): The blob model
        """
        from views.scope_blob_item import ScopeBlobItem
        
        # Create blob item
        blob_item = ScopeBlobItem(blob, self)
        self.addItem(blob_item)
        blob.polygon_item = blob_item
    
    def create_blob(self, start_point, end_point, label=""):
        """
        Create a new blob between two points.
        
        Args:
            start_point (QPointF): Starting point of the blob
            end_point (QPointF): Ending point of the blob
            label (str, optional): Text label for the blob. Defaults to "".
            
        Returns:
            ScopeBlob: The created blob
        """
        # Calculate blob points
        points = self.calculate_blob_points(start_point, end_point)
        
        # Create and execute command
        command = AddBlobCommand(self, points, label)
        self.undo_stack.push(command)
        
        # Emit signal
        self.blob_created.emit(command.blob)
        
        return command.blob
    
    def calculate_blob_points(self, start_point, end_point, width=40):
        """
        Calculate the points for a blob between two points.
        
        Args:
            start_point (QPointF): Starting point of the blob
            end_point (QPointF): Ending point of the blob
            width (float, optional): Width of the blob. Defaults to 40.
            
        Returns:
            list: List of points defining the blob's shape
        """
        # Calculate direction vector
        dx = end_point.x() - start_point.x()
        dy = end_point.y() - start_point.y()
        length = math.sqrt(dx*dx + dy*dy)
        
        if length < 0.001:  # Avoid division by zero
            return [start_point, end_point]
        
        # Normalize direction vector
        dx /= length
        dy /= length
        
        # Calculate perpendicular vector
        px = -dy * width/2
        py = dx * width/2
        
        # Calculate four corners of the blob
        points = [
            QPointF(start_point.x() + px, start_point.y() + py),
            QPointF(end_point.x() + px, end_point.y() + py),
            QPointF(end_point.x() - px, end_point.y() - py),
            QPointF(start_point.x() - px, start_point.y() - py)
        ]
        
        return points
    
    def delete_blob(self, blob_item):
        """
        Delete a blob from the diagram.
        
        Args:
            blob_item (ScopeBlobItem): The visual representation of the blob
        """
        # Create and execute command
        command = DeleteBlobCommand(self, blob_item)
        self.undo_stack.push(command)
        
        # Emit signal
        self.blob_deleted.emit(blob_item.blob)
    
    def change_item_color(self, item, new_color):
        """
        Change the color of an item.
        
        Args:
            item: The item whose color is being changed
            new_color: The new color for the item
        """
        # Get old color
        old_color = None
        if hasattr(item, 'get_color'):
            old_color = item.get_color()
        elif hasattr(item, 'color'):
            old_color = item.color
        elif hasattr(item, 'blob') and hasattr(item.blob, 'color'):
            old_color = item.blob.color
        
        if old_color:
            # Create and execute command
            command = ChangeColorCommand(item, old_color, new_color)
            self.undo_stack.push(command)
    
    def contextMenuEvent(self, event):
        """
        Handle context menu events.
        
        Args:
            event (QGraphicsSceneContextMenuEvent): The context menu event
        """
        # Get item at position
        item = self.itemAt(event.scenePos(), self.views()[0].transform())
        
        if item:
            # Create context menu based on item type
            menu = QMenu()
            
            # Check if item has its own context menu
            if hasattr(item, 'contextMenuEvent'):
                # Let the item handle its own context menu
                super().contextMenuEvent(event)
                return
            
            # Add common actions
            if hasattr(item, 'set_color') or hasattr(item, 'setColor'):
                color_action = QAction("Change Color", menu)
                menu.addAction(color_action)
                color_action.triggered.connect(lambda: self.show_color_dialog(item))
            
            if hasattr(item, 'blob'):
                delete_action = QAction("Delete Blob", menu)
                menu.addAction(delete_action)
                delete_action.triggered.connect(lambda: self.delete_blob(item))
            
            # Show menu if not empty
            if not menu.isEmpty():
                menu.exec_(event.screenPos())
            else:
                super().contextMenuEvent(event)
        else:
            super().contextMenuEvent(event)
    
    def start_drawing_blob(self):
        """
        Start drawing a blob.
        This method is called when the user clicks the 'Draw Blob' button.
        It sets up the scene to enter blob drawing mode.
        """
        # Reset state
        self.start_swimlane = None
        self.end_swimlane = None
        self.start_outcome = None
        self.end_outcome = None
        
        # Set cursor to indicate drawing mode
        for view in self.views():
            view.setCursor(Qt.CrossCursor)
        
        print("Blob drawing mode activated. Click on an outcome to start drawing.")
    
    def add_swimlane(self, label, angle, color=None, length=250):
        """
        Add a new swimlane to the diagram.
        
        Args:
            label (str): The label for the swimlane
            angle (float): The angle of the swimlane in degrees
            color (QColor, optional): The color of the swimlane. Defaults to None.
            length (float, optional): The length of the swimlane. Defaults to 250.
            
        Returns:
            Swimlane: The created swimlane
        """
        from models.swimlane import Swimlane
        
        # Create swimlane model
        swimlane = Swimlane(label=label, angle=angle, color=color, length=length)
        
        # Add to diagram
        self.diagram.add_swimlane(swimlane)
        
        # Add visual representation
        self.add_swimlane_visual(swimlane)
        
        return swimlane
    
    def add_outcome(self, swimlane_label, distance, label):
        """
        Add a new outcome to the diagram.
        
        Args:
            swimlane_label (str): The label of the swimlane to add the outcome to
            distance (float): The distance from the center
            label (str): The label for the outcome
            
        Returns:
            Outcome: The created outcome
        """
        from models.outcome import Outcome
        
        # Find swimlane by label
        swimlane = None
        for s in self.diagram.swimlanes.values():
            if s.label == swimlane_label:
                swimlane = s
                break
        
        if not swimlane:
            raise ValueError(f"Swimlane with label '{swimlane_label}' not found")
        
        # Create outcome model
        outcome = Outcome(swimlane_id=swimlane.id, distance=distance, label=label)
        
        # Add to diagram
        self.diagram.add_outcome(outcome)
        
        # Add visual representation
        self.add_outcome_visual(outcome)
        
        return outcome
    
    def show_color_dialog(self, item):
        """
        Show color dialog for changing item color.
        
        Args:
            item: The item whose color is being changed
        """
        from PyQt5.QtWidgets import QColorDialog
        
        # Get current color
        current_color = None
        if hasattr(item, 'get_color'):
            current_color = item.get_color()
        elif hasattr(item, 'color'):
            current_color = item.color
        elif hasattr(item, 'blob') and hasattr(item.blob, 'color'):
            current_color = item.blob.color
        
        if not current_color:
            current_color = QColor(Qt.red)
        
        # Show color dialog
        color = QColorDialog.getColor(current_color, None, "Select Color")
        if color.isValid():
            self.change_item_color(item, color)
