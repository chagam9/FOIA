
import os

def replace_function():
    html_path = '/Users/agamhen/Desktop/html/index.html'
    js_path = '/Users/agamhen/Desktop/html/map_update.js'
    
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open(js_path, 'r', encoding='utf-8') as f:
        new_func = f.read()
        
    # Find start of function
    start_marker = 'function updateMapViz() {'
    start_idx = content.find(start_marker)
    
    if start_idx == -1:
        print("Could not find start of function")
        return
    
    # Find end of function (simple brace counting or manual inspection known end)
    # The old function matches exactly what we saw in view_file.
    # It ends with specific lines. We can just use brace counting.
    
    curr = start_idx
    brace_count = 0
    found_first_brace = False
    end_idx = -1
    
    for i in range(start_idx, len(content)):
        char = content[i]
        if char == '{':
            brace_count += 1
            found_first_brace = True
        elif char == '}':
            brace_count -= 1
        
        if found_first_brace and brace_count == 0:
            end_idx = i + 1 # Include the closing brace
            break
            
    if end_idx == -1:
        print("Could not find end of function")
        return
        
    print(f"Replacing chars {start_idx} to {end_idx}")
    
    new_content = content[:start_idx] + new_func + content[end_idx:]
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("Success")

if __name__ == '__main__':
    replace_function()
