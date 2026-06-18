#!/bin/bash

# Script to append fildengu and foldengu functions to ~/.zshrc

ZSHRC="$HOME/.zshrc"

# Check if .zshrc exists
if [[ ! -f "$ZSHRC" ]]; then
  echo "Error: $ZSHRC not found"
  exit 1
fi

# Check if functions already exist
if grep -q "fildengu()" "$ZSHRC"; then
  echo "Warning: fildengu function already exists in $ZSHRC"
  read "?Overwrite? (y/n) " -n 1 response
  echo
  if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
  fi
  # Remove existing functions
  sed -i.bak '/^fildengu()/,/^}/d' "$ZSHRC"
  sed -i '/^foldengu()/,/^}/d' "$ZSHRC"
fi

# Append the functions
cat >> "$ZSHRC" << 'EOF'

# File deletion with confirmation
fildengu() {
  local force=false
  local args=()

  for arg in "$@"; do
    [[ "$arg" == "ehe" ]] && force=true || args+=("$arg")
  done

  [[ ${#args[@]} -eq 0 ]] && { echo "Usage: fildengu <filename> [ehe]"; return 1 }

  for file in "${args[@]}"; do
    [[ ! -f "$file" ]] && { echo "Error: '$file' is not a file"; continue }

    if [[ "$force" == true ]]; then
      rm "$file" && echo "Deleted: $file"
    else
      read "?Delete file '$file'? (Y/n) " response
      [[ "$response" =~ ^[Nn]$ ]] || { rm "$file"; echo "Deleted: $file"; }
    fi
  done
}

# Folder deletion with confirmation
foldengu() {
  local force=false
  local args=()

  for arg in "$@"; do
    [[ "$arg" == "ehe" ]] && force=true || args+=("$arg")
  done

  [[ ${#args[@]} -eq 0 ]] && { echo "Usage: foldengu <foldername> [ehe]"; return 1 }

  for folder in "${args[@]}"; do
    [[ ! -d "$folder" ]] && { echo "Error: '$folder' is not a directory"; continue }

    if [[ "$force" == true ]]; then
      rm -rf "$folder" && echo "Deleted: $folder"
    else
      read "?Delete folder '$folder'? (Y/n) " response
      [[ "$response" =~ ^[Nn]$ ]] || { rm -rf "$folder"; echo "Deleted: $folder"; }
    fi
  done
}
EOF

echo "✓ Functions appended to $ZSHRC"
echo "Run: source ~/.zshrc"
echo ""
echo "Usage:"
echo "  fildengu <filename>              # Delete file with confirmation"
echo "  fildengu <filename> ehe          # Delete file without confirmation"
echo "  foldengu <foldername>            # Delete folder with confirmation"
echo "  foldengu <foldername> ehe        # Delete folder without confirmation"