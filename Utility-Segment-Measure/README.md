# Utility Segment Measure

Turn plan takeoffs into field-reference measurements while you digitize.

Utility Segment Measure is a QGIS plugin that provides real-time segment tracking and cumulative distance measurements while digitizing features.

## Coordinate Reference Systems

Utility Segment Measure is intended for use with any QGIS coordinate reference system. For utility locating, construction, and takeoff workflows, projected coordinate systems such as State Plane, HARN, WTM, and UTM are recommended for best accuracy and usability.

Measured distances can be displayed in:

- Feet (ft)
- Meters (m)
- Inches (in)
- Millimeters (mm)

## Features

- Previous Segment Length
- Live Segment Length
- Running Total Length
- Floating Cursor HUD
- Multiple Unit Support (ft, m, in, mm)
- Toolbar Toggle On/Off
- Exit Tracker Button
- Dockable and Floating Interface

## How It Works

While digitizing lines or polygons in QGIS, Utility Segment Measure automatically displays:

- Previous Segment Length
- Live Segment Length
- Running Total Length

Measurements update automatically as vertices are added, removed, completed, or cancelled, allowing users to convert plan-derived measurements into field-reference distances without interrupting the digitizing workflow.

## Intended Use

Utility Segment Measure was designed for:

- Utility locating
- Construction takeoffs
- Field layout planning
- Linear measurement workflows
- Infrastructure estimating
- Distance-based quantity verification

## Installation

1. Copy the `segmentmeasure` folder into your QGIS plugins directory.
2. Open **Plugins → Manage and Install Plugins**.
3. Enable **Utility Segment Measure**.
4. Click the Utility Segment Measure toolbar button to launch the tracker.

## Screenshots

Documentation screenshots will be added in a future release.

## Author

**Elliott Reams**  
**North of 29 LLC**

GitHub: https://github.com/northof29/utility-segment-measure

## License

Released under the GNU General Public License (GPL).