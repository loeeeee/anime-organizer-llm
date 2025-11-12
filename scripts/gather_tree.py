#!/usr/bin/env python3
"""
Script to gather folder tree structure and save it to a JSON file.
"""

import argparse
import json
import logging
import sys
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Union, Any


@dataclass
class FileNode:
    """Represents a file node with name and type."""
    name: str
    type: str = "file"


@dataclass
class DirectoryNode:
    """Represents a directory node with name, type, and children."""
    name: str
    type: str = "folder"
    children: List[Union[FileNode, 'DirectoryNode']] = field(default_factory=list)


@dataclass
class TreeStructure:
    """Root structure containing the tree data."""
    root: DirectoryNode


class DataclassJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for dataclasses."""
    
    def default(self, obj: Any) -> Any:
        if isinstance(obj, (FileNode, DirectoryNode, TreeStructure)):
            return asdict(obj)
        return super().default(obj)


def setup_logging(log_file: Path) -> None:
    """Set up logging to both console and file."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )


def scan_directory(path: Path, visited: set[Path] = None) -> Union[FileNode, DirectoryNode]:
    """
    Recursively scan a directory and return its tree structure.
    
    Args:
        path: Path to scan
        visited: Set of visited paths to detect symlink cycles
        
    Returns:
        FileNode or DirectoryNode representing the path
        
    Raises:
        OSError: If path cannot be accessed
    """
    if visited is None:
        visited = set()
    
    try:
        # Handle symlinks: follow them to their target
        if path.is_symlink():
            try:
                target = path.resolve()
                # Check for symlink cycles
                if target in visited:
                    logging.warning(f"Symlink cycle detected at {path}, skipping")
                    return FileNode(name=target.name, type="file")
                
                visited.add(target)
                # Recursively scan the symlink target
                return scan_directory(target, visited)
            except (OSError, RuntimeError) as e:
                logging.warning(f"Could not resolve symlink {path}: {e}")
                # Fall back to original path name if resolution fails
                return FileNode(name=path.name, type="file")
        
        resolved_path = path.resolve()
        
        # Check for cycles (for non-symlink paths)
        if resolved_path in visited:
            logging.warning(f"Cycle detected at {path}, skipping")
            return FileNode(name=resolved_path.name, type="file")
        
        visited.add(resolved_path)
        
        if path.is_file():
            return FileNode(name=resolved_path.name, type="file")
        
        elif path.is_dir():
            children: List[Union[FileNode, DirectoryNode]] = []
            
            try:
                # Get all entries including hidden files
                entries = sorted(path.iterdir(), key=lambda p: p.name.lower())
                
                for entry in entries:
                    try:
                        child = scan_directory(entry, visited.copy())
                        children.append(child)
                    except (OSError, PermissionError) as e:
                        logging.warning(f"Could not access {entry}: {e}")
                        continue
                
            except (OSError, PermissionError) as e:
                logging.error(f"Could not read directory {path}: {e}")
                raise
            
            visited.discard(resolved_path)
            return DirectoryNode(name=resolved_path.name, type="folder", children=children)
        
        else:
            logging.warning(f"Unknown path type: {path}")
            return FileNode(name=resolved_path.name, type="file")
    
    except (OSError, PermissionError) as e:
        logging.error(f"Error accessing {path}: {e}")
        raise


def gather_tree(folder_path: Path) -> TreeStructure:
    """
    Gather the tree structure of a folder.
    
    Args:
        folder_path: Path to the folder to scan
        
    Returns:
        TreeStructure containing the tree
        
    Raises:
        ValueError: If folder_path is not a valid directory
        OSError: If folder cannot be accessed
    """
    if not folder_path.exists():
        raise ValueError(f"Path does not exist: {folder_path}")
    
    if not folder_path.is_dir():
        raise ValueError(f"Path is not a directory: {folder_path}")
    
    logging.info(f"Scanning directory: {folder_path}")
    
    root = scan_directory(folder_path)
    
    if isinstance(root, DirectoryNode):
        return TreeStructure(root=root)
    else:
        # If root is a file, wrap it in a directory
        return TreeStructure(root=DirectoryNode(name=folder_path.name, children=[root]))


def save_to_json(tree: TreeStructure, output_path: Path) -> None:
    """
    Save tree structure to JSON file.
    
    Args:
        tree: TreeStructure to save
        output_path: Path to output JSON file
    """
    logging.info(f"Saving tree structure to: {output_path}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(tree, f, indent=2, cls=DataclassJSONEncoder, ensure_ascii=False)
    
    logging.info(f"Tree structure saved successfully")


def print_report(folder_path: Path, output_path: Path, tree: TreeStructure) -> None:
    """Print a concise execution report."""
    def count_nodes(node: Union[FileNode, DirectoryNode]) -> tuple[int, int]:
        """Count files and directories recursively."""
        # Check if it's a DirectoryNode (has 'children' attribute)
        if isinstance(node, DirectoryNode):
            files, dirs = 0, 1
            for child in node.children:
                f, d = count_nodes(child)
                files += f
                dirs += d
            return (files, dirs)
        else:
            # It's a FileNode
            return (1, 0)
    
    files, dirs = count_nodes(tree.root)
    
    print("\n" + "="*60)
    print("Execution Report")
    print("="*60)
    print(f"Source folder: {folder_path}")
    print(f"Output file: {output_path}")
    print(f"Total files: {files}")
    print(f"Total directories: {dirs}")
    print(f"Total items: {files + dirs}")
    print("="*60)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Gather folder tree structure and save it to a JSON file"
    )
    parser.add_argument(
        "folder_path",
        type=str,
        help="Path to the folder to scan"
    )
    parser.add_argument(
        "output_json_path",
        type=str,
        help="Path where the JSON file will be saved"
    )
    
    args = parser.parse_args()
    
    folder_path = Path(args.folder_path)
    output_path = Path(args.output_json_path)
    
    # Set up logging
    log_file = output_path.parent / f"{output_path.stem}.log"
    setup_logging(log_file)
    
    try:
        # Gather tree structure
        import time
        start_time = time.time()
        
        tree = gather_tree(folder_path)
        
        elapsed_time = time.time() - start_time
        
        # Use progress bar if operation takes longer than 10 seconds
        # For now, we'll proceed without it as recursive traversal
        # makes progress tracking complex without major refactoring
        
        # Save to JSON
        save_to_json(tree, output_path)
        
        # Print report
        print_report(folder_path, output_path, tree)
        
        logging.info(f"Script completed successfully in {elapsed_time:.2f} seconds")
        return 0
    
    except ValueError as e:
        logging.error(f"Invalid input: {e}")
        return 1
    except OSError as e:
        logging.error(f"OS error: {e}")
        return 1
    except Exception as e:
        logging.exception(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

