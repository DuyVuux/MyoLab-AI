import os
import re

SKELETON_FILE = 'docs/repo_skeleton/semg_mfcv_ai_project_skeleton.md'
ROOT_DIR = '.'

IGNORE_DIRS = {
    '.git', '.github', '__pycache__', '.pytest_cache', 'venv', 'env',
    'day1_starter_pack', 'day2_starter_pack', 'day3_starter_pack',
    'day4_starter_pack', 'day5_starter_pack', 'day6_starter_pack',
    'day7_starter_pack', 'day8_starter_pack', 'day9_starter_pack',
    'day10_starter_pack', 'day11_starter_pack', 'day12_starter_pack',
    'logs', 'tmp', '.vscode', '.agents', 'node_modules', '.venv'
}

def parse_existing_skeleton(filepath):
    comments = {}
    with open(filepath, 'r') as f:
        content = f.read()

    # Find the tree block
    tree_match = re.search(r'```text\n(.*?)```', content, re.DOTALL)
    if not tree_match:
        return comments, content

    tree_text = tree_match.group(1)
    
    for line in tree_text.split('\n'):
        # Extract filename and comment
        # e.g., "├── .env.example                                                 # [MVP-1][MUST] Biến môi trường mẫu, không chứa secret thật"
        parts = line.split('#', 1)
        if len(parts) > 1:
            comment = parts[1].strip()
            # extract filename, remove tree characters ├── └── │
            filename_part = parts[0].strip()
            # clean up filename_part
            filename = re.sub(r'^[│├└─\s]+', '', filename_part)
            if filename:
                comments[filename] = comment
    return comments, content

def generate_tree(dir_path, prefix="", comments=None):
    if comments is None:
        comments = {}
    
    tree_str = ""
    try:
        entries = sorted(os.listdir(dir_path))
    except PermissionError:
        return ""
        
    # filter out ignored
    entries = [e for e in entries if e not in IGNORE_DIRS and not e.endswith('.pyc')]
    
    for i, entry in enumerate(entries):
        path = os.path.join(dir_path, entry)
        is_last = (i == len(entries) - 1)
        
        connector = "└── " if is_last else "├── "
        
        display_name = entry + "/" if os.path.isdir(path) else entry
        
        line = f"{prefix}{connector}{display_name}"
        
        # pad to column 65 for comments
        if display_name in comments or entry in comments:
            comment = comments.get(display_name, comments.get(entry))
            pad_len = max(1, 65 - len(line))
            line += " " * pad_len + f"# {comment}"
            
        tree_str += line + "\n"
        
        if os.path.isdir(path):
            new_prefix = prefix + ("    " if is_last else "│   ")
            tree_str += generate_tree(path, new_prefix, comments)
            
    return tree_str

def main():
    comments, original_content = parse_existing_skeleton(SKELETON_FILE)
    
    # Root comment
    root_line = "semg-fatigue-platform/                                           # [ROOT] Monorepo\n"
    
    tree_content = generate_tree(ROOT_DIR, comments=comments)
    full_tree = root_line + tree_content
    
    # Replace in file
    new_content = re.sub(r'```text\n.*?```', f'```text\n{full_tree}```', original_content, flags=re.DOTALL)
    
    with open(SKELETON_FILE, 'w') as f:
        f.write(new_content)
        
    print(f"Updated {SKELETON_FILE}")

if __name__ == '__main__':
    main()
