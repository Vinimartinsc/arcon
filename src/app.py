#!/usr/bin/env python3
"""
Image Archive Processor
Converts RAW images and applies metadata
Supports both CLI and web interface
"""

import os
import sys
import subprocess
import argparse
import logging
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify
import webbrowser
from threading import Timer

# import threading

app = Flask(__name__)

class ImageProcessor:
    def __init__(self, archive, output_dir, logs_dir="logs", quality=95, rotate=0, license_only=False,
                 creator="", credit="", copyright_name="", usage_terms="", license_url=""):
        self.archive = Path(archive)
        self.output_dir = Path(output_dir)
        self.logs_dir = Path(logs_dir)
        self.quality = quality
        self.rotate = rotate
        self.license_only = license_only
        self.year = datetime.now().year
        
        self.creator = creator
        self.credit = credit
        self.copyright_name = copyright_name
        self.usage_terms = usage_terms
        self.license_url = license_url
        
        self.log = []
        
    def log_message(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {msg}"
        self.log.append(log_line)
        print(log_line)
        
    def check_dependencies(self):
        deps = ['dcraw', 'convert', 'exiftool', 'find', 'xargs']
        missing = []
        
        for cmd in deps:
            if subprocess.run(['which', cmd], capture_output=True).returncode != 0:
                missing.append(cmd)
        
        if missing:
            raise RuntimeError(f"Missing dependencies: {', '.join(missing)}")
    
    def validate(self):
        if not self.archive.is_dir():
            raise ValueError(f"Archive folder not found: {self.archive}")
        
        if self.archive.resolve() == self.output_dir.resolve():
            raise ValueError("Output folder must be different from input archive folder")
        
        if not 1 <= self.quality <= 100:
            raise ValueError("Quality must be between 1 and 100")
        
        try:
            int(self.rotate)
        except ValueError:
            raise ValueError("Rotate must be an integer")
    
    def process(self):
        self.log_message("=" * 50)
        self.log_message(f"Started at: {datetime.now()}")
        self.log_message(f"Archive Name: {self.archive}")
        self.log_message(f"Image Quality: {self.quality}")
        self.log_message(f"Image Rotation: {self.rotate}")
        self.log_message(f"License Only: {self.license_only}")
        self.log_message("=" * 50)
        
        archive_name = self.archive.name
        base_public = self.output_dir / archive_name
        base_logs = self.logs_dir
        
        base_public.mkdir(parents=True, exist_ok=True)
        base_logs.mkdir(parents=True, exist_ok=True)
        
        log_file = base_logs / f"{archive_name}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
        
        if not self.license_only:
            self.process_images(base_public)
        else:
            self.log_message("License-only mode — skipping image conversion")
        
        self.apply_metadata(base_public)
        
        # Save log to file
        with open(log_file, 'w') as f:
            f.write('\n'.join(self.log))
        
        self.log_message("=" * 50)
        self.log_message(f"Completed at: {datetime.now()}")
        self.log_message(f"Log file: {log_file}")
        self.log_message("=" * 50)
        
        return '\n'.join(self.log)
    
    def process_images(self, base_public):
        for dossier in self.archive.iterdir():
            if not dossier.is_dir():
                continue
            
            self.log_message(f"Processing Dossier: {dossier.name}")
            
            for document in dossier.iterdir():
                if not document.is_dir():
                    continue
                
                self.log_message(f"  Processing Document: {document.name}")
                
                output_dir = base_public / dossier.name / document.name
                output_dir.mkdir(parents=True, exist_ok=True)
                
                nef_files = list(document.glob("*.NEF")) + list(document.glob("*.nef"))
                
                for raw in nef_files:
                    output_file = output_dir / f"{raw.stem}.jpg"
                    self.log_message(f"    Converting: {raw.name}")
                    
                    try:
                        # dcraw conversion
                        dcraw_cmd = ['dcraw', '-c', '-w', '-g', '2.2', '12.92', '-q', '3', '-H', '2', str(raw)]
                        dcraw_proc = subprocess.Popen(dcraw_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        
                        # ImageMagick conversion
                        convert_cmd = ['convert', '-']
                        if self.rotate != 0:
                            convert_cmd.extend(['-rotate', str(self.rotate)])
                        convert_cmd.extend([
                            '-colorspace', 'sRGB',
                            '-sampling-factor', '4:4:4',
                            '-quality', str(self.quality),
                            str(output_file)
                        ])
                        
                        convert_proc = subprocess.Popen(convert_cmd, stdin=dcraw_proc.stdout, 
                                                       stderr=subprocess.PIPE)
                        dcraw_proc.stdout.close()
                        
                        _, convert_err = convert_proc.communicate()
                        
                        if convert_proc.returncode != 0:
                            self.log_message(f"    ERROR: {convert_err.decode()}")
                    
                    except Exception as e:
                        self.log_message(f"    ERROR: {str(e)}")
    
    def apply_metadata(self, base_public):
        if not any([self.creator, self.credit, self.copyright_name, 
                   self.usage_terms, self.license_url]):
            self.log_message("No license metadata provided — skipping")
            return
        
        self.log_message("Writing XMP/IPTC metadata...")
        
        jpg_files = list(base_public.rglob("*.jpg")) + list(base_public.rglob("*.JPG"))
        
        if not jpg_files:
            self.log_message("No JPG files found to apply metadata")
            return
        
        cmd = ['exiftool', '-overwrite_original']
        
        if self.creator:
            cmd.extend([f'-XMP-dc:Creator={self.creator}', f'-IPTC:By-line={self.creator}'])
        if self.copyright_name:
            cmd.extend([f'-XMP-dc:Rights={self.copyright_name}', 
                       f'-IPTC:CopyrightNotice={self.copyright_name}'])
        if self.usage_terms:
            cmd.extend([f'-XMP-xmpRights:UsageTerms={self.usage_terms}',
                       f'-IPTC:SpecialInstructions={self.usage_terms}'])
        if self.license_url:
            cmd.extend([f'-XMP-xmpRights:WebStatement={self.license_url}',
                       f'-IPTC:Source={self.license_url}'])
        if self.credit:
            cmd.append(f'-IPTC:Credit={self.credit}')
        
        cmd.extend([str(f) for f in jpg_files])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                self.log_message(f"Metadata applied to {len(jpg_files)} files")
            else:
                self.log_message(f"ERROR applying metadata: {result.stderr}")
        except Exception as e:
            self.log_message(f"ERROR: {str(e)}")

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    try:
        data = request.json
        
        processor = ImageProcessor(
            archive=data['archive'],
            output_dir=data['outputDir'],
            logs_dir=data.get('logsDir', 'logs'),
            quality=int(data.get('quality', 95)),
            rotate=int(data.get('rotate', 0)),
            license_only=data.get('licenseOnly', False),
            creator=data.get('creator', ''),
            credit=data.get('credit', ''),
            copyright_name=data.get('copyright', ''),
            usage_terms=data.get('usageTerms', ''),
            license_url=data.get('licenseUrl', '')
        )
        
        processor.check_dependencies()
        processor.validate()
        log = processor.process()
        
        return jsonify({'success': True, 'log': log})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'log': getattr(processor, 'log', [])})

