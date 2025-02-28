"""
SwimlaneItem class for visual representation of swimlanes.
"""

import math
from PyQt5.QtWidgets import QGraphicsLineItem, QGraphicsTextItem, QGraphicsItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QColor, QFont

from utils.geometry import calculate_point_on_line


class SwimlaneItem(QGraphicsLineItem):
    """
    Visual representation of a swimlane.
    
    Attributes:
        swimlane (Swimlane): The swimlane model
        diagram_scene (DiagramScene): The scene this item belongs to
        normal_pen (QPen): Pen for normal state
        hover_pen (QPen): Pen for hover state
        selected_pen (QPen): Pen for selected state
        label_item (QGraphicsTextItem): Text item for the label
        is_resizing (bool): Whether the swimlane is being resized
        is_rotating (bool): Whether the swimlane is being rotated
        start_pos (QPointF): Starting position for drag operations
        start_angle (float): Starting angle for rotation operations
        start_length (float): Starting length for resize operations
    """
    
    def __init__(self, swimlane, diagram_scene):
        """
        Initialize a new SwimlaneItem.
        
        Args:
            swimlane (Swimlane): The swimlane model
            diagram_scene (DiagramScene): The scene this item belongs to
        """
        # Calculate line points
        center = diagram_scene.center
        angle_rad = math.radians(swimlane.angle)
        end_point = calculate_point_on_line(center, angle_rad, diagram_scene.radius)
        
        super().__init__(center.x(), center.y(), end_point.x(), end_point.y())
        
        self.swimlane = swimlane
        self.diagram_scene = diagram_scene
        
        # Set up pens for different states
        self.normal_pen = QPen(swimlane.color, 2)
        self.hover_pen = QPen(swimlane.color, 3)
        self.selected_pen = QPen(swimlane.color, 3, Qt.DashLine)
        
        # Set initial pen
        self.setPen(self.normal_pen)
        
        # Make item selectable and movable
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        
        # Add label
        self.label_item = QGraphicsTextItem(swimlane.label)
        self.label_item.setFont(QFont("Arial", 10))
        self.label_item.setDefaultTextColor(swimlane.color)
        
        # Position label at the end of the line
        self.update_label_position()
        
        # Add to scene
        diagram_scene.addItem(self.label_item)
        
        # For drag and resize operations
        self.is_resizing = False
        self.is_rotating = False
        self.start_pos = None
        self.start_angle = None
        self.start_length = None
    
    def update_label_position(self):
        """
        Update the position of the label based on the line position.
        """
        line = self.line()
        # Position label at the end of the line with a small offset
        offset = 10
        angle_rad = math.atan2(line.dy(), line.dx())
        label_x = line.p2().x() + offset * math.cos(angle_rad)
        label_y = line.p2().y() + offset * math.sin(angle_rad)
        
        # Center the label on the point
        label_width = self.label_item.boundingRect().width()
        label_height = self.label_item.boundingRect().height()
        self.label_item.setPos(label_x - label_width / 2, label_y - label_height / 2)
    
    def get_color(self):
        """
        Get the color of the swimlane.
        
        Returns:
            QColor: The color of the swimlane
        """
        return self.swimlane.color
    
    def set_color(self, color):
        """
        Set the color of the swimlane.
        
        Args:
            color (QColor): The new color
        """
        self.swimlane.color = color
        self.normal_pen = QPen(color, 2)
        self.hover_pen = QPen(color, 3)
        self.selected_pen = QPen(color, 3, Qt.DashLine)
        self.setPen(self.isSelected() and self.selected_pen or self.normal_pen)
        self.label_item.setDefaultTextColor(color)
    
    def update_model(self):
        """
        Update the model based on the item's state.
        """
        # Update swimlane angle based on line angle
        line = self.line()
        dx = line.p2().x() - line.p1().x()
        dy = line.p2().y() - line.p1().y()
        angle_rad = math.atan2(dy, dx)
        self.swimlane.angle = math.degrees(angle_rad) % 360
    
    def mousePressEvent(self, event):
        """
        Handle mouse press events.
        
        Args:
            event (QGraphicsSceneMouseEvent): The mouse event
        """
        if event.button() == Qt.LeftButton:
            # Store starting position and state
            self.start_pos = event.pos()
            
            # Get line endpoints
            line = self.line()
            center = QPointF(line.p1())
            end = QPointF(line.p2())
            
            # Calculate distance from click to end point
            end_dist = (event.pos() - end).manhattanLength()
            
            # If click is near the end point, start resizing
            if end_dist < 20:  # Adjust threshold as needed
                self.is_resizing = True
                # Calculate current length
                dx = line.p2().x() - line.p1().x()
                dy = line.p2().y() - line.p1().y()
                self.start_length = math.sqrt(dx*dx + dy*dy)
                # Calculate current angle
                self.start_angle = math.atan2(dy, dx)
            else:
                # Otherwise, start rotating
                self.is_rotating = True
                # Calculate current angle
                dx = line.p2().x() - line.p1().x()
                dy = line.p2().y() - line.p1().y()
                self.start_angle = math.atan2(dy, dx)
            
            # Accept the event
            event.accept()
            
            # Call parent method
            super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """
        Handle mouse move events.
        
        Args:
            event (QGraphicsSceneMouseEvent): The mouse event
        """
        if self.is_resizing and self.start_pos is not None and self.start_angle is not None and self.start_length is not None:
            # Get line endpoints
            line = self.line()
            center = QPointF(line.p1())
            
            # Calculate vector from center to current mouse position
            dx = event.pos().x() - center.x()
            dy = event.pos().y() - center.y()
            
            # Calculate new length while maintaining angle
            new_length = math.sqrt(dx*dx + dy*dy)
            if new_length <= 0:
                new_length = 1  # Ensure positive length
            
            # Update line end point
            new_end = calculate_point_on_line(center, self.start_angle, new_length)
            self.setLine(center.x(), center.y(), new_end.x(), new_end.y())
            
            # Update label position
            self.update_label_position()
            
            # Update model
            self.update_model()
            
            # Accept the event
            event.accept()
        elif self.is_rotating and self.start_pos is not None and self.start_length is not None:
            # Get line endpoints
            line = self.line()
            center = QPointF(line.p1())
            
            # Calculate vector from center to current mouse position
            dx = event.pos().x() - center.x()
            dy = event.pos().y() - center.y()
            
            # Calculate new angle
            new_angle = math.atan2(dy, dx)
            
            # Update line end point, maintaining length
            new_end = calculate_point_on_line(center, new_angle, self.start_length)
            self.setLine(center.x(), center.y(), new_end.x(), new_end.y())
            
            # Update label position
            self.update_label_position()
            
            # Update model
            self.update_model()
            
            # Accept the event
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """
        Handle mouse release events.
        
        Args:
            event (QGraphicsSceneMouseEvent): The mouse event
        """
        if event.button() == Qt.LeftButton and (self.is_resizing or self.is_rotating):
            # Reset state
            self.is_resizing = False
            self.is_rotating = False
            self.start_pos = None
            self.start_angle = None
            self.start_length = None
            
            # Accept the event
            event.accept()
        
        # Call parent method
        super().mouseReleaseEvent(event)
    
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
        
        # Show menu
        menu.exec_(event.screenPos())
    
    def show_color_dialog(self):
        """
        Show color dialog for changing swimlane color.
        """
        from PyQt5.QtWidgets import QColorDialog
        
        color = QColorDialog.getColor(self.swimlane.color, None, "Select Color")
        if color.isValid():
            self.diagram_scene.change_item_color(self, color)
    
    def edit_label(self):
        """
        Edit the swimlane label.
        """
        from PyQt5.QtWidgets import QInputDialog
        
        text, ok = QInputDialog.getText(None, "Edit Label", "Label:", text=self.swimlane.label)
        if ok and text:
            self.swimlane.label = text
            self.label_item.setPlainText(text)
            self.update_label_position()
