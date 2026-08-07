import re
import subprocess
import os

old_file = "docs/repo_skeleton/semg_mfcv_ai_project_skeleton.md"
with open(old_file, "r") as f:
    lines = f.readlines()

old_tree_lines = lines[39:1382]
end_sections = lines[13538:]
intro_sections = lines[0:39]

annotations = {}
path_stack = []

for line in old_tree_lines:
    line_clean = line.rstrip('\n')
    if not line_clean: continue
    
    parts = line_clean.split('  # ')
    if len(parts) == 1:
        parts = line_clean.split('\t# ')
    if len(parts) == 1:
        parts = line_clean.split(' # ')
        
    tree_part = parts[0]
    annotation = "# " + parts[1].strip() if len(parts) > 1 else ""
    
    prefix_match = re.match(r'^([│ ├└─]*)(.*)', tree_part)
    if prefix_match:
        prefix = prefix_match.group(1)
        name = prefix_match.group(2).strip()
        
        depth = len(prefix) // 4
        
        while len(path_stack) > depth:
            path_stack.pop()
        
        path_stack.append(name)
        full_path = "/".join(path_stack)
        
        if annotation:
            annotations[full_path] = annotation

# Handle root renaming in annotations
renamed_annotations = {}
for path, anno in annotations.items():
    if path.startswith("semg-fatigue-platform"):
        new_path = "." + path[len("semg-fatigue-platform"):]
        renamed_annotations[new_path] = anno
    else:
        renamed_annotations[path] = anno

cmd = ['tree', '-a', '-I', '.git|node_modules|.next|.cache|__pycache__|.venv|venv|.cursor|.DS_Store|.claude|tests|*.pyc|.agents', '--dirsfirst', '--charset=utf-8']
result = subprocess.run(cmd, capture_output=True, text=True)
new_tree_lines = result.stdout.split('\n')

annotated_new_tree = []
path_stack = []

for line in new_tree_lines:
    if not line.strip() or line.startswith(' ' + ' ' * 10): 
        if "directories," in line: continue
        
    tree_part = line
    prefix_match = re.match(r'^([│ ├└─]*)(.*)', tree_part)
    if prefix_match:
        prefix = prefix_match.group(1)
        name = prefix_match.group(2).strip()
        
        depth = len(prefix) // 4
        
        while len(path_stack) > depth:
            path_stack.pop()
            
        path_stack.append(name)
        full_path = "/".join(path_stack)
        
        anno = renamed_annotations.get(full_path, "")
        
        if full_path == ".":
            tree_part = tree_part.replace(".", "semg-fatigue-platform/")
            anno = "# [ROOT] Monorepo"

        if anno:
            padding = max(1, 65 - len(tree_part))
            annotated_line = tree_part + " " * padding + anno
        else:
            if "day37" in full_path.lower(): anno = "# [MVP-2][MUST] Day 37 Quantitative Metrics"
            elif "day38" in full_path.lower(): anno = "# [MVP-2][MUST] Day 38 Cross-Dataset Transfer"
            elif "day39" in full_path.lower(): anno = "# [MVP-2][MUST] Day 39 Reproducibility & Governance"
            elif "day41" in full_path.lower(): anno = "# [MVP-2][MUST] Day 41 Portfolio Management"
            
            if anno:
                padding = max(1, 65 - len(tree_part))
                annotated_line = tree_part + " " * padding + anno
            else:
                annotated_line = tree_part
            
        annotated_new_tree.append(annotated_line)

with open(old_file, "w") as f:
    f.writelines(intro_sections)
    for line in annotated_new_tree:
        if line.strip() and not line.startswith("553 directories"):
            f.write(line + "\n")
    f.write("```\n\n")
    f.writelines(end_sections)

print(f"Updated {old_file}")
