import os

CASE_DIR = "case_studies"

# Markers that indicate the END of the header section. 
# We will discard everything before the last occurrence of these markers in the top section.
HEADER_END_MARKERS = [
    "[联系销售](/landing/feishu_contact_sales",
    "[免费试用](https://www.feishu.cn/accounts/page/ug_register",
    "[下载飞书](https://www.feishu.cn/download)",
    "[登录](https://login.feishu.cn/suite/passport/page/login"
]

def clean_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Check if empty
    if not lines: return

    # We want to keep the metadata (Lines starting with # or URL:) likely at the top 
    # but the scraper puts them at lines 0 and 2.
    # The junk starts after that.
    
    # Strategy:
    # 1. Separate the preamble (Title, URL) from the Body.
    # 2. Clean the Body.
    # 3. Reassemble.
    
    preamble = []
    body = []
    
    # Heuristic: First few lines are title/url until we hit the image or junk
    # The scraper writes:
    # Line 1: # Title
    # Line 2: Empty
    # Line 3: URL: ...
    # Line 4: Empty
    # Line 5: Body starts
    
    body_start_index = 0
    if len(lines) > 0 and lines[0].startswith("# "):
        preamble.append(lines[0])
        body_start_index = 1
        
    for i in range(body_start_index, len(lines)):
        line = lines[i]
        if line.startswith("URL:"):
            preamble.append(line)
        elif line.strip() == "":
            preamble.append(line)
        else:
            # Found start of body content
            body = lines[i:]
            break
            
    # Join body to search
    body_text = "".join(body)
    
    cutoff_index = -1
    
    # Find the last occurrence of any marker in the first 2000 characters
    # (Header shouldn't be deeper than that)
    search_scope_len = min(len(body_text), 3000)
    search_scope = body_text[:search_scope_len]
    
    found_marker = False
    for marker in HEADER_END_MARKERS:
        idx = search_scope.rfind(marker)
        if idx != -1:
            # Find the end of this line
            line_end = search_scope.find('\n', idx)
            if line_end != -1:
                cutoff_index = max(cutoff_index, line_end + 1)
                found_marker = True
    
    if found_marker and cutoff_index != -1:
        clean_body = body_text[cutoff_index:].strip()
        
        # Reconstruct
        new_content = "".join(preamble) + "\n" + clean_body
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
        
    return False

def run_cleanup():
    count = 0
    files = [f for f in os.listdir(CASE_DIR) if f.endswith(".md")]
    print(f"Cleaning {len(files)} files...")
    
    for filename in files:
        if clean_file(os.path.join(CASE_DIR, filename)):
            count += 1
            print(f"cleaned: {filename}")
            
    print(f"Done. Cleaned {count} files.")

if __name__ == "__main__":
    if os.path.exists(CASE_DIR):
        run_cleanup()
