/**
 * Frontend JavaScript for Shortage Management Application
 * Handles UI interactions, form validation, and API communication
 */

// DOM Elements
const projectSelect = document.getElementById('projectSelect');
const fileInput = document.getElementById('fileInput');
const fileName = document.getElementById('fileName');
const buildQty = document.getElementById('buildQty');
const wastagePercent = document.getElementById('wastagePercent');
const calculateBtn = document.getElementById('calculateBtn');
const statusMessage = document.getElementById('statusMessage');
const resultsSection = document.getElementById('resultsSection');
const resultsTableBody = document.getElementById('resultsTableBody');
const exportBtn = document.getElementById('exportBtn');
const summaryTotal = document.getElementById('summaryTotal');
const summaryShort = document.getElementById('summaryShort');
const summaryTotalShortage = document.getElementById('summaryTotalShortage');
const summaryConfig = document.getElementById('summaryConfig');

// Store current results for export
let currentResults = null;

/**
 * Initialize application
 */
document.addEventListener('DOMContentLoaded', function() {
    loadProjects();
    setupEventListeners();
});

/**
 * Set up event listeners
 */
function setupEventListeners() {
    fileInput.addEventListener('change', handleFileSelect);
    projectSelect.addEventListener('change', handleProjectSelect);
    calculateBtn.addEventListener('click', handleCalculate);
    exportBtn.addEventListener('click', handleExport);
}

/**
 * Load projects from API
 */
async function loadProjects() {
    try {
        const response = await fetch('/api/projects');
        const data = await response.json();
        
        if (data.status === 'success') {
            const projects = data.projects;
            projects.forEach(project => {
                const option = document.createElement('option');
                option.value = project;
                option.textContent = project;
                projectSelect.appendChild(option);
            });
            
            // Check BOM status for all projects
            await checkBOMStatus(projects);
        } else {
            showMessage('Failed to load projects', 'error');
            projectSelect.classList.add('error');
        }
    } catch (error) {
        showMessage('Error loading projects: ' + error.message, 'error');
        projectSelect.classList.add('error');
    }
}

/**
 * Handle file selection
 */
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        // Validate file type
        const allowedExtensions = ['xlsx', 'xls'];
        const fileExtension = file.name.split('.').pop().toLowerCase();
        
        if (!allowedExtensions.includes(fileExtension)) {
            showMessage('Please select a valid Excel file (.xlsx or .xls)', 'error');
            fileInput.value = '';
            fileName.textContent = 'Choose Excel file (.xlsx)';
            return;
        }
        
        // Validate file size (max 16MB)
        const maxSize = 16 * 1024 * 1024;
        if (file.size > maxSize) {
            showMessage('File size exceeds 16MB limit', 'error');
            fileInput.value = '';
            fileName.textContent = 'Choose Excel file (.xlsx)';
            return;
        }
        
        fileName.textContent = file.name;
        hideMessage();
    }
}

/**
 * Check BOM status for all projects and update select field color
 */
async function checkBOMStatus(projects) {
    let allSuccess = true;
    
    for (const project of projects) {
        try {
            const response = await fetch(`/api/bom-status/${encodeURIComponent(project)}`);
            const data = await response.json();
            
            if (data.status !== 'success') {
                allSuccess = false;
                break;
            }
        } catch (error) {
            allSuccess = false;
            break;
        }
    }
    
    // Update select field color
    projectSelect.classList.remove('success', 'error');
    if (allSuccess) {
        projectSelect.classList.add('success');
    } else {
        projectSelect.classList.add('error');
    }
}

/**
 * Validate form inputs
 */
function validateInputs() {
    const errors = [];
    
    if (!projectSelect.value) {
        errors.push('Please select a project');
    }
    
    if (!fileInput.files.length) {
        errors.push('Please upload an inventory Excel file');
    }
    
    const qty = parseInt(buildQty.value);
    if (!buildQty.value || qty <= 0) {
        errors.push('Build quantity must be a positive number');
    }
    
    const wastage = parseFloat(wastagePercent.value);
    if (wastagePercent.value === '' || isNaN(wastage) || wastage < 0 || wastage > 100) {
        errors.push('Wastage percentage must be between 0 and 100');
    }
    
    return errors;
}

