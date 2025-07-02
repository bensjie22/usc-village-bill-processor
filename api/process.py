#!/usr/bin/env python3

import os
import json
import tempfile
import zipfile
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import PyPDF2
import re
from collections import defaultdict

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

class USCVillageProcessor:
    def __init__(self):
        self.bills_info = []
        self.created_files = []
        
    def process_batch_pdf(self, pdf_file, bill_type="electric", month_year="May 2025"):
        """Main processing function"""
        
        # Create temporary directory for processing
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Save uploaded file
            pdf_path = os.path.join(temp_dir, 'input.pdf')
            pdf_file.save(pdf_path)
            
            # Extract bill information
            self.bills_info = self.extract_all_bills(pdf_path, bill_type, month_year)
            
            # Create individual PDFs
            output_dir = os.path.join(temp_dir, 'output')
            os.makedirs(output_dir, exist_ok=True)
            self.created_files = self.create_individual_pdfs(pdf_path, output_dir)
            
            # Create summary report
            report_path = self.create_summary_report(output_dir, bill_type, month_year)
            
            # Create ZIP file
            zip_path = self.create_zip_package(output_dir, bill_type, month_year)
            
            return {
                'success': True,
                'total_bills': len(self.created_files),
                'zip_path': zip_path,
                'summary': f"Successfully separated {len(self.created_files)} {bill_type} bills for {month_year}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_all_bills(self, pdf_path, bill_type, month_year):
        """Extract information from all bills in the PDF"""
        
        bills_info = []
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                
                # Extract bill information based on type
                if bill_type.lower() == "electric":
                    bill_info = self.extract_electric_bill_info(text, page_num + 1, month_year)
                else:  # water
                    bill_info = self.extract_water_bill_info(text, page_num + 1, month_year)
                
                if bill_info:
                    bills_info.append(bill_info)
                else:
                    # Fallback naming
                    bills_info.append({
                        'page': page_num + 1,
                        'suite': f'Page{page_num + 1}',
                        'tenant': 'Unknown',
                        'bill_type': bill_type.title(),
                        'month_year': month_year
                    })
        
        return bills_info
    
    def extract_electric_bill_info(self, text, page_num, month_year):
        """Extract suite and tenant from SECOND LINE of electric bill header"""
        
        lines = text.split('\n')
        
        # Look for USC header first, then check the SECOND line after it
        for i, line in enumerate(lines):
            if 'USC' in line.upper() and 'FPM' in line.upper():
                # Found USC header, now look at next few lines
                for j in range(1, min(5, len(lines) - i)):
                    if i + j < len(lines):
                        candidate_line = lines[i + j]
                        
                        # Skip the first line (utility codes like UVIB4-MHC-Electric)
                        if j == 1 and re.search(r'[A-Z]{4,}-[A-Z]{3,}-', candidate_line):
                            continue  # This is the utility code line, skip it
                        
                        # Look for the actual suite-tenant pattern in second line
                        if j == 2 or 'Electric Bill' in candidate_line:
                            bill_info = self.parse_electric_line(candidate_line, page_num, month_year)
                            if bill_info:
                                return bill_info
        
        # Fallback: look for any line with suite-tenant pattern
        for line in lines:
            if re.search(r'\d{3,4}[A-Z]?-[A-Za-z]', line) and 'Electric' in line:
                bill_info = self.parse_electric_line(line, page_num, month_year)
                if bill_info and not self.is_utility_code(bill_info['tenant']):
                    return bill_info
        
        return None
    
    def parse_electric_line(self, line, page_num, month_year):
        """Parse a line for electric bill suite-tenant info"""
        
        # Patterns for electric bills
        patterns = [
            r'(\d{3,4}[A-Z]?)-([^_\n]+)_Electric_Bill',
            r'(\d{3,4}[A-Z]?)-([^E\n]+)\s*Electric\s+Bill',
            r'(\d{3,4}[A-Z]?)-([A-Za-z][^-\n]*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                suite, tenant = match.groups()
                tenant = self.clean_tenant_name(tenant)
                
                # Validate this is a real business name, not utility code
                if tenant and not self.is_utility_code(tenant):
                    return {
                        'page': page_num,
                        'suite': suite,
                        'tenant': tenant,
                        'bill_type': 'Electric',
                        'month_year': month_year
                    }
        
        return None
    
    def extract_water_bill_info(self, text, page_num, month_year):
        """Extract suite and tenant from consumption data in water bills"""
        
        # Water bills have suite-tenant info embedded in consumption data
        patterns = [
            r'[\d\.,\$]*(\d{3,4}[A-Z]?)\s*-\s*([A-Za-z][A-Za-z0-9\s&\']+)',
            r'[\d\.,\$]*(\d{3,4}[A-Z]?)-([A-Za-z][A-Za-z0-9\s&\']+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                suite, tenant = matches[0]
                tenant = self.clean_tenant_name(tenant)
                
                if tenant and not self.is_utility_code(tenant):
                    return {
                        'page': page_num,
                        'suite': suite,
                        'tenant': tenant,
                        'bill_type': 'Water',
                        'month_year': month_year
                    }
        
        return None
    
    def clean_tenant_name(self, tenant):
        """Clean up tenant name"""
        # Remove common suffixes
        tenant = re.sub(r'Electric.*$', '', tenant, flags=re.IGNORECASE)
        tenant = re.sub(r'_Bill.*$', '', tenant, flags=re.IGNORECASE)
        tenant = tenant.replace('_', ' ').strip()
        tenant = re.sub(r'[^\w\s&\'-]', '', tenant).strip()
        
        # Known cleanups
        cleanups = {
            'CreditUnion': 'Credit Union',
            'CafeDulce': 'Cafe Dulce',
            'RoskiEyeInst': 'RoskiEye',
            'JimmyJohn': 'Jimmy Johns',
            'BankofAmerica': 'Bank of America',
            'TraderJoes': 'Trader Joes',
            'CorePowerYoga': 'CorePower Yoga'
        }
        
        for old, new in cleanups.items():
            if old.lower() in tenant.lower():
                tenant = new
                break
        
        return tenant
    
    def is_utility_code(self, tenant):
        """Check if tenant name looks like a utility code instead of business name"""
        utility_codes = ['MHC', 'CIC', 'NBC', 'MRC', 'CRC', 'DPS']
        return tenant.upper() in utility_codes or len(tenant) <= 3
    
    def create_individual_pdfs(self, source_pdf_path, output_dir):
        """Split the source PDF into individual bill PDFs"""
        
        # Track filename usage to handle duplicates
        filename_counts = defaultdict(int)
        created_files = []
        
        with open(source_pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for bill in self.bills_info:
                page_num = bill['page'] - 1  # Convert to 0-based index
                
                # Create new PDF with single page
                pdf_writer = PyPDF2.PdfWriter()
                pdf_writer.add_page(pdf_reader.pages[page_num])
                
                # Generate filename with duplicate handling
                base_filename = self.generate_filename(bill)
                filename_key = f"{bill['suite']}-{bill['tenant']}"
                filename_counts[filename_key] += 1
                
                if filename_counts[filename_key] > 1:
                    name_part, ext = os.path.splitext(base_filename)
                    filename = f"{name_part} ({filename_counts[filename_key]}){ext}"
                else:
                    filename = base_filename
                
                filepath = os.path.join(output_dir, filename)
                
                # Write individual PDF
                with open(filepath, 'wb') as output_file:
                    pdf_writer.write(output_file)
                
                created_files.append({
                    'page': bill['page'],
                    'suite': bill['suite'],
                    'tenant': bill['tenant'],
                    'filename': filename,
                    'filepath': filepath
                })
        
        return created_files
    
    def generate_filename(self, bill_info):
        """Generate filename according to naming convention"""
        filename = f"USC Village - {bill_info['suite']}-{bill_info['tenant']} {bill_info['bill_type']} - {bill_info['month_year']}.pdf"
        
        # Make filename safe for filesystem
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = re.sub(r'\s+', ' ', filename)
        
        return filename
    
    def create_summary_report(self, output_dir, bill_type, month_year):
        """Create detailed summary report"""
        
        report_path = os.path.join(output_dir, "USC Village Bills Summary Report.txt")
        
        with open(report_path, 'w') as f:
            f.write("USC VILLAGE UTILITY BILLS SEPARATION REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Bill Type: {bill_type.title()} Bills\n")
            f.write(f"Billing Period: {month_year}\n")
            f.write(f"Total Bills Processed: {len(self.created_files)}\n\n")
            
            # Group by suite
            by_suite = defaultdict(list)
            for file_info in self.created_files:
                suite = file_info['suite']
                by_suite[suite].append(file_info)
            
            f.write("BILLS BY SUITE:\n")
            f.write("-" * 30 + "\n")
            
            for suite in sorted(by_suite.keys(), key=lambda x: (len(x), x)):
                files = by_suite[suite]
                f.write(f"\nSuite {suite} - {files[0]['tenant']}:\n")
                for file_info in files:
                    f.write(f"  Page {file_info['page']}: {file_info['filename']}\n")
            
            f.write(f"\nAll files saved to output directory\n")
            f.write("\nNaming Convention: USC Village - [Suite#]-[Tenant Name] [Bill Type] - [Month Year].pdf\n")
            f.write(f"\nProcessing completed successfully!\n")
        
        return report_path
    
    def create_zip_package(self, output_dir, bill_type, month_year):
        """Create ZIP package with all files"""
        
        zip_filename = f"USC Village {bill_type.title()} Bills - {month_year}.zip"
        zip_path = os.path.join(os.path.dirname(output_dir), zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, output_dir)
                    zipf.write(file_path, arcname)
        
        return zip_path

@app.route('/api/process', methods=['POST'])
def process_bills():
    """API endpoint to process uploaded PDF"""
    
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Get parameters
        bill_type = request.form.get('billType', 'electric')
        month_year = request.form.get('monthYear', 'May 2025')
        
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'success': False, 'error': 'Only PDF files are supported'}), 400
        
        # Process the file
        processor = USCVillageProcessor()
        result = processor.process_batch_pdf(file, bill_type, month_year)
        
        if result['success']:
            # Store zip path for download
            # In a real app, you'd store this in a database or cache
            return jsonify({
                'success': True,
                'total_bills': result['total_bills'],
                'summary': result['summary'],
                'download_url': f'/api/download/{os.path.basename(result["zip_path"])}'
            })
        else:
            return jsonify({'success': False, 'error': result['error']}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    """API endpoint to download processed ZIP file"""
    
    try:
        # In a real app, you'd retrieve the file path from storage
        # For now, we'll look in temp directories
        temp_dirs = [d for d in os.listdir('/tmp') if d.startswith('tmp')]
        
        for temp_dir in temp_dirs:
            zip_path = os.path.join('/tmp', temp_dir, filename)
            if os.path.exists(zip_path):
                return send_file(zip_path, as_attachment=True, download_name=filename)
        
        return jsonify({'error': 'File not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'USC Village Bill Processor'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

