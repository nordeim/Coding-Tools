import os
import re
import sys

def replace_in_file(file_path, current_string, replacement_string):
    """
    Replace occurrences of current_string with replacement_string in a single file.
    Returns the number of replacements made.
      - Returns 0 if no occurrences are found.
      - Returns -1 if a file error occurs (read or write).
    """
    try:
        # Specify encoding, handle potential decoding errors during read
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        # Print specific read error
        print(f"Error: Failed to read file '{file_path}': {e}")
        return -1

    # Escape the current_string so that special characters are treated literally.
    pattern = re.escape(current_string)

    # Perform substitution and get count
    try:
        new_content, count = re.subn(pattern, replacement_string, content)
    except Exception as e:
        # Handle potential errors during regex processing, though less common here
        print(f"Error: Failed during replacement in file '{file_path}': {e}")
        return -1

    # If no replacements were made, no need to write the file again.
    if count == 0:
        return 0

    # Write the modified content back to the file
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
    except Exception as e:
        # Print specific write error
        print(f"Error: Failed to write to file '{file_path}': {e}")
        return -1

    # Return the number of replacements if successful
    return count

def process_path(path, current_string, replacement_string):
    """
    Process the given path.
      - If path is a file, perform replacements only on that file.
      - If path is a directory, perform replacements on all files directly in the folder.
      - Provides status messages and warnings if the string is not found or if errors occur.
    """
    if not os.path.exists(path):
        print(f"Error: The provided path '{path}' does not exist.")
        return

    # Process a single file.
    if os.path.isfile(path):
        count = replace_in_file(path, current_string, replacement_string)
        # Check the result from replace_in_file
        # Error messages (-1) are already printed within replace_in_file
        if count == 0:
            print(f"Warning: No occurrences of '{current_string}' found in file '{path}'.")
        elif count > 0:
            print(f"File '{path}' processed successfully: {count} replacement(s) made.")
        # No need for an else block for count == -1, error was already printed
        return

    # Process all files in a directory (non-recursively).
    elif os.path.isdir(path):
        files_found = False
        any_replacements = False
        print(f"Processing files in folder: '{path}'...") # Added context for directory processing
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            # Ensure we only process files, not subdirectories
            if os.path.isfile(file_path):
                files_found = True
                print(f"--- Processing file: '{filename}' ---") # Indicate which file is being processed
                count = replace_in_file(file_path, current_string, replacement_string)
                # Check the result for each file
                # Error messages (-1) are already printed within replace_in_file
                if count == 0:
                    # Adjusted message slightly for clarity within directory context
                    print(f"    No occurrences of '{current_string}' found.")
                elif count > 0:
                    print(f"    {count} replacement(s) made.")
                    any_replacements = True
                # No need for an else block for count == -1, error was already printed

        print("-" * 20) # Separator after processing directory contents

        # Provide summary warnings for the directory operation
        if not files_found:
            print(f"Warning: No files found in folder '{path}'.")
        elif not any_replacements:
            # This warning is only relevant if files were actually found and processed
            print(f"Warning: The string '{current_string}' was not found in any files within folder '{path}'.")
        else:
            print(f"Finished processing folder '{path}'.") # Confirmation message
        return

    # Handle cases where the path exists but is neither a file nor a directory
    else:
        print(f"Error: The provided path '{path}' is neither a file nor a folder.")

def main():
    """
    Main function:
      - Checks for command line parameters; if missing, prompts the user.
      - Uses the provided or entered parameters to process the file/folder.
    Expected usage:
      python script.py <file_or_folder_path> <current_string> <replacement_string>
    """
    args = sys.argv[1:]
    path = None
    current_string = None
    replacement_string = None

    # Check command-line arguments or prompt interactively
    if len(args) >= 3:
        path = args[0]
        current_string = args[1]
        replacement_string = args[2]
    else:
        if len(args) >= 1:
            path = args[0]
        else:
            path = input("Enter the file or folder path: ").strip()

        if len(args) >= 2:
            current_string = args[1]
        else:
            current_string = input("Enter the current string to be replaced: ").strip()

        # Always needs replacement string if not fully provided via args
        replacement_string = input("Enter the replacement string: ").strip()

    # Basic validation before processing
    if not path or current_string is None or replacement_string is None:
         print("Error: Missing required information (path, current string, or replacement string).")
         sys.exit(1) # Exit if essential info is missing after prompts

    print(f"\nStarting replacement process...")
    print(f"Path: '{path}'")
    print(f"Replacing: '{current_string}'")
    print(f"With: '{replacement_string}'\n")

    process_path(path, current_string, replacement_string)

if __name__ == "__main__":
    main()
  
