"""Configuration builder for creating and managing transform configurations."""

from las_trx.config import ReferenceConfig, TransformConfig
from las_trx.controllers import ConfigurationController
from las_trx.ui_interface import UIWidgetInterface


class ConfigurationBuilder:
    """Builder class for creating transformation configurations from UI state."""

    def __init__(self, ui_interface: UIWidgetInterface) -> None:
        """Initialize with UI interface.

        Args:
            ui_interface: Interface to access UI widget values
        """
        self.ui = ui_interface
        self.config_controller = ConfigurationController()

    def build_origin_config(self) -> ReferenceConfig:
        """Build origin reference configuration from UI state.

        Returns:
            Origin reference configuration
        """
        return self.config_controller.create_reference_config(
            ref_frame=self.ui.get_input_reference(),
            epoch=self.ui.get_input_epoch(),
            vd=self.ui.get_input_vertical_datum(),
            coord_type=self.ui.get_input_coordinate_type(),
        )

    def build_destination_config(self) -> ReferenceConfig:
        """Build destination reference configuration from UI state.

        Returns:
            Destination reference configuration
        """
        return self.config_controller.create_reference_config(
            ref_frame=self.ui.get_output_reference(),
            epoch=self.ui.get_output_epoch(),
            vd=self.ui.get_output_vertical_datum(),
            coord_type=self.ui.get_output_coordinate_type(),
        )

    def build_transform_config(self) -> TransformConfig:
        """Build complete transformation configuration from UI state.

        Returns:
            Complete transformation configuration
        """
        origin = self.build_origin_config()
        destination = self.build_destination_config()
        max_workers = self.config_controller.validate_core_count(self.ui.get_worker_cores())

        return self.config_controller.create_transform_config(
            origin=origin, destination=destination, max_workers=max_workers
        )

    def apply_config_to_ui(self, config: TransformConfig) -> None:
        """Apply configuration values to UI widgets.

        Args:
            config: Configuration to apply to UI
        """
        # Apply origin configuration
        origin = config.origin
        self.ui.set_input_reference(origin.ref_frame)
        self.ui.set_input_epoch(origin.epoch)
        self.ui.set_input_coordinate_type(origin.coord_type)
        self.ui.set_input_vertical_datum(origin.vd)

        # Apply destination configuration
        destination = config.destination
        self.ui.set_output_reference(destination.ref_frame)
        self.ui.set_output_epoch(destination.epoch)
        self.ui.set_output_coordinate_type(destination.coord_type)
        self.ui.set_output_vertical_datum(destination.vd)

        # Apply worker configuration
        self.ui.set_worker_cores(config.max_workers)

        # Enable epoch transformation if epochs differ
        if origin.epoch != destination.epoch:
            self.ui.set_epoch_transformation_enabled(True)

    def validate_configuration(self, config: TransformConfig) -> list[str]:
        """Validate configuration and return list of issues.

        Args:
            config: Configuration to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        issues = []

        # Check for file paths
        input_path = self.ui.get_input_file_path()
        output_path = self.ui.get_output_file_path()

        if not input_path.strip():
            issues.append("Input file path is required")

        if not output_path.strip():
            issues.append("Output file path is required")

        # Check for same input/output reference and coordinate type
        if (
            config.origin.ref_frame == config.destination.ref_frame
            and config.origin.coord_type == config.destination.coord_type
            and config.origin.vd == config.destination.vd
            and config.origin.epoch == config.destination.epoch
        ):
            issues.append("Origin and destination configurations are identical - no transformation needed")

        # Check for reasonable worker count
        if config.max_workers < 1:
            issues.append("Worker count must be at least 1")

        return issues
