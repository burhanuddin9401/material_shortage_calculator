"""
Flask backend for Shortage Management Application.
Handles file uploads, shortage calculations, and Excel export.
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import pandas as pd
from werkzeug.utils import secure_filename
from datetime import datetime
from io import BytesIO

from bom_data import get_projects, get_bom
from processor import process_inventory, map_alternates, calculate_shortage, format_output


# Initialize Flask app
app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create uploads folder if not exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename: str) -> bool:
    """Check if file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Render main page."""
    return render_template('index.html')


@app.route('/api/projects', methods=['GET'])
def api_get_projects():
    """Get list of available projects."""
    try:
        projects = get_projects()
        return jsonify({'status': 'success', 'projects': projects})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/bom', methods=['GET'])
def api_get_bom():
    """Get BOM for selected project."""
    try:
        project_name = request.args.get('project')
        if not project_name:
            return jsonify({'status': 'error', 'message': 'Project not specified'}), 400
        
        bom = get_bom(project_name)
        if not bom:
            return jsonify({'status': 'error', 'message': 'Project not found'}), 404
        
        return jsonify({'status': 'success', 'bom': bom})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/bom-status/<project_name>', methods=['GET'])
def api_get_bom_status(project_name):
    """Get BOM loading status for a project."""
    try:
        bom = get_bom(project_name)
        if bom and len(bom) > 0:
            return jsonify({'status': 'success', 'message': f'BOM loaded successfully with {len(bom)} components'})
        else:
            return jsonify({'status': 'error', 'message': 'BOM not found or empty'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/calculate', methods=['POST'])
def api_calculate():
    """Calculate shortages based on uploaded inventory and parameters."""
    try:
        # Validate form data
        file = request.files.get('file')
        if not file:
            return jsonify({'status': 'error', 'message': 'No file uploaded'}), 400
        
        filename = getattr(file, 'filename', '') or ''
        if not filename:
            return jsonify({'status': 'error', 'message': 'No file selected'}), 400
        
        if not allowed_file(filename):
            return jsonify({'status': 'error', 'message': 'File must be .xlsx or .xls'}), 400
        
        filename = secure_filename(filename)
        if not filename:
            return jsonify({'status': 'error', 'message': 'Invalid file name'}), 400
        
        # Get parameters
        project_name = request.form.get('project', '')
        try:
            build_qty = int(request.form.get('build_qty', 0))
            wastage_percent = float(request.form.get('wastage_percent', 0))
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Invalid build quantity or wastage percentage'}), 400
        
        if build_qty <= 0:
            return jsonify({'status': 'error', 'message': 'Build quantity must be greater than 0'}), 400
        
        if wastage_percent < 0 or wastage_percent > 100:
            return jsonify({'status': 'error', 'message': 'Wastage percentage must be between 0 and 100'}), 400
        
        if not project_name:
            return jsonify({'status': 'error', 'message': 'Project not selected'}), 400
        
        # Get BOM
        bom = get_bom(project_name)
        if not bom:
            return jsonify({'status': 'error', 'message': 'Project not found'}), 404
        
        # Save uploaded file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Process inventory
            inventory_df = process_inventory(filepath)
            
            # Map alternates and calculate available quantities
            mpn_inventory = map_alternates(bom, inventory_df)
            
            # Calculate shortages
            shortage_records = calculate_shortage(
                bom,
                mpn_inventory,
                build_qty,
                wastage_percent
            )
            
            # Format output
            result_df = format_output(shortage_records)
            
            # Prepare response
            response_data = {
                'status': 'success',
                'project': project_name,
                'build_qty': build_qty,
                'wastage_percent': wastage_percent,
                'results': result_df.to_dict('records'),
                'summary': {
                    'total_components': len(shortage_records),
                    'components_short': sum(1 for r in shortage_records if r['is_short']),
                    'total_shortage': round(sum(r['shortage'] for r in shortage_records), 2)
                }
            }
            
            return jsonify(response_data)
            
        finally:
            # Clean up uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Calculation error: {str(e)}'}), 500


@app.route('/api/export', methods=['POST'])
def api_export():
    """Export shortage results to Excel file."""
    try:
        # Get data from request
        data = request.json
        if not data or 'results' not in data:
            return jsonify({'status': 'error', 'message': 'No results to export'}), 400
        
        results = data['results']
        project = data.get('project', 'Shortage Report')
        build_qty = data.get('build_qty', '')
        wastage_percent = data.get('wastage_percent', '')
        
        # Create DataFrame
        df = pd.DataFrame(results)
        
        # Reorder columns for export
        export_columns = [
            'original_mpn',
            'description',
            'qty_per_unit',
            'total_available',
            'required_qty',
            'required_with_wastage',
            'shortage',
            'alternates'
        ]
        
        df = df[export_columns]
        
        # Rename columns for clarity
        df.columns = [
            'Original MPN',
            'Description',
            'Qty per Unit',
            'Total Available',
            'Required Qty',
            'Required with Wastage',
            'Shortage Qty',
            'Alternate MPNs'
        ]
        
        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Write results sheet
            df.to_excel(writer, sheet_name='Shortages', index=False)
            
            # Write summary sheet
            summary_data = {
                'Parameter': [
                    'Project',
                    'Build Quantity',
                    'Wastage %',
                    'Total Components',
                    'Components Short',
                    'Total Shortage Units',
                    'Report Generated'
                ],
                'Value': [
                    project,
                    build_qty,
                    wastage_percent,
                    len(df),
                    sum(df['Shortage Qty'] > 0),
                    df['Shortage Qty'].sum(),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Auto-adjust column widths
            for sheet in writer.sheets.values():
                for column in sheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    sheet.column_dimensions[column_letter].width = adjusted_width
        
        # Reset pointer
        output.seek(0)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'Shortage_Report_{timestamp}.xlsx'
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Export error: {str(e)}'}), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error."""
    return jsonify({'status': 'error', 'message': 'File too large (max 16MB)'}), 413


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
