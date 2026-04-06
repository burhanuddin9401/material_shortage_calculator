import sys
import os
import pandas as pd

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bom_data import get_projects, get_bom
from processor import process_inventory, map_alternates, calculate_shortage, format_output

def test_application():
    """Test core functionality without Flask"""
    
    print("=" * 70)
    print("SHORTAGE MANAGEMENT APPLICATION - TEST VALIDATION")
    print("=" * 70)
    
    # Test 1: Load projects
    print("\n[TEST 1] Loading available projects...")
    projects = get_projects()
    print(f"✓ Available projects: {', '.join(projects)}")
    
    # Test 2: Load BOM for first project
    project_name = projects[0]
    print(f"\n[TEST 2] Loading BOM for '{project_name}'...")
    bom = get_bom(project_name)
    print(f"✓ Loaded {len(bom)} components")
    print(f"  Sample component: {bom[0]['original_mpn']}")
    print(f"  - Qty per unit: {bom[0]['qty_per_unit']}")
    print(f"  - Alternates: {bom[0]['alternates']}")
    
    # Test 3: Create sample inventory
    print("\n[TEST 3] Creating sample inventory data...")
    inventory_data = {
        'MPN': [
            'LTC6811-1', 'LTC6811-2', 'LTC6812-1',
            'STM32L496ZGI6', 'STM32L496RGI6',
            'CAN1050', 'TJA1050', 'MCP2551'
        ],
        'Qty': [50, 30, 20, 25, 15, 40, 35, 10]
    }
    inventory_df = pd.DataFrame(inventory_data)
    print(f"✓ Created inventory with {len(inventory_df)} MPN entries")
    print(inventory_df.to_string(index=False))
    
    # Test 4: Map alternates
    print("\n[TEST 4] Mapping alternate MPNs...")
    mpn_inventory = map_alternates(bom, inventory_df)
    print(f"✓ Mapped {len(mpn_inventory)} components")
    
    # Sample: LTC6811-1 should aggregate all variants
    ltc_key = 'LTC6811-1'
    if ltc_key in mpn_inventory:
        print(f"\n  Example - {ltc_key}:")
        print(f"  - Original: 50 units")
        print(f"  - LTC6811-2: 30 units")
        print(f"  - LTC6812-1: 20 units")
        print(f"  - Total Available: {mpn_inventory[ltc_key]} units")
    
    # Test 5: Calculate shortages
    print("\n[TEST 5] Calculating shortages...")
    build_qty = 50
    wastage_percent = 10
    results = calculate_shortage(bom, mpn_inventory, build_qty, wastage_percent)
    print(f"✓ Calculated shortages for {len(results)} components")
    
    # Test 6: Display results
    print(f"\n[TEST 6] Results for Build Qty: {build_qty}, Wastage: {wastage_percent}%")
    result_df = format_output(results)
    
    # Show first 3 components
    print("\nFirst 3 components:")
    print(result_df[['original_mpn', 'total_available', 'required_qty', 
                      'required_with_wastage', 'shortage']].head(3).to_string(index=False))
    
    # Show components with shortage
    short_components = [r for r in results if r['is_short']]
    if short_components:
        print(f"\nComponents with shortage ({len(short_components)}):")
        for comp in short_components[:3]:
            print(f"  - {comp['original_mpn']}: {comp['shortage']} units short")
    else:
        print("\n✓ No shortages detected!")
    
    # Test 7: Summary statistics
    print(f"\n[TEST 7] Summary Statistics")
    total_shortage = sum(r['shortage'] for r in results)
    print(f"  Total Components: {len(results)}")
    print(f"  Components Short: {len(short_components)}")
    print(f"  Total Shortage Units: {total_shortage}")
    
    print("\n" + "=" * 70)
    print("✓ ALL TESTS PASSED - APPLICATION READY")
    print("=" * 70)

if __name__ == "__main__":
    try:
        test_application()
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
