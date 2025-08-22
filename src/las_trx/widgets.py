"""Custom widgets for the application."""

import os
import platform

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
            new_value = max(1, current // 2) if current > 1 else 1

        # Only change if the value actually changes
        if new_value != current:
            self.setValue(new_value)


class WidgetFactory:
    """Factory for creating and configuring custom widgets."""

    @staticmethod
    def create_worker_cores_spinbox(
        parent: QWidget | None = None, max_cores: int | None = None, default_cores: int | None = None
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

        # Apply platform-specific styling
        if platform.system() == "Windows":
            # Minimal Windows-specific styling - let Qt handle the layout
            spinbox.setStyleSheet("""
                QSpinBox {
                    border: 1px solid black;
                    padding-right: 15px;
                }
                QSpinBox::up-button {
                    subcontrol-origin: border;
                    subcontrol-position: top right;
                    width: 15px;
                }
                QSpinBox::down-button {
                    subcontrol-origin: border;
                    subcontrol-position: bottom right;
                    width: 15px;
                }
            """)
        else:
            # Standard styling for Mac/Linux
            spinbox.setStyleSheet("border: 1px solid black;")

        # Ensure proper button behavior
        spinbox.setButtonSymbols(QSpinBox.ButtonSymbols.UpDownArrows)
        spinbox.setCorrectionMode(QSpinBox.CorrectionMode.CorrectToNearestValue)

        return spinbox

    @staticmethod
    def replace_widget_in_layout(old_widget: QWidget, new_widget: QWidget) -> bool:
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
                # Only copy stylesheet if new widget doesn't have one
                if not new_widget.styleSheet():
                    new_widget.setStyleSheet(old_widget.styleSheet())

                # Replace in layout
                layout.removeWidget(old_widget)
                layout.insertWidget(i, new_widget)
                old_widget.deleteLater()

                return True

        return False
