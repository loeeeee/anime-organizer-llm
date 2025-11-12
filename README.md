# Anime Organizer LLM

Use LLM to organize anime

## Motivation

People name the anime file so badly that my Jellyfin cannot recognize it!

### Examples

## Scripts

### gather_tree.py

A Python script that gathers the tree structure of a folder and saves it to a JSON file.

**Usage:**
```bash
python scripts/gather_tree.py <folder_path> <output_json_path>
```

**Features:**
- Recursively scans directory structures
- Follows symlinks (with cycle detection)
- Includes hidden files
- Outputs clean JSON structure with file/directory names and hierarchy
- Provides logging and execution reports

For more details, see `docs-vibe/01-folder-tree-to-json.md`.
