"""
ScopeBlobItem class for visual representation of scope blobs.
"""

import math
from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QBrush, QColor, QPainterPath

from utils.geometry import calculate_point_on_line


class ScopeBlobItem(QGraphicsPathItem):
    """
    Visual representation of a scope blob.
    
    Attributes:
        blob (ScopeBlob): The scope blob model
        diagram_scene (DiagramScene): The scene this item belongs to
        normal_pen (QPen): Pen for normal state
        hover_pen (QPen): Pen for hover state
        selected_pen (QPen): Pen for selected state
    """
    
    def __init__(self, blob, diagram_scene):
        """
        Initialize a new ScopeBlobItem.
        
        Args:
            blob (ScopeBlob): The scope blob model
            diagram_scene (DiagramScene): The scene this item belongs to
        """
        super().__init__()
        
        self.blob = blob
        self.diagram_scene = diagram_scene
        
        # Set up appearance
        self.setBrush(QBrush(blob.color.lighter(150)))
        
        # Set up pens for different states
        self.normal_pen = QPen(blob.color, 2)
        self.hover_pen = QPen(blob.color, 3)
        self.selected_pen = QPen(blob.color, 3, Qt.DashLine)
        
        # Set initial pen
        self.setPen(self.normal_pen)
        
        # Make item selectable
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        
        # Set z-value to be below outcomes but above swimlanes
        self.setZValue(-1)
        
        # Create path
        self.update_path()
    
    def update_path(self):
        """
        Update the path based on the blob's connected outcomes.
        """
        # Get outcomes
        start_outcome = self.diagram_scene.diagram.get_outcome_by_id(self.blob.start_outcome_id)
        end_outcome = self.diagram_scene.diagram.get_outcome_by_id(self.blob.end_outcome_id)
        
        if not start_outcome or not end_outcome:
            return
        
        # Get swimlanes
        start_swimlane = self.diagram_scene.diagram.get_swimlane_by_id(start_outcome.swimlane_id)
        end_swimlane = self.diagram_scene.diagram.get_swimlane_by_id(end_outcome.swimlane_id)
        
        if not start_swimlane or not end_swimlane:
            return
        
        # Calculate positions
        center = self.diagram_scene.center
        start_angle_rad = math.radians(start_swimlane.angle)
        end_angle_rad = math.radians(end_swimlane.angle)
        
        start_pos = calculate_point_on_line(center, start_angle_rad, start_outcome.distance)
        end_pos = calculate_point_on_line(center, end_angle_rad, end_outcome.distance)
        
        # Calculate control points for a smooth curve
        # Use the center as a reference point
        control1 = QPointF(
            start_pos.x() + (center.x() - start_pos.x()) * 0.5,
            start_pos.y() + (center.y() - start_pos.y()) * 0.5
        )
        
        control2 = QPointF(
            end_pos.x() + (center.x() - end_pos.x()) * 0.5,
            end_pos.y() + (center.y() - end_pos.y()) * 0.5
        )
        
        # Create path
        path = QPainterPath()
        path.moveTo(start_pos)
        path.cubicTo(control1, control2, end_pos)
        
        # Add some thickness to the path
        stroke_width = 20  # Adjust as needed
        
        # Calculate normal vectors to the path
        # This is a simplified approach - for a more accurate path,
        # you would need to calculate normals at multiple points
        dx1 = control1.x() - start_pos.x()
        dy1 = control1.y() - start_pos.y()
        length1 = math.sqrt(dx1 * dx1 + dy1 * dy1)
        
        dx2 = end_pos.x() - control2.x()
        dy2 = end_pos.y() - control2.y()
        length2 = math.sqrt(dx2 * dx2 + dy2 * dy2)
        
        if length1 > 0 and length2 > 0:
            # Calculate normal vectors (perpendicular to the path)
            nx1 = -dy1 / length1
            ny1 = dx1 / length1
            
            nx2 = -dy2 / length2
            ny2 = dx2 / length2
            
            # Create the thickened path
            offset_start1 = QPointF(start_pos.x() + nx1 * stroke_width, start_pos.y() + ny1 * stroke_width)
            offset_control1 = QPointF(control1.x() + nx1 * stroke_width, control1.y() + ny1 * stroke_width)
            offset_control2 = QPointF(control2.x() + nx2 * stroke_width, control2.y() + ny2 * stroke_width)
            offset_end1 = QPointF(end_pos.x() + nx2 * stroke_width, end_pos.y() + ny2 * stroke_width)
            
            offset_start2 = QPointF(start_pos.x() - nx1 * stroke_width, start_pos.y() - ny1 * stroke_width)
            offset_control1b = QPointF(control1.x() - nx1 * stroke_width, control1.y() - ny1 * stroke_width)
            offset_control2b = QPointF(control2.x() - nx2 * stroke_width, control2.y() - ny2 * stroke_width)
            offset_end2 = QPointF(end_pos.x() - nx2 * stroke_width, end_pos.y() - ny2 * stroke_width)
            
            # Create the final path
            path = QPainterPath()
            path.moveTo(offset_start1)
            path.cubicTo(offset_control1, offset_control2, offset_end1)
            path.lineTo(offset_end2)
            path.cubicTo(offset_control2b, offset_control1b, offset_start2)
            path.closeSubpath()
        
        self.setPath(path)
    
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
        
        # Add delete action
        delete_action = QAction("Delete", menu)
        menu.addAction(delete_action)
        delete_action.triggered.connect(self.delete_blob)
        
        # Show menu
        menu.exec_(event.screenPos())
    
    def show_color_dialog(self):
        """
        Show color dialog for changing blob color.
        """
        from PyQt5.QtWidgets import QColorDialog
        
        color = QColorDialog.getColor(self.blob.color, None, "Select Color")
        if color.isValid():
            self.diagram_scene.change_item_color(self, color)
    
    def delete_blob(self):
        """
        Delete this blob.
        """
        self.diagram_scene.delete_blob(self.blob)
