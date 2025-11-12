{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python313
    uv
  ];

  shellHook = ''
    # Ensure we're using Python 3.13
    export PYTHONPATH="${pkgs.python313}/lib/python3.13/site-packages:$PYTHONPATH"
    
    # Initialize uv if not already done
    if [ ! -d ".venv" ]; then
      echo "Creating virtual environment with uv..."
      uv venv
    fi
    
    # Activate the virtual environment
    source .venv/bin/activate
    
    # Sync dependencies if pyproject.toml exists
    if [ -f "pyproject.toml" ]; then
      echo "Syncing dependencies with uv..."
      uv sync
    fi
  '';
}

