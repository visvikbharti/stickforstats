#!/usr/bin/env python3
import os
import re
from pathlib import Path

def extract_imports_with_line_numbers(file_path):
    """Extract all import statements from a file with line numbers."""
    imports = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line_num, line in enumerate(lines, 1):
            # Match various import patterns
            # import ... from './path' or '../path'
            match1 = re.search(r"import\s+(?:.*?)\s+from\s+['\"]([./].*?)['\"]", line)
            # import './path' or '../path'
            match2 = re.search(r"import\s+['\"]([./].*?)['\"]", line)
            # require('./path') or require('../path')
            match3 = re.search(r"require\s*\(\s*['\"]([./].*?)['\"]", line)
            # export ... from './path' or '../path'
            match4 = re.search(r"export\s+(?:.*?)\s+from\s+['\"]([./].*?)['\"]", line)
            
            for match in [match1, match2, match3, match4]:
                if match:
                    imports.append({
                        'import_path': match.group(1),
                        'line_num': line_num,
                        'line': line.strip(),
                        'file_path': file_path
                    })
                
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

def find_similar_files(filename, search_dir):
    """Find files with similar names in the project."""
    similar = []
    basename = os.path.basename(filename).split('.')[0]
    
    for root, dirs, files in os.walk(search_dir):
        for file in files:
            if basename.lower() in file.lower() and file.endswith(('.js', '.jsx', '.ts', '.tsx')):
                similar.append(os.path.relpath(os.path.join(root, file), search_dir))
    
    return similar

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
        imports = extract_imports_with_line_numbers(file_path)
        
        for import_info in imports:
            import_path = import_info['import_path']
            resolved = resolve_import_path(import_path, file_path)
            if resolved is None:
                relative_source = os.path.relpath(file_path, frontend_src)
                import_info['relative_source'] = relative_source
                
                # Try to find similar files
                target_file = os.path.basename(import_path)
                if '/' in import_path:
                    target_file = import_path.split('/')[-1]
                    
                similar_files = find_similar_files(target_file, frontend_src)
                import_info['similar_files'] = similar_files
                
                missing_imports.append(import_info)
    
    # Display results
    if missing_imports:
        print(f"\nFound {len(missing_imports)} missing imports:\n")
        
        # Group by source file
        by_file = {}
        for item in missing_imports:
            source = item['relative_source']
            if source not in by_file:
                by_file[source] = []
            by_file[source].append(item)
        
        # Display grouped results with suggestions
        for source_file in sorted(by_file.keys()):
            print(f"\n{'='*80}")
            print(f"File: {source_file}")
            print(f"{'='*80}")
            
            for import_item in by_file[source_file]:
                print(f"\nLine {import_item['line_num']}: {import_item['line']}")
                print(f"Missing: {import_item['import_path']}")
                
                if import_item['similar_files']:
                    print(f"Possible alternatives found:")
                    for alt in import_item['similar_files'][:5]:  # Show top 5
                        print(f"  - {alt}")
        
        print(f"\n\n{'='*80}")
        print(f"Summary:")
        print(f"Total missing imports: {len(missing_imports)}")
        print(f"Files with missing imports: {len(by_file)}")
        
        # Generate fix suggestions
        print(f"\n\n{'='*80}")
        print("Fix suggestions:")
        print("1. For AuthContext imports, use: import { useAuth } from '../../context/AuthContext';")
        print("2. Missing service files (authService, contentService) need to be created")
        print("3. Missing component files (CaseStudies, LoadingOverlay, ProgressTracker) need to be created")
        print("4. Missing hook files (useDOEWebSocket, useRAGWebSocket) need to be created")
        
    else:
        print("\nNo missing imports found!")

if __name__ == "__main__":
    main()