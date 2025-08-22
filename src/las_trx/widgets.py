"""Custom widgets for the application."""

import os

from PyQt6.QtWidgets import QSpinBox, QWidget


class WorkerCoresSpinBox(QSpinBox):
    """Custom spinbox for worker core selection with intelligent stepping."""
    
    def stepBy(self, steps: int) -> None:  # noqa: N802
        """Custom stepping behavior that doubles/halves values."""
        current = self.value()
        if steps > 0:
            # Step up: double the value (capped at maximum)
            new_value = min(self.maximum(), max(current * 2, current + 1))
        else:
            # Step down: halve the value (minimum 1)
            new_value = max(1, current // 2)
        self.setValue(new_value)


class WidgetFactory:
    """Factory for creating and configuring custom widgets."""
    
    @staticmethod
    def create_worker_cores_spinbox(
        parent: QWidget | None = None,
        max_cores: int | None = None,
        default_cores: int | None = None
    ) -> WorkerCoresSpinBox:
        """Create a configured worker cores spinbox.
        
        Args:
            parent: Parent widget
            max_cores: Maximum number of cores (defaults to CPU count)
            default_cores: Default number of cores (defaults to half CPU count)
            
        Returns:
            Configured WorkerCoresSpinBox
        """
        if max_cores is None:
            max_cores = os.cpu_count() or 1
            
        if default_cores is None:
            default_cores = max(1, max_cores // 2)
            
        spinbox = WorkerCoresSpinBox(parent)
        spinbox.setMinimum(1)
        spinbox.setMaximum(max_cores)
        spinbox.setValue(default_cores)
        
        return spinbox
    
    @staticmethod
    def replace_widget_in_layout(
        old_widget: QWidget, 
        new_widget: QWidget
    ) -> bool:
        """Replace a widget in its parent layout.
        
        Args:
            old_widget: Widget to replace
            new_widget: Widget to replace with
            
        Returns:
            True if replacement was successful, False otherwise
        """
        parent = old_widget.parent()
        if not parent:
            return False
            
        layout = parent.layout()
        if not layout:
            return False
        
        # Find the widget in the layout and replace it
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item and item.widget() == old_widget:
                # Copy properties
                new_widget.setObjectName(old_widget.objectName())
                new_widget.setStyleSheet(old_widget.styleSheet())
                
                # Replace in layout
                layout.removeWidget(old_widget)
                layout.insertWidget(i, new_widget)
                old_widget.deleteLater()
                
                return True
                
        return False