Below is the enhanced Python script for recursive search and replace with optional file extension as requirement.

```python
import os
import sys
import shutil

def get_input(prompt_text, default=None):
    """Prompt the user and return the input; if blank and default is provided, return default."""
    if default:
        prompt = f"{prompt_text} [{default}]: "
    else:
        prompt = f"{prompt_text}: "
    value = input(prompt).strip()
    return value if value else (default if default is not None else "")

def is_readable_text_file(file_path):
    """
    Check if a file is a readable text file.
    Attempts to read a small portion using UTF-8.
    If UnicodeDecodeError or other issues occur, returns False.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(1024)
        return True
    except Exception:
        return False

def replace_string_in_file(file_path, old_str, new_str):
    """
    Replace all occurrences of old_str with new_str in the specified file.
    Creates a backup with the .bak extension before modifying.
    Returns:
      - status: 'replaced', 'no_match', or 'skipped'
      - count: Number of replacements made (0 if none)
      - error: Error message if any exception occurred
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return 'skipped', 0, f"Error reading file: {e}"

    occurences = content.count(old_str)
    if occurences == 0:
        return 'no_match', 0, None

    # Create a backup
    backup_path = file_path + ".bak"
    try:
        shutil.copy(file_path, backup_path)
    except Exception as e:
        return 'skipped', 0, f"Error creating backup: {e}"

    new_content = content.replace(old_str, new_str)
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
    except Exception as e:
        return 'skipped', 0, f"Error writing file: {e}"

    return 'replaced', occurences, None

def process_files(folder, old_str, new_str, file_extension):
    total_files = 0
    replaced_files = 0
    skipped_files = 0
    no_match_files = 0

    # Walk directory recursively
    for root, dirs, files in os.walk(folder):
        for filename in files:
            full_path = os.path.join(root, filename)
            # If a file extension filter is provided, skip files not matching
            if file_extension:
                if not filename.lower().endswith(file_extension.lower()):
                    continue
            else:
                # When no extension is provided, test for readability (all text types)
                if not is_readable_text_file(full_path):
                    print(f"Skipped non-readable text file: {full_path}")
                    skipped_files += 1
                    continue

            total_files += 1
            status, count, error = replace_string_in_file(full_path, old_str, new_str)

            if status == 'skipped':
                print(f"Skipped {full_path}: {error}")
                skipped_files += 1
            elif status == 'no_match':
                print(f"No match found in {full_path}")
                no_match_files += 1
            elif status == 'replaced':
                print(f"Replaced {count} occurrence(s) in {full_path}")
                replaced_files += 1

    # Print overall summary
    print("\n=== Replacement Summary ===")
    print(f"Total files processed: {total_files}")
    print(f"Files modified: {replaced_files}")
    print(f"Files with no match: {no_match_files}")
    print(f"Files skipped: {skipped_files}")

def main():
    # Retrieve command-line parameters; prompt interactively for any missing ones.
    args = sys.argv[1:]
    folder = ""
    old_str = ""
    new_str = ""
    file_extension = None  # Optional parameter

    if len(args) >= 1:
        folder = args[0]
    else:
        folder = get_input("Enter the folder path to search files")

    if len(args) >= 2:
        old_str = args[1]
    else:
        old_str = get_input("Enter the search string (old_str)")

    if len(args) >= 3:
        new_str = args[2]
    else:
        new_str = get_input("Enter the replacement string (new_str)")

    if len(args) >= 4:
        file_extension = args[3]
    else:
        # Warn that without extension, all readable text files will be processed.
        print("\nWarning: No file extension provided. All readable text files will be processed.")
        proceed = get_input("Do you want to proceed? (Y/y to continue)")
        if proceed.lower() != 'y':
            print("Operation aborted by the user.")
            sys.exit(0)

    # Validate folder path
    if not os.path.isdir(folder):
        print("Invalid folder path provided. Exiting.")
        sys.exit(1)

    process_files(folder, old_str, new_str, file_extension)

if __name__ == "__main__":
    main()
```

---

### **Script Review and Simulation Analysis**

1. **Command-line/Interactive Input:**  
   - **Implementation:**  
     The script checks the number of command-line arguments. If fewer than the required three parameters (folder, old string, new string) are provided, it prompts the user interactively with clear, intelligent prompts.  
   - **Enhancement:**  
     When the optional fourth parameter (file extension) is not provided, the script warns the user that it will operate on all readable text files. It then confirms the continuation when the user enters "Y" or "y".  
   - **Validation:**  
     This covers robust command-line and interactive handling, ensuring the missing parameters are requested smartly.

2. **File/Directory Logic:**  
   - **Implementation:**  
     The script uses `os.walk()` to recursively traverse the given directory and its subdirectories. Files are filtered based on the provided file extension (if any); otherwise, each file is checked for readability as a text file.  
   - **Enhancement:**  
     Non-readable files are skipped with a clear message, and only files that meet the criteria are processed.  
   - **Validation:**  
     This logic meets the requirement of searching all files (using recursion) and handling typical text file formats while skipping non-readable files.

3. **Literal Replacement (Special Characters):**  
   - **Implementation:**  
     The script uses Python’s built-in `str.replace()` to perform literal string replacement. This method inherently handles any non-alphanumeric ASCII characters (such as `,;|"'<>-_()$@~%^[]{}\`) without the need for additional escaping.  
   - **Validation:**  
     Special characters are processed correctly, meeting the requirement for literal replacement.

4. **Accurate Reporting:**  
   - **Implementation:**  
     As each file is processed, the script prints a status—whether the file was skipped, had no match, or the number of occurrences replaced.  
   - **Enhancement:**  
     At the end of the run, a summary displays totals for processed files, modified files, files with no matches, and skipped files.  
   - **Validation:**  
     This provides clear, detailed feedback and overall statistics, ensuring accurate and comprehensive reporting.

5. **Error Handling:**  
   - **Implementation:**  
     The script wraps file read, backup creation, and write operations in try/except blocks to catch and report errors. Backup files are created using Python’s `shutil.copy()`, and any exceptions encountered lead to appropriate status messages (e.g., "skipped" with an error message).  
   - **Enhancement:**  
     In cases of directory validation or file operation failures, the script exits gracefully with clear error messages.  
   - **Validation:**  
     This thorough error handling ensures robustness against common file I/O issues.

---

### **Conclusion**

The enhanced script meets all the five specified requirements:
- **Command-line/Interactive Input:** It intelligently prompts for missing parameters and confirms user intent when processing all text files.
- **File/Directory Logic:** It recursively processes subdirectories, applies file extension filters, and validates file readability.
- **Literal Replacement (Special Chars):** It uses direct string replacement to safely handle special characters.
- **Accurate Reporting:** It provides per-file and overall summaries of actions taken.
- **Error Handling:** It includes robust try/except blocks to manage unexpected errors during file processing.

https://copilot.microsoft.com/shares/sYQDoWmWFrXKK5fuEeJH8
