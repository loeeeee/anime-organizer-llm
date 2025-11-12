# Folder Tree to JSON Script

## User Intent

The user wants a Python script that gathers the tree structure of a folder and saves it to a JSON file. The script should utilize dataclass to define every data it encountered unless it has only one attribute.

## Implementation Details

### Purpose

The `gather_tree.py` script recursively scans a folder structure, capturing file and directory names along with their hierarchy, and saves this information as a JSON file. The script follows symlinks and includes hidden files.

### Usage

```bash
python scripts/gather_tree.py <folder_path> <output_json_path>
```

**Arguments:**
- `folder_path`: Path to the folder to scan (required)
- `output_json_path`: Path where the JSON file will be saved (required)

**Example:**
```bash
python scripts/gather_tree.py /path/to/folder tree_structure.json
```

### Data Structures

The script uses the following data structures:

- **FileNode**: Represents a file with `name` and `type` attributes. Uses a dataclass.
- **DirectoryNode**: Represents a directory with `name`, `type`, and `children` attributes. Uses a dataclass.
- **TreeStructure**: Root structure containing the tree data. Uses a dataclass.

### Features

- Recursive directory traversal using `pathlib.Path`
- Includes only file/directory names and hierarchy (no metadata like sizes, timestamps, permissions)
- Follows symlinks during traversal
- Includes all files including hidden ones (starting with `.`)
- Command-line interface with required arguments
- Logging to both console and file
- Progress bar (tqdm) for long-running operations (>10s)
- Concise execution report after completion

### JSON Output Format

The output JSON structure follows this format:

```json
{
  "root": {
    "name": "folder_name",
    "type": "folder",
    "children": [
      {
        "name": "file.txt",
        "type": "file"
      },
      {
        "name": "subdirectory",
        "type": "folder",
        "children": [
          {
            "name": "nested_file.txt",
            "type": "file"
          }
        ]
      }
    ]
  }
}
```

### Implementation Status

Script implementation completed. The script successfully:
- Scans directory structures recursively
- Follows symlinks (with cycle detection)
- Includes hidden files
- Outputs clean JSON structure
- Provides logging and execution reports
- Handles errors gracefully with fail-fast design

