#!/usr/bin/env python3
"""
Markdown to PDF Converter
Usage: python3 md2pdf.py [input.md] [output.pdf]
If no arguments provided, converts README.md to README.pdf
"""

import sys
import os
import subprocess
import tempfile
import markdown

def convert_md_to_pdf(input_file, output_file):
    """Convert a markdown file to PDF with professional styling."""
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        return False
    
    # Read the markdown file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
    except Exception as e:
        print(f"Error reading '{input_file}': {e}")
        return False
    
    # Convert markdown to HTML
    try:
        html = markdown.markdown(markdown_content)
    except Exception as e:
        print(f"Error converting markdown to HTML: {e}")
        return False
    
    # Add professional HTML structure and CSS styling
    html_with_style = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>''' + os.path.basename(input_file) + '''</title>
    <style>
        @page {
            margin: 1in;
            size: letter;
        }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; 
            margin: 0;
            padding: 0;
            line-height: 1.6; 
            color: #333;
            font-size: 12pt;
        }
        h1 { 
            color: #2c3e50; 
            border-bottom: 3px solid #3498db; 
            padding-bottom: 10px; 
            margin-top: 0;
            font-size: 24pt;
        }
        h2 { 
            color: #34495e; 
            margin-top: 30px; 
            border-left: 4px solid #3498db; 
            padding-left: 15px; 
            font-size: 18pt;
        }
        h3 {
            color: #34495e;
            margin-top: 25px;
            font-size: 14pt;
        }
        p {
            margin-bottom: 12px;
            text-align: justify;
        }
        code { 
            background-color: #f8f9fa; 
            padding: 2px 6px; 
            border-radius: 4px; 
            font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
            border: 1px solid #e9ecef;
            font-size: 10pt;
        }
        pre { 
            background-color: #f8f9fa; 
            padding: 15px; 
            border-radius: 6px; 
            overflow-x: auto; 
            border: 1px solid #e9ecef;
            margin: 16px 0;
            page-break-inside: avoid;
        }
        pre code {
            background: none;
            border: none;
            padding: 0;
            font-size: 10pt;
        }
        ul, ol { 
            margin-left: 20px; 
            margin-bottom: 16px;
        }
        li {
            margin-bottom: 5px;
        }
        strong {
            color: #2c3e50;
            font-weight: 600;
        }
        blockquote {
            border-left: 4px solid #ddd;
            margin: 16px 0;
            padding-left: 16px;
            color: #666;
            font-style: italic;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
            font-weight: 600;
        }
        .page-break {
            page-break-before: always;
        }
    </style>
</head>
<body>
''' + html + '''
</body>
</html>
'''
    
    # Create temporary HTML file
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as temp_html:
            temp_html.write(html_with_style)
            temp_html_path = temp_html.name
    except Exception as e:
        print(f"Error creating temporary HTML file: {e}")
        return False
    
    try:
        # Check if Chrome is available
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",  # macOS
            "/usr/bin/google-chrome",  # Linux
            "/usr/bin/google-chrome-stable",  # Linux alternative
            "/usr/bin/chromium-browser",  # Linux Chromium
            "chrome.exe",  # Windows (if in PATH)
            "google-chrome"  # Generic (if in PATH)
        ]
        
        chrome_path = None
        for path in chrome_paths:
            if os.path.exists(path) or (path.endswith('.exe') or '/' not in path):
                # For executables without full path, check if they're in PATH
                try:
                    subprocess.run([path, '--version'], capture_output=True, check=True)
                    chrome_path = path
                    break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
        
        if not chrome_path:
            print("Error: Google Chrome not found. Please install Chrome to convert to PDF.")
            return False
        
        # Convert HTML to PDF using Chrome headless
        file_url = f"file://{os.path.abspath(temp_html_path)}"
        cmd = [
            chrome_path,
            "--headless",
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--disable-extensions",
            "--no-sandbox",
            f"--print-to-pdf={os.path.abspath(output_file)}",
            file_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Successfully converted '{input_file}' to '{output_file}'")
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"PDF file size: {file_size:,} bytes")
            return True
        else:
            print(f"Error converting to PDF: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error during PDF conversion: {e}")
        return False
    
    finally:
        # Clean up temporary HTML file
        try:
            os.unlink(temp_html_path)
        except Exception:
            pass

def main():
    """Main function to handle command line arguments."""
    
    # Parse command line arguments
    if len(sys.argv) == 1:
        # Default: README.md -> README.pdf
        input_file = "README.md"
        output_file = "README.pdf"
    elif len(sys.argv) == 2:
        # Single argument: input.md -> input.pdf
        input_file = sys.argv[1]
        if input_file.endswith('.md'):
            output_file = input_file[:-3] + '.pdf'
        else:
            output_file = input_file + '.pdf'
    elif len(sys.argv) == 3:
        # Two arguments: input.md output.pdf
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    else:
        print("Usage: python3 md2pdf.py [input.md] [output.pdf]")
        print("Examples:")
        print("  python3 md2pdf.py                    # README.md -> README.pdf")
        print("  python3 md2pdf.py document.md        # document.md -> document.pdf")
        print("  python3 md2pdf.py input.md out.pdf   # input.md -> out.pdf")
        sys.exit(1)
    
    # Check if markdown module is available
    try:
        import markdown
    except ImportError:
        print("Error: 'markdown' module not found. Install it with: pip3 install markdown")
        sys.exit(1)
    
    # Convert the file
    success = convert_md_to_pdf(input_file, output_file)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