/**
 * Handle project selection change
 */
function handleProjectSelect() {
    // Hide any previous results when the project changes
    hideMessage();
    resultsSection.style.display = 'none';
    currentResults = null;
    console.debug('Project changed to', projectSelect.value);
}

/**
 * Handle calculate button click
 */
async function handleCalculate() {
    // Validate inputs
    const errors = validateInputs();
    if (errors.length > 0) {
        showMessage(errors.join('; '), 'error');
        return;
    }
    
    // Show loading state
    calculateBtn.disabled = true;
    calculateBtn.innerHTML = '<span class="spinner"></span> Processing...';
    hideMessage();
    
    try {
        // Prepare form data
        const formData = new FormData();
        formData.append('project', projectSelect.value);
        formData.append('file', fileInput.files[0]);
        formData.append('build_qty', buildQty.value);
        formData.append('wastage_percent', wastagePercent.value);
        
        // Send request
        const response = await fetch('/api/calculate', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            currentResults = data;
            displayResults(data);
            showMessage('Calculation completed successfully', 'success');
            resultsSection.style.display = 'flex';
        } else {
            showMessage('Error: ' + data.message, 'error');
        }
    } catch (error) {
        showMessage('Error during calculation: ' + error.message, 'error');
    } finally {
        // Reset button state
        calculateBtn.disabled = false;
        calculateBtn.innerHTML = 'Calculate Shortages';
    }
}

/**
 * Display results in table
 */
function displayResults(data) {
    const results = data.results;
    const summary = data.summary;
    
    // Clear table
    resultsTableBody.innerHTML = '';
    
    // Populate table rows
    results.forEach(row => {
        const tr = document.createElement('tr');
        
        if (row.is_short) {
            tr.classList.add('short-row');
        }
        
        tr.innerHTML = `
            <td><strong>${escapeHtml(row.original_mpn)}</strong></td>
            <td>${escapeHtml(row.description)}</td>
            <td class="text-center">${row.qty_per_unit}</td>
            <td class="text-center">${row.total_available}</td>
            <td class="text-center">${row.required_qty}</td>
            <td class="text-center">${row.required_with_wastage}</td>
            <td class="text-center">
                <span class="shortage-badge ${row.shortage === 0 ? 'zero' : ''}">
                    ${row.shortage}
                </span>
            </td>
            <td><small>${escapeHtml(row.alternates)}</small></td>
        `;
        
        resultsTableBody.appendChild(tr);
    });
    
    // Update summary
    summaryTotal.textContent = summary.total_components;
    summaryShort.textContent = summary.components_short;
    summaryTotalShortage.textContent = summary.total_shortage;
    summaryConfig.textContent = `${data.build_qty} units / ${data.wastage_percent}% waste`;
}

/**
 * Handle export to Excel
 */
async function handleExport() {
    if (!currentResults) {
        showMessage('No results to export', 'error');
        return;
    }
    
    exportBtn.disabled = true;
    exportBtn.innerHTML = '<span class="spinner"></span> Exporting...';
    
    try {
        const response = await fetch('/api/export', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(currentResults)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Export failed');
        }
        
        // Download file
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        
        // Extract filename from Content-Disposition header
        const contentDisposition = response.headers.get('content-disposition');
        const filename = contentDisposition
            ? contentDisposition.split('filename=')[1].replace(/"/g, '')
            : 'shortage_report.xlsx';
        
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        showMessage('Excel file exported successfully', 'success');
    } catch (error) {
        showMessage('Error exporting file: ' + error.message, 'error');
    } finally {
        exportBtn.disabled = false;
        exportBtn.innerHTML = '📥 Export to Excel';
    }
}

/**
 * Show status message
 */
function showMessage(message, type = 'info') {
    statusMessage.textContent = message;
    statusMessage.className = `status-message ${type}`;
    statusMessage.style.display = 'flex';
}

/**
 * Hide status message
 */
function hideMessage() {
    statusMessage.style.display = 'none';
}

/**
 * Escape HTML special characters
 */
function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}