def run_cli():
    parser = argparse.ArgumentParser(
        description='Archive Converter - Bulk Convert Archive images and apply metadata'
    )
    
    parser.add_argument('--archive', required=True, help='Root archive folder (input)')
    parser.add_argument('--output', required=True, help='Output folder for processed images')
    parser.add_argument('--logs', default='logs', help='Logs directory (default: logs)')
    parser.add_argument('--quality', type=int, default=95, help='JPEG quality (1-100)')
    parser.add_argument('--rotate', type=int, default=0, help='Rotation angle in degrees')
    parser.add_argument('--license-only', action='store_true', help='Only apply license metadata')
    
    parser.add_argument('--creator', default='', help='Creator / author')
    parser.add_argument('--credit', default='', help='Credit line')
    parser.add_argument('--copyright', default='', help='Copyright holder')
    parser.add_argument('--usage-terms', default='', help='License / usage terms')
    parser.add_argument('--license-url', default='', help='License URL')
    
    # Remove the '--cli' argument before parsing
    args = parser.parse_args(sys.argv[2:])
    
    try:
        processor = ImageProcessor(
            archive=args.archive,
            output_dir=args.output,
            logs_dir=args.logs,
            quality=args.quality,
            rotate=args.rotate,
            license_only=args.license_only,
            creator=args.creator,
            credit=args.credit,
            copyright_name=args.copyright,
            usage_terms=args.usage_terms,
            license_url=args.license_url
        )
        
        processor.check_dependencies()
        processor.validate()
        processor.process()
        
    except Exception as e:
        print(f"[ERROR] {str(e)}", file=sys.stderr)
        sys.exit(1)

def run_web():
    import logging
    log = logging.getLogger('werkzeug')
    log.disabled = True
    log.setLevel(logging.ERROR)

    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: None

    
    print("Starting Archive Conversion Tool...")
    print("Open your browser: http://localhost:3932")
    Timer(1, webbrowser.open_new, args=("http://localhost:3932",)).start()
    print("\nTo stop the server, press Ctrl+C")
    app.run(host='0.0.0.0', port=3932, debug=False, use_reloader=False)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--':
        run_cli()
    else:
        run_web()