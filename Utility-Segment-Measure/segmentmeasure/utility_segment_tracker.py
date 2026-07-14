from qgis.PyQt.QtCore import (
    Qt,
    QObject,
    QEvent,
    QPoint,
    QTimer
)

from qgis.PyQt.QtWidgets import (
    QDockWidget,
    QLabel,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QComboBox,
    QFrame,
    QCheckBox
)

from qgis.core import (
    QgsDistanceArea,
    QgsProject
)

from qgis.utils import iface


class HybridSegmentTrackerV27(QObject):

    def __init__(self):
        super().__init__()

        self.canvas = iface.mapCanvas()

        self.unit = "ft"

        self.live_segment_m = 0
        self.previous_segment_m = 0
        self.total_length_m = 0
        self.plugin = None

        self.unit_factors = {
            "m": 1,
            "ft": 3.28084,
            "in": 39.3701,
            "mm": 1000
        }

        self.distance_calculator = QgsDistanceArea()

        self.distance_calculator.setSourceCrs(
            self.canvas.mapSettings().destinationCrs(),
            QgsProject.instance().transformContext()
        )

        self.distance_calculator.setEllipsoid("WGS84")

        self.init_panel()
        self.create_floating_display()

        self.canvas.viewport().installEventFilter(self)

        self.canvas.mapToolSet.connect(
            self.tool_changed
        )

        iface.currentLayerChanged.connect(
            self.layer_changed
        )

        self.timer = QTimer()

        self.timer.timeout.connect(
            self.update_geometry
        )

        self.floating.hide()

        self.stop_tracking()

        if self.digitizing_active():
            self.start_tracking()

    # -----------------------------------------------------
    # UI
    # -----------------------------------------------------

    def init_panel(self):


        self.dock = QDockWidget(
            "Utility Segment Measure",
            iface.mainWindow()
        )



        self.widget = QWidget()

        self.layout = QVBoxLayout()

        self.label = QLabel(
            "Activate a digitizing tool..."
        )

        self.unit_selector = QComboBox()

        self.unit_selector.addItems(
            ["m", "ft", "in", "mm"]
        )

        self.unit_selector.setCurrentText("ft")

        self.unit_selector.currentTextChanged.connect(
            self.change_unit
        )

        self.cursor_checkbox = QCheckBox(
            "Enable Cursor Window"
        )

        self.cursor_checkbox.setChecked(True)

        self.cursor_checkbox.toggled.connect(
            self.toggle_cursor_window
        )

        self.reset_button = QPushButton(
            "Reset Display"
        )

        self.reset_button.clicked.connect(
            self.clear_display
        )
        self.close_button = QPushButton(
            "Exit Tracker"
        )

        self.close_button.clicked.connect(
            self.shutdown
        )


        self.layout.addWidget(self.label)
        self.layout.addWidget(self.unit_selector)
        self.layout.addWidget(self.cursor_checkbox)
        self.layout.addWidget(self.reset_button)
        self.layout.addWidget(self.close_button)

        self.widget.setLayout(
            self.layout
        )

        self.dock.setWidget(
            self.widget
        )

        iface.addDockWidget(
            Qt.RightDockWidgetArea,
            self.dock
        )

    # -----------------------------------------------------
    # Floating HUD
    # -----------------------------------------------------

    def create_floating_display(self):

        self.floating = QFrame(None)

        self.floating.setWindowFlags(
            Qt.Tool
            | Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
        )

        self.floating.setStyleSheet("""
            QFrame {
                background-color: rgba(30,30,30,220);
                color: white;
                border: 1px solid gray;
                border-radius: 5px;
            }

            QLabel {
                color: white;
                font-size: 10pt;
                padding: 4px;
            }
        """)

        layout = QVBoxLayout()

        self.floating_label = QLabel(
            "Waiting..."
        )

        layout.addWidget(
            self.floating_label
        )

        self.floating.setLayout(
            layout
        )

    # -----------------------------------------------------
    # Tracking Control
    # -----------------------------------------------------

    def start_tracking(self):

        if not self.timer.isActive():

            self.timer.start(100)

    def stop_tracking(self):

        if self.timer.isActive():

            self.timer.stop()

        self.clear_display()

    # -----------------------------------------------------
    # Helpers
    # -----------------------------------------------------

    def digitizing_active(self):

        tool = self.canvas.mapTool()

        return hasattr(
            tool,
            "points"
        )

    def get_capture_points(self):

        tool = self.canvas.mapTool()

        if not hasattr(
            tool,
            "points"
        ):
            return []

        try:

            return list(
                tool.points()
            )

        except Exception:

            return []

    # -----------------------------------------------------
    # Display
    # -----------------------------------------------------

    def refresh_text(self):

        factor = self.unit_factors[
            self.unit
        ]

        previous_segment = (
            self.previous_segment_m
            * factor
        )

        live_segment = (
            self.live_segment_m
            * factor
        )

        running_total = (
            self.total_length_m
            * factor
        )

        text = (
            f"Previous Segment: "
            f"{previous_segment:.2f} {self.unit}\n"
            f"Live Segment: "
            f"{live_segment:.2f} {self.unit}\n"
            f"Running Total: "
            f"{running_total:.2f} {self.unit}"
        )

        self.label.setText(
            text
        )

        self.floating_label.setText(
            text
        )

        self.floating.adjustSize()

    def clear_display(self):

        self.live_segment_m = 0
        self.previous_segment_m = 0
        self.total_length_m = 0

        self.refresh_text()

    # -----------------------------------------------------
    # Geometry Updates
    # -----------------------------------------------------

    def update_geometry(self):

        if not self.digitizing_active():

            self.stop_tracking()

            self.floating.hide()

            return

        points = self.get_capture_points()

        if len(points) == 0:

            self.clear_display()

            return

        if len(points) == 1:

            self.previous_segment_m = 0
            self.total_length_m = 0

            self.refresh_text()

            return

        total = 0

        for i in range(len(points) - 1):

            total += (
                self.distance_calculator.measureLine(
                    points[i],
                    points[i + 1]
                )
            )

        self.total_length_m = total

        self.previous_segment_m = (
            self.distance_calculator.measureLine(
                points[-2],
                points[-1]
            )
        )

        self.refresh_text()

    # -----------------------------------------------------
    # Events
    # -----------------------------------------------------

    def eventFilter(
        self,
        obj,
        event
    ):

        if (
            event.type()
            == QEvent.MouseButtonRelease
            and self.digitizing_active()
        ):

            self.update_geometry()

        if (
            event.type()
            == QEvent.MouseMove
        ):

            if not self.digitizing_active():

                return False

            if (
                self.cursor_checkbox.isChecked()
            ):

                cursor_global = (
                    self.canvas.mapToGlobal(
                        event.pos()
                    )
                )

                self.floating.move(
                    cursor_global
                    + QPoint(20, 20)
                )

            points = (
                self.get_capture_points()
            )

            if len(points) > 0:

                current_pos = (
                    self.canvas
                    .getCoordinateTransform()
                    .toMapCoordinates(
                        event.pos()
                    )
                )

                self.live_segment_m = (
                    self.distance_calculator.measureLine(
                        points[-1],
                        current_pos
                    )
                )

            else:

                self.live_segment_m = 0

        return False

    # -----------------------------------------------------
    # Actions
    # -----------------------------------------------------

    def set_plugin(self, plugin):

        self.plugin = plugin


    def shutdown(self):

        try:
            self.timer.stop()
        except Exception:
            pass

        try:
            self.floating.hide()
            self.floating.close()
        except Exception:
            pass

        try:
            self.dock.blockSignals(True)
            self.dock.close()
        except Exception:
            pass

        try:
            self.plugin.tracker = None
        except Exception:
            pass


    def change_unit(
        self,
        unit
    ):

        self.unit = unit

        self.refresh_text()

    def toggle_cursor_window(
        self,
        checked
    ):

        if not checked:

            self.floating.hide()

        elif self.digitizing_active():

            self.floating.show()

    def tool_changed(
        self,
        new_tool,
        old_tool
    ):

        if self.digitizing_active():

            self.start_tracking()

            if (
                self.cursor_checkbox.isChecked()
            ):

                self.floating.show()

        else:

            self.stop_tracking()

            self.floating.hide()

    def layer_changed(self):

        self.stop_tracking()

        self.floating.hide()