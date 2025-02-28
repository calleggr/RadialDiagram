"""
Utility functions for geometric calculations.
"""

import math
from PyQt5.QtCore import QPointF, QLineF


def calculate_point_on_line(start_point, angle_rad, distance):
    """
    Calculate a point on a line starting from start_point at the given angle and distance.
    
    Args:
        start_point (QPointF): The starting point
        angle_rad (float): The angle in radians
        distance (float): The distance from the starting point
        
    Returns:
        QPointF: The calculated point
    """
    x = start_point.x() + distance * math.cos(angle_rad)
    y = start_point.y() + distance * math.sin(angle_rad)
    return QPointF(x, y)


def distance_point_to_line(point, line_start, line_end):
    """Calculate the distance from a point to a line segment."""
    line = QLineF(line_start, line_end)
    normal = QLineF(line)
    normal.setAngle(normal.angle() + 90)
    normal.setLength(1)
    
    # Calculate the perpendicular distance
    dx = line_end.x() - line_start.x()
    dy = line_end.y() - line_start.y()
    
    if dx == 0 and dy == 0:  # Line is a point
        return QLineF(point, line_start).length()
    
    # Calculate the projection of the point onto the line
    t = ((point.x() - line_start.x()) * dx + (point.y() - line_start.y()) * dy) / (dx * dx + dy * dy)
    
    if t < 0:  # Point is beyond the start of the line
        return QLineF(point, line_start).length()
    elif t > 1:  # Point is beyond the end of the line
        return QLineF(point, line_end).length()
    
    # Projection falls on the line segment
    projection = QPointF(line_start.x() + t * dx, line_start.y() + t * dy)
    return QLineF(point, projection).length()


def calculate_arc_points(center, start_point, end_point, num_points=20):
    """Calculate points along an arc from start_point to end_point around center."""
    # Calculate angles
    start_angle = math.atan2(start_point.y() - center.y(), start_point.x() - center.x())
    end_angle = math.atan2(end_point.y() - center.y(), end_point.x() - center.x())
    
    # Ensure we go the shorter way around
    if abs(end_angle - start_angle) > math.pi:
        if end_angle > start_angle:
            start_angle += 2 * math.pi
        else:
            end_angle += 2 * math.pi
    
    # Calculate radius (use average of distances)
    radius1 = math.sqrt((start_point.x() - center.x())**2 + (start_point.y() - center.y())**2)
    radius2 = math.sqrt((end_point.x() - center.x())**2 + (end_point.y() - center.y())**2)
    radius = (radius1 + radius2) / 2
    
    # Generate points along the arc
    points = []
    for i in range(num_points):
        t = i / (num_points - 1)
        angle = start_angle * (1 - t) + end_angle * t
        x = center.x() + radius * math.cos(angle)
        y = center.y() + radius * math.sin(angle)
        points.append(QPointF(x, y))
    
    return points
