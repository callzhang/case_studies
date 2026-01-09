import os

CASE_DIR = "case_studies"

def validate_files():
    files = [f for f in os.listdir(CASE_DIR) if f.endswith(".md")]
    print(f"Scanning {len(files)} files in {CASE_DIR}...\n")
    
    valid_count = 0
    short_files = []
    error_files = []
    
    for filename in files:
        path = os.path.join(CASE_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Check for error indicators
        if "404 Not Found" in content or "页面不存在" in content:
            error_files.append(filename)
            continue
            
        # Check for length
        if len(content) < 200:
            short_files.append(filename)
            continue
            
        valid_count += 1
        
    print(f"✅ Valid files: {valid_count}")
    print(f"⚠️ Short files (<200 chars): {len(short_files)}")
    for f in short_files:
        print(f"  - {f}")
        
    print(f"❌ Error files (404/Not Found): {len(error_files)}")
    for f in error_files:
        print(f"  - {f}")
        
    # Optional cleanup logic
    if short_files or error_files:
        print("\nDo you want to delete these invalid files? (Run manually to confirm)")

if __name__ == "__main__":
    if os.path.exists(CASE_DIR):
        validate_files()
    else:
        print(f"Directory {CASE_DIR} does not exist.")
