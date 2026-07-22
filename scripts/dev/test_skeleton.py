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

def get_files_from_skeleton(filepath):
    files = set()
    with open(filepath, 'r') as f:
        content = f.read()

    tree_match = re.search(r'```text\n(.*?)```', content, re.DOTALL)
    if not tree_match:
        return files

    tree_text = tree_match.group(1)
    
    # Simple heuristic to extract paths from the tree block
    # By tracking the depth of each item
    path_stack = []
    
    for line in tree_text.split('\n'):
        if not line.strip() or line.startswith('semg-fatigue-platform/'):
            continue
            
        parts = line.split('#', 1)
        tree_part = parts[0].rstrip()
        
        # Calculate depth by counting prefix spaces and tree characters
        # Each level is 4 characters (e.g. "├── " or "│   ")
        prefix = re.match(r'^[│├└─\s]+', tree_part)
        if not prefix:
            continue
            
        prefix_len = len(prefix.group(0))
        depth = prefix_len // 4
        
        name = re.sub(r'^[│├└─\s]+', '', tree_part).strip()
        
        if not name:
            continue
            
        is_dir = name.endswith('/')
        name = name.rstrip('/')
        
        # Adjust stack
        while len(path_stack) > depth:
            path_stack.pop()
            
        path_stack.append(name)
        
        full_path = os.path.join(*path_stack)
        files.add(full_path)
        
    return files

def get_files_from_fs(dir_path):
    files = set()
    for root, dirs, filenames in os.walk(dir_path):
        # Exclude ignored dirs
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        rel_root = os.path.relpath(root, dir_path)
        if rel_root == '.':
            rel_root = ""
            
        for d in dirs:
            path = os.path.join(rel_root, d) if rel_root else d
            files.add(path)
            
        for f in filenames:
            if f.endswith('.pyc'):
                continue
            path = os.path.join(rel_root, f) if rel_root else f
            files.add(path)
            
    return files

def main():
    skel_files = get_files_from_skeleton(SKELETON_FILE)
    fs_files = get_files_from_fs(ROOT_DIR)
    
    # We only care about files tracked by skeleton which might have missed something
    missing_in_skel = fs_files - skel_files
    missing_in_fs = skel_files - fs_files
    
    print(f"Total entries in Skeleton: {len(skel_files)}")
    print(f"Total entries in Filesystem: {len(fs_files)}")
    
    if not missing_in_skel and not missing_in_fs:
        print("\n✅ MATCH: The skeleton is 100% perfectly synced with the actual filesystem structure!")
    else:
        if missing_in_skel:
            print(f"\n❌ ERROR: Found {len(missing_in_skel)} entries in filesystem but NOT in skeleton:")
            for item in sorted(list(missing_in_skel))[:20]:
                print(f"  - {item}")
            if len(missing_in_skel) > 20: print("  ... and more")
            
        if missing_in_fs:
            print(f"\n❌ ERROR: Found {len(missing_in_fs)} entries in skeleton but NOT in filesystem:")
            for item in sorted(list(missing_in_fs))[:20]:
                print(f"  - {item}")
            if len(missing_in_fs) > 20: print("  ... and more")

if __name__ == '__main__':
    main()
