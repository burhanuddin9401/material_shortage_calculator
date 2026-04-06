"""
Create sample inventory Excel file for testing the application.
Run this script to generate sample_inventory.xlsx for testing.
"""

import pandas as pd
import os

def create_sample_inventory():
    """Create sample inventory Excel file."""
    
    # Sample inventory data with MPN and quantities
    mpn_list = [
        # Battery Management System components
        'LTC6811-1', 'LTC6811-2', 'LTC6812-1',
        'STM32L496ZGI6', 'STM32L496RGI6', 'STM32L476RGI6',
        'CAN1050', 'TJA1050', 'MCP2551',
        '100UF-50V-SMD', '100UF-63V-SMD', '10K-RESISTOR-0603',
        
        # Battery TCU components
        'NTC-THERMISTOR-10K', 'NTC-10K-ALT',
        'ISO9050', 'TLP291-4', 'BQ76PL536A-Q1',
        'VREF-5V-SMD', 'LM4040A50',
        '470UF-25V-CAP', '470UF-35V-CAP',
        
        # Vehicle TCU components
        'ATSAME70', 'ATSAME70Q21A',
        'MOSFET-N-CHANNEL-60V', 'IRF7532',
        'RELAY-12V-32A', 'RELAY-12V-30A',
        'CONN-USB-MICRO', 'CONN-USB-MINI',
        'FUSE-10A-AMP', 'FUSE-15A-AMP',
        'LED-RED-3MM', 'LED-RED-5MM',
    ]
    
    qty_list = [
        # BMS stock (lower for testing shortages)
        50, 30, 20,      # LTC6811 variants
        25, 15, 10,      # STM32 variants
        40, 35, 10,      # CAN transceivers
        25, 20, 50,      # Capacitors and resistors
        
        # TCU stock
        55, 45,          # Thermistors
        30, 25, 20,      # Gate drivers and monitors
        40, 35,          # Voltage references
        35, 28,          # Capacitors
        
        # Vehicle TCU stock
        40, 35,          # MCUs
        80, 70,          # MOSFETs
        45, 40,          # Relays
        50, 40,          # Connectors
        55, 45,          # Fuses
        100, 90,         # LEDs
    ]
    
    inventory_data = {
        'MPN': mpn_list,
        'Qty': qty_list
    }
    
    df = pd.DataFrame(inventory_data)
    
    # Save to Excel
    output_path = 'sample_inventory.xlsx'
    df.to_excel(output_path, sheet_name='Inventory', index=False)
    
    print(f"✓ Created {output_path}")
    print(f"  - Total entries: {len(df)}")
    print(f"  - Columns: {', '.join(df.columns)}")
    print(f"\nSample data:")
    print(df.head(10).to_string(index=False))
    
    return output_path

if __name__ == "__main__":
    try:
        create_sample_inventory()
        print("\n✓ Sample inventory file created successfully!")
        print("You can now upload this file in the web application.")
    except Exception as e:
        print(f"❌ Error creating sample inventory: {str(e)}")
        import traceback
        traceback.print_exc()
