"""
Predefined BOM data for the three projects.
Each project contains components with original MPN and alternate MPNs.
"""

from bms_bom_base import BMS_BOM_BASE

BOM_DATA = {
    "Battery Management System (BMS)": BMS_BOM_BASE,
    "Battery TCU": [
        {
            "original_mpn": "NTC-THERMISTOR-10K",
            "qty_per_unit": 4,
            "description": "NTC Thermistor 10kΩ",
            "alternates": ["NTC-10K-ALT"]
        },
        {
            "original_mpn": "ISO9050",
            "qty_per_unit": 2,
            "description": "Isolated Gate Driver",
            "alternates": ["TLP291-4", "TISO291-4"]
        },
        {
            "original_mpn": "BQ76PL536A-Q1",
            "qty_per_unit": 1,
            "description": "Battery Pack Monitor",
            "alternates": ["BQ76PL534A-Q1"]
        },
        {
            "original_mpn": "VREF-5V-SMD",
            "qty_per_unit": 2,
            "description": "Voltage Reference 5V",
            "alternates": ["LM4040A50", "TL431"]
        },
        {
            "original_mpn": "470UF-25V-CAP",
            "qty_per_unit": 3,
            "description": "Capacitor 470µF",
            "alternates": ["470UF-35V-CAP"]
        }
    ],
    "Vehicle TCU": [
        {
            "original_mpn": "ATSAME70",
            "qty_per_unit": 1,
            "description": "ARM MCU",
            "alternates": ["ATSAME70Q21A", "ATSAME70N21A"]
        },
        {
            "original_mpn": "MOSFET-N-CHANNEL-60V",
            "qty_per_unit": 4,
            "description": "N-Channel MOSFET",
            "alternates": ["IRF7532", "FDS4435BZ"]
        },
        {
            "original_mpn": "RELAY-12V-32A",
            "qty_per_unit": 2,
            "description": "Relay 12V 32A",
            "alternates": ["RELAY-12V-30A"]
        },
        {
            "original_mpn": "CONN-USB-MICRO",
            "qty_per_unit": 1,
            "description": "USB Micro Connector",
            "alternates": ["CONN-USB-MINI"]
        },
        {
            "original_mpn": "FUSE-10A-AMP",
            "qty_per_unit": 3,
            "description": "Fuse 10A",
            "alternates": ["FUSE-15A-AMP"]
        },
        {
            "original_mpn": "LED-RED-3MM",
            "qty_per_unit": 8,
            "description": "LED Red 3mm",
            "alternates": ["LED-RED-5MM"]
        }
    ]
}


def get_projects():
    """Return list of available projects."""
    return list(BOM_DATA.keys())


def get_bom(project_name):
    """Return BOM for specified project."""
    return BOM_DATA.get(project_name, [])
