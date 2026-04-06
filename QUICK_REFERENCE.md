# Shortage Management Application - Quick Reference

## One-Command Setup

```bash
cd "d:\Personal Docs\Python App\Shortage Management Application" && python -m pip install -r requirements.txt && python app.py
```

Then open: **http://localhost:5000**

---

## Essential Commands

| Task | Command |
|------|---------|
| **Install Dependencies** | `python -m pip install -r requirements.txt` |
| **Run Application** | `python app.py` |
| **Run Tests** | `python test_validation.py` |
| **Create Sample Data** | `python create_sample_inventory.py` |
| **Check Port 5000** | `netstat -ano \| findstr ":5000"` |
| **Stop Server** | `Ctrl+C` in terminal |

---

## File Locations

```
d:\Personal Docs\Python App\Shortage Management Application\
├── app.py                      # Main Flask server
├── bom_data.py                 # Project BOMs
├── processor.py                # Calculation logic
├── requirements.txt            # Dependencies
├── test_validation.py          # Test suite
├── create_sample_inventory.py  # Sample data generator
├── README.md                   # User guide
├── DEPLOYMENT_GUIDE.txt        # Detailed setup
├── QUICK_REFERENCE.md          # This file
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── script.js
└── uploads/                    # Temporary files
```

---

## Browser Access

- **Local**: http://localhost:5000
- **Alternate**: http://127.0.0.1:5000
- **External**: http://YOUR_IP:5000

---

## Excel File Format

Required columns (case-insensitive):
- **MPN** - Part number (text)
- **Qty** - Quantity available (number)

Example:
```
MPN              Qty
LTC6811-1        50
LTC6811-2        30
STM32L496ZGI6    25
CAN1050          40
```

---

## Projects Available

1. **Battery Management System (BMS)**
   - 5 components
   - Example alternates: LTC6811 family

2. **Battery TCU**
   - 5 components
   - Thermistors, gate drivers

3. **Vehicle TCU**
   - 6 components
   - MCU, MOSFETs, relays

---

## Feature Summary

✓ Upload Excel inventory files (.xlsx/.xls)
✓ Select predefined projects
✓ Input build quantity & wastage %
✓ Automatic alternate MPN aggregation
✓ Real-time shortage calculation
✓ Professional results table
✓ Excel export with summary
✓ Responsive web design
✓ No database required
✓ Zero configuration needed

---

## Calculation Formula

```
Required = Qty_Per_Board × Build_Qty
With Wastage = Required × (1 + Wastage%)
Total Available = SUM(Original_MPN + All_Alternates)
Shortage = MAX(0, With_Wastage - Total_Available)
```

---

## Example Scenario

**Input:**
- Project: BMS
- Build Qty: 50 units
- Wastage: 10%
- Inventory: LTC6811-1 (50), LTC6811-2 (30), LTC6812-1 (20)

**Calculation (for component with qty_per_unit=1):**
- Required: 1 × 50 = 50
- With Wastage: 50 × 1.10 = 55
- Total Available: 50 + 30 + 20 = 100
- **Shortage: 0** ✓

---

## Error Messages

| Error | Solution |
|-------|----------|
| "No file uploaded" | Click file area and select Excel file |
| "Project not selected" | Choose project from dropdown |
| "Invalid Excel format" | Ensure MPN and Qty columns exist |
| "Build qty must be > 0" | Enter positive integer |
| "Port already in use" | Change port in app.py or restart |
| "Module not found" | Run: `python -m pip install -r requirements.txt` |

---

## Performance

- **Calculation**: ~500ms-1000ms
- **Excel Export**: ~1-2 seconds
- **Page Load**: <1 second
- **File Upload**: <1 second (typical)

---

## Browser Compatibility

| Browser | Support |
|---------|---------|
| Chrome | ✓ Full support |
| Firefox | ✓ Full support |
| Edge | ✓ Full support |
| Safari | ✓ Full support |
| IE11 | ✗ Not supported |

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Space` on Select | Show project dropdown |
| `Click` file area | Select inventory file |
| `Enter` in fields | Submit calculation |
| `Ctrl+S` | Save exported Excel |

---

## Troubleshooting Quick Fixes

**App won't start:**
```bash
python -m pip install --upgrade setuptools
python app.py
```

**File upload fails:**
- File must be .xlsx or .xls
- Max 16MB
- Must have MPN and Qty columns

**No projects showing:**
```bash
python test_validation.py  # Check projects load
```

**Port error:**
Edit `app.py` last line, change port from 5000

---

## Data Privacy

- ✓ No cloud uploads
- ✓ Files processed locally
- ✓ Temporary files deleted after use
- ✓ No analytics tracking
- ✓ No logins required

---

## Tips & Tricks

1. **Save time:** Create a template Excel file with your common MPNs
2. **Test mode:** Use sample_inventory.xlsx to test before real data
3. **Export:** Download results for audit trail
4. **Batch processing:** Process multiple projects one after another
5. **Mobile:** Works on tablets (may need to zoom)

---

## File Size Limits

- Max Excel file: 16MB
- File timeout: 30 seconds
- Temp file cleanup: Automatic after each calculation

---

## Developer Notes

**Core Functions:**
- `load_bom()` - Get project BOM
- `process_inventory()` - Parse Excel file
- `map_alternates()` - Group alternate MPNs
- `calculate_shortage()` - Compute shortages
- `format_output()` - Prepare display data

**API Endpoints:**
- `GET /api/projects` - List projects
- `GET /api/bom?project=X` - Get BOM
- `POST /api/calculate` - Process calculation
- `POST /api/export` - Generate Excel

---

## Advanced: Add Custom Project

1. Edit `bom_data.py`
2. Add to `BOM_DATA` dictionary:

```python
"Custom Project": [
    {
        "original_mpn": "PART123",
        "qty_per_unit": 2,
        "description": "Description",
        "alternates": ["ALT1", "ALT2"]
    }
]
```

3. Restart app - shows in dropdown immediately

---

## Python Module Dependencies

```
Flask>=3.0.0        # Web framework
pandas>=2.1.0       # Data processing
openpyxl>=3.1.0     # Excel handling
python-dotenv>=1.0.0 # Config management
```

---

## Exit/Stop Application

**Method 1:** Press `Ctrl+C` in terminal
**Method 2:** Close terminal window
**Method 3:** Kill process on port 5000

---

**Status:** ✓ Production Ready
**Last Updated:** 2024
**Version:** 1.0

For detailed information, see README.md and DEPLOYMENT_GUIDE.txt
