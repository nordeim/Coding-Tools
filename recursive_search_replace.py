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
    Check if a file appears to be a readable text file.
    Attempts to read a small portion using UTF-8 encoding.
    If UnicodeDecodeError or other I/O issues occur, returns False.
    Note: This check is limited to UTF-8 encoding. Files with other valid
          text encodings might be incorrectly flagged as non-readable.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(1024) # Read a small chunk to test readability
        return True
    except Exception: # Catching broad Exception as any failure means it's not readable as UTF-8
        return False

def replace_string_in_file(file_path, old_str, new_str):
    """
    Replace all occurrences of old_str with new_str in the specified file.
    Creates a backup with the .bak extension before modifying.
    Note: This function reads the entire file into memory. It may not be
          suitable for very large files due to potential memory constraints.
    Returns:
      - status: 'replaced', 'no_match', or 'skipped'
      - count: Number of replacements made (0 if none)
      - error: Error message if any exception occurred
    """
    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return 'skipped', 0, f"Error reading file: {e}"

    # Count occurrences before replacement
    occurences = content.count(old_str)
    if occurences == 0:
        return 'no_match', 0, None

    # Create a backup
    backup_path = file_path + ".bak"
    try:
        shutil.copy(file_path, backup_path)
    except Exception as e:
        # If backup fails, do not proceed with modification
        return 'skipped', 0, f"Error creating backup: {e}"

    # Perform the replacement
    new_content = content.replace(old_str, new_str)

    # Write the modified content back to the original file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
    except Exception as e:
        # Attempt to restore from backup if write fails? (Optional complexity)
        # For simplicity, we just report the write error. The .bak file still exists.
        return 'skipped', 0, f"Error writing file: {e}"

    return 'replaced', occurences, None

def process_files(folder, old_str, new_str, file_extension):
    """
    Recursively processes files in a folder for string replacement.
    """
    total_files_processed = 0 # Files attempted for replacement (matching criteria)
    total_files_encountered = 0 # All files seen by os.walk
    files_modified = 0
    files_skipped_error = 0
    files_skipped_filter = 0
    files_no_match = 0

    print("\n--- Processing Files ---")
    # Walk directory recursively
    for root, dirs, files in os.walk(folder):
        # Optional: Skip hidden directories (like .git, .svn) - could be added if needed
        # dirs[:] = [d for d in dirs if not d.startswith('.')]

        for filename in files:
            total_files_encountered += 1
            full_path = os.path.join(root, filename)

            # *** Enhancement: Explicitly skip .bak files ***
            if filename.lower().endswith(".bak"):
                print(f"Skipped backup file: {full_path}")
                files_skipped_filter += 1
                continue

            # Check if the file matches the criteria (extension or readability)
            process_this_file = False
            if file_extension:
                # Filter by specific extension (case-insensitive)
                if filename.lower().endswith(file_extension.lower()):
                    process_this_file = True
                else:
                    # Doesn't match extension, skip silently for summary later
                    files_skipped_filter += 1
            else:
                # No extension provided, check if it's a readable text file
                if is_readable_text_file(full_path):
                    process_this_file = True
                else:
                    print(f"Skipped non-readable/binary file: {full_path}")
                    files_skipped_filter += 1

            # If the file meets criteria, attempt replacement
            if process_this_file:
                total_files_processed += 1
                status, count, error = replace_string_in_file(full_path, old_str, new_str)

                if status == 'skipped':
                    print(f"[ERROR] Skipped {os.path.relpath(full_path, folder)}: {error}")
                    files_skipped_error += 1
                elif status == 'no_match':
                    print(f"[No Match] No occurrences found in {os.path.relpath(full_path, folder)}")
                    files_no_match += 1
                elif status == 'replaced':
                    print(f"[Replaced] {count} occurrence(s) in {os.path.relpath(full_path, folder)}")
                    files_modified += 1

    # Print overall summary
    print("\n=== Replacement Summary ===")
    print(f"Total files encountered: {total_files_encountered}")
    print(f"Files matching criteria: {total_files_processed}")
    print(f"----------------------------")
    print(f"Files modified: {files_modified}")
    print(f"Files with no match: {files_no_match}")
    print(f"Files skipped (errors): {files_skipped_error}")
    print(f"Files skipped (filter/type): {files_skipped_filter + (total_files_encountered - total_files_processed - files_skipped_error)}") # Recalculate for clarity


def main():
    # Retrieve command-line parameters; prompt interactively for any missing ones.
    args = sys.argv[1:]
    folder = ""
    old_str = ""
    new_str = ""
    file_extension = None # Optional parameter, default is None

    # Argument parsing
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
        # Ensure extension starts with a dot if user forgot
        if not file_extension.startswith('.'):
             file_extension = '.' + file_extension
        print(f"Filtering by file extension: {file_extension}")
    else:
        # Warn that without extension, all readable text files will be processed.
        print("\nWarning: No file extension provided.")
        print("The script will attempt to process ALL readable text files recursively.")
        print("Binary files or files with non-UTF8 encodings will likely be skipped.")
        proceed = get_input("Do you want to proceed? (Y/y to continue, anything else to abort)")
        if proceed.lower() != 'y':
            print("Operation aborted by the user.")
            sys.exit(0)

    # Validate folder path
    if not folder or not os.path.isdir(folder):
        print(f"Error: Invalid folder path provided: '{folder}'. Exiting.")
        sys.exit(1)

    # Basic validation for search string
    if not old_str:
        print("Error: The search string (old_str) cannot be empty. Exiting.")
        sys.exit(1)

    # Proceed with processing
    process_files(folder, old_str, new_str, file_extension)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation interrupted by user (Ctrl+C). Exiting.")
        sys.exit(1)
      
