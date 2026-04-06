"""
Core processing logic for shortage calculations.
Handles alternate MPN mapping, inventory processing, and shortage calculation.
"""

import pandas as pd
from typing import List, Dict, Tuple


def process_inventory(file_path: str) -> pd.DataFrame:
    """
    Load and process inventory Excel file.
    
    Args:
        file_path: Path to Excel file
        
    Returns:
        DataFrame with 'MPN' and 'Qty' columns (normalized)
        
    Raises:
        ValueError: If required columns not found
        Exception: If file cannot be read
    """
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Normalize column names (case-insensitive and trim whitespace)
        df.columns = df.columns.str.strip().str.upper()
        
        # Check for required columns
        required_cols = ['MPN', 'QTY']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"Excel file must contain columns: {required_cols}")
        
        # Select and rename columns
        df = df[['MPN', 'QTY']].copy()
        df.columns = ['MPN', 'Qty']
        
        # Clean MPN values
        df['MPN'] = df['MPN'].astype(str).str.strip()
        
        # Convert Qty to numeric, handle errors
        df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce').fillna(0).astype(int)
        
        # Remove rows with invalid MPN or zero qty
        df = df[(df['MPN'] != '') & (df['MPN'] != 'nan') & (df['Qty'] > 0)]
        
        return df
        
    except FileNotFoundError:
        raise Exception(f"File not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error processing inventory file: {str(e)}")


def map_alternates(bom: List[Dict], inventory_df: pd.DataFrame) -> Dict:
    """
    Map BOM components to inventory considering alternate MPNs.
    
    Args:
        bom: List of BOM dictionaries with original_mpn and alternates
        inventory_df: DataFrame with MPN and Qty columns
        
    Returns:
        Dictionary mapping original MPN to total available quantity
    """
    mpn_inventory = {}
    
    # Create inventory lookup (all MPNs in upper case)
    inventory_dict = {}
    for _, row in inventory_df.iterrows():
        mpn = row['MPN'].upper().strip()
        qty = row['Qty']
        # Aggregate if MPN exists multiple times
        inventory_dict[mpn] = inventory_dict.get(mpn, 0) + qty
    
    # For each BOM component, find total available quantity
    for component in bom:
        original_mpn = component['original_mpn'].upper().strip()
        alternates = [alt.upper().strip() for alt in component.get('alternates', [])]
        
        # Create list of all MPNs (original + alternates)
        all_mpns = [original_mpn] + alternates
        
        # Sum quantities from inventory for all matching MPNs
        total_qty = sum(inventory_dict.get(mpn, 0) for mpn in all_mpns)
        
        mpn_inventory[original_mpn] = total_qty
    
    return mpn_inventory


def calculate_shortage(
    bom: List[Dict],
    mpn_inventory: Dict,
    build_qty: int,
    wastage_percent: float
) -> List[Dict]:
    """
    Calculate shortage for each BOM component.
    
    Args:
        bom: List of BOM dictionaries
        mpn_inventory: Dict mapping MPN to available quantity
        build_qty: Number of units to build
        wastage_percent: Wastage percentage (e.g., 10 for 10%)
        
    Returns:
        List of shortage records with detailed information
    """
    shortage_records = []
    wastage_multiplier = 1 + (wastage_percent / 100)
    
    for component in bom:
        original_mpn = component['original_mpn'].upper().strip()
        qty_per_unit = component.get('qty_per_unit', 0)
        description = component.get('description', '')
        alternates = component.get('alternates', [])
        
        # Calculate required quantity
        required_qty = qty_per_unit * build_qty
        
        # Apply wastage
        required_with_wastage = required_qty * wastage_multiplier
        
        # Get available quantity
        total_available = mpn_inventory.get(original_mpn, 0)
        
        # Calculate shortage
        shortage = max(0, required_with_wastage - total_available)
        
        record = {
            'original_mpn': original_mpn,
            'description': description,
            'qty_per_unit': qty_per_unit,
            'total_available': int(total_available),
            'required_qty': int(required_qty),
            'required_with_wastage': round(required_with_wastage, 2),
            'shortage': round(shortage, 2),
            'alternates': ', '.join(alternates) if alternates else 'None',
            'is_short': shortage > 0
        }
        
        shortage_records.append(record)
    
    return shortage_records


def format_output(shortage_records: List[Dict]) -> pd.DataFrame:
    """
    Format shortage records into output DataFrame.
    
    Args:
        shortage_records: List of shortage calculation records
        
    Returns:
        Formatted DataFrame for display
    """
    df = pd.DataFrame(shortage_records)
    
    # Reorder columns for clarity
    column_order = [
        'original_mpn',
        'description',
        'qty_per_unit',
        'total_available',
        'required_qty',
        'required_with_wastage',
        'shortage',
        'alternates',
        'is_short'
    ]
    
    df = df[column_order]
    
    return df
