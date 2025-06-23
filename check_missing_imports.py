#!/usr/bin/env python3
import os
import re
from pathlib import Path

def extract_imports(file_path):
    """Extract all import statements from a file."""
    imports = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Match various import patterns
        # import ... from './path' or '../path'
        pattern1 = r"import\s+(?:.*?)\s+from\s+['\"]([./].*?)['\"]"
        # import './path' or '../path'
        pattern2 = r"import\s+['\"]([./].*?)['\"]"
        # require('./path') or require('../path')
        pattern3 = r"require\s*\(\s*['\"]([./].*?)['\"]"
        # export ... from './path' or '../path'
        pattern4 = r"export\s+(?:.*?)\s+from\s+['\"]([./].*?)['\"]"
        
        for pattern in [pattern1, pattern2, pattern3, pattern4]:
            matches = re.findall(pattern, content, re.MULTILINE)
            for match in matches:
                imports.append((match, file_path))
                
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return imports

def resolve_import_path(import_path, source_file):
    """Resolve relative import path to absolute path."""
    source_dir = os.path.dirname(source_file)
    
    # Handle import path without extension
    resolved_path = os.path.normpath(os.path.join(source_dir, import_path))
    
    # Check with various extensions
    extensions = ['', '.js', '.jsx', '.ts', '.tsx', '.json', '.css', '.scss', '.module.css', '.module.scss']
    
    for ext in extensions:
        test_path = resolved_path + ext
        if os.path.exists(test_path):
            return test_path
            
        # Also check if it's a directory with index file
        if os.path.isdir(resolved_path):
            for index_ext in ['.js', '.jsx', '.ts', '.tsx']:
                index_path = os.path.join(resolved_path, f'index{index_ext}')
                if os.path.exists(index_path):
                    return index_path
    
    return None

def main():
    frontend_src = "/Users/vishalbharti/Downloads/StickForStats_Migration/new_project/frontend/src"
    missing_imports = []
    
    # Find all JS/JSX/TS/TSX files
    js_files = []
    for root, dirs, files in os.walk(frontend_src):
        for file in files:
            if file.endswith(('.js', '.jsx', '.ts', '.tsx')):
                js_files.append(os.path.join(root, file))
    
    print(f"Checking {len(js_files)} JavaScript/TypeScript files...")
    print("=" * 80)
    
    # Check each file
    for file_path in js_files:
        imports = extract_imports(file_path)
        
        for import_path, source_file in imports:
            resolved = resolve_import_path(import_path, source_file)
            if resolved is None:
                relative_source = os.path.relpath(source_file, frontend_src)
                missing_imports.append({
                    'source_file': relative_source,
                    'import_path': import_path,
                    'full_source': source_file
                })
    
    # Group by source file and display results
    if missing_imports:
        print(f"\nFound {len(missing_imports)} missing imports:\n")
        
        # Group by source file
        by_file = {}
        for item in missing_imports:
            source = item['source_file']
            if source not in by_file:
                by_file[source] = []
            by_file[source].append(item['import_path'])
        
        # Display grouped results
        for source_file in sorted(by_file.keys()):
            print(f"\n{source_file}:")
            for import_path in sorted(set(by_file[source_file])):
                print(f"  - Missing: {import_path}")
        
        print(f"\n\nTotal missing imports: {len(missing_imports)}")
        print(f"Files with missing imports: {len(by_file)}")
    else:
        print("\nNo missing imports found!")

if __name__ == "__main__":
    main()