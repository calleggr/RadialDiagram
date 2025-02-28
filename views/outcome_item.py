"""
OutcomeItem class for visual representation of outcomes.
"""

import math
from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsItem
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QPen, QBrush, QColor, QFont

from utils.geometry import calculate_point_on_line


class OutcomeItem(QGraphicsEllipseItem):
    """
    Visual representation of an outcome.
    
    Attributes:
        outcome (Outcome): The outcome model
        diagram_scene (DiagramScene): The scene this item belongs to
        normal_pen (QPen): Pen for normal state
        hover_pen (QPen): Pen for hover state
        selected_pen (QPen): Pen for selected state
        label_item (QGraphicsTextItem): Text item for the label
    """
    
    def __init__(self, outcome, diagram_scene, radius=10):
        """
        Initialize a new OutcomeItem.
        
        Args:
            outcome (Outcome): The outcome model
            diagram_scene (DiagramScene): The scene this item belongs to
            radius (float, optional): Radius of the outcome circle. Defaults to 10.
        """
        # Find the swimlane
        swimlane = diagram_scene.diagram.get_swimlane_by_id(outcome.swimlane_id)
        if not swimlane:
            raise ValueError(f"Swimlane with ID {outcome.swimlane_id} not found")
        
        # Calculate position on the swimlane
        center = diagram_scene.center
        angle_rad = math.radians(swimlane.angle)
        distance = outcome.distance
        position = calculate_point_on_line(center, angle_rad, distance)
        
        # Create ellipse
        super().__init__(position.x() - radius, position.y() - radius, radius * 2, radius * 2)
        
        self.outcome = outcome
        self.diagram_scene = diagram_scene
        self.radius = radius
        
        # Set up appearance
        self.setBrush(QBrush(QColor(255, 255, 255)))
        
        # Set up pens for different states
        self.normal_pen = QPen(Qt.black, 1)
        self.hover_pen = QPen(Qt.black, 2)
        self.selected_pen = QPen(Qt.black, 2, Qt.DashLine)
        
        # Set initial pen
        self.setPen(self.normal_pen)
        
        # Make item selectable and movable
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        
        # Add label
        self.label_item = QGraphicsTextItem(outcome.label)
        self.label_item.setFont(QFont("Arial", 8))
        
        # Position label
        self.update_label_position()
        
        # Add to scene
        diagram_scene.addItem(self.label_item)
    
    def update_label_position(self):
        """
        Update the position of the label based on the ellipse position.
        """
        # Position label below the ellipse
        rect = self.rect()
        center_x = rect.x() + rect.width() / 2
        bottom_y = rect.y() + rect.height() + 5
        
        # Center the label on the point
        label_width = self.label_item.boundingRect().width()
        self.label_item.setPos(center_x - label_width / 2, bottom_y)
    
    def update_model(self):
        """
        Update the model based on the item's position.
        """
        # Calculate distance from center
        center = self.diagram_scene.center
        item_center = self.rect().center() + self.pos()
        dx = item_center.x() - center.x()
        dy = item_center.y() - center.y()
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Calculate angle to determine which swimlane we're on
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad) % 360
        
        # Find closest swimlane
        closest_swimlane = None
        min_angle_diff = float('inf')
        
        for swimlane in self.diagram_scene.diagram.swimlanes.values():
            angle_diff = min((swimlane.angle - angle_deg) % 360, (angle_deg - swimlane.angle) % 360)
            if angle_diff < min_angle_diff:
                min_angle_diff = angle_diff
                closest_swimlane = swimlane
        
        if closest_swimlane:
            # Update outcome model
            self.outcome.swimlane_id = closest_swimlane.id
            self.outcome.distance = distance
            
            # Snap to swimlane line
            self.snap_to_swimlane(closest_swimlane)
    
    def snap_to_swimlane(self, swimlane):
        """
        Snap the outcome to the swimlane line.
        
        Args:
            swimlane (Swimlane): The swimlane to snap to
        """
        center = self.diagram_scene.center
        angle_rad = math.radians(swimlane.angle)
        distance = self.outcome.distance
        position = calculate_point_on_line(center, angle_rad, distance)
        
        # Update ellipse position
        rect = self.rect()
        self.setPos(position.x() - rect.width() / 2 - rect.x(), 
                    position.y() - rect.height() / 2 - rect.y())
        
        # Update label position
        self.update_label_position()
    
    def itemChange(self, change, value):
        """
        Handle item changes.
        
        Args:
            change: The change type
            value: The new value
            
        Returns:
            The processed value
        """
        if change == QGraphicsItem.ItemSelectedChange:
            # Update pen based on selection state
            self.setPen(value and self.selected_pen or self.normal_pen)
        elif change == QGraphicsItem.ItemPositionChange and self.scene():
            # Update label position when item is moved
            self.update_label_position()
        elif change == QGraphicsItem.ItemPositionHasChanged and self.scene():
            # Update model when position has changed
            self.update_model()
        
        return super().itemChange(change, value)
    
    def hoverEnterEvent(self, event):
        """
        Handle hover enter events.
        
        Args:
            event: The hover event
        """
        if not self.isSelected():
            self.setPen(self.hover_pen)
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """
        Handle hover leave events.
        
        Args:
            event: The hover event
        """
        if not self.isSelected():
            self.setPen(self.normal_pen)
        super().hoverLeaveEvent(event)
    
    def contextMenuEvent(self, event):
        """
        Handle context menu events.
        
        Args:
            event: The context menu event
        """
        from PyQt5.QtWidgets import QMenu, QAction, QColorDialog
        
        menu = QMenu()
        
        # Add color action
        color_action = QAction("Change Color", menu)
        menu.addAction(color_action)
        color_action.triggered.connect(self.show_color_dialog)
        
        # Add edit label action
        edit_action = QAction("Edit Label", menu)
        menu.addAction(edit_action)
        edit_action.triggered.connect(self.edit_label)
        
        # Add delete action
        delete_action = QAction("Delete", menu)
        menu.addAction(delete_action)
        delete_action.triggered.connect(self.delete_outcome)
        
        # Show menu
        menu.exec_(event.screenPos())
    
    def show_color_dialog(self):
        """
        Show color dialog for changing outcome color.
        """
        from PyQt5.QtWidgets import QColorDialog
        
        color = QColorDialog.getColor(self.brush().color(), None, "Select Color")
        if color.isValid():
            self.diagram_scene.change_item_color(self, color)
    
    def edit_label(self):
        """
        Edit the outcome label.
        """
        from PyQt5.QtWidgets import QInputDialog
        
        text, ok = QInputDialog.getText(None, "Edit Label", "Label:", text=self.outcome.label)
        if ok and text:
            self.outcome.label = text
            self.label_item.setPlainText(text)
            self.update_label_position()
    
    def delete_outcome(self):
        """
        Delete this outcome.
        """
        self.diagram_scene.delete_outcome(self.outcome.id)
