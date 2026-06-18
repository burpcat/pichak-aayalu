```markdown
# deng-ehe

File and folder deletion utility with Telugu brainrot intuition. Delete files and directories with optional confirmation, force-delete with a single keyword.

---

## What it does

Provides two shell functions—`fildengu` and `foldengu`—that delete files and folders respectively. By default, they prompt for confirmation. Pass `ehe` as a flag to force-delete without asking. Includes error checking for non-existent paths and proper validation.

---

## Usage

```bash
# Delete a file (with confirmation)
fildengu myfile.txt

# Delete a file without confirmation
fildengu myfile.txt ehe

# Delete multiple files (confirmation per file)
fildengu file1.txt file2.txt file3.txt

# Delete a folder (with confirmation)
foldengu myfolder/

# Delete a folder without confirmation
foldengu myfolder/ ehe

# Delete multiple folders
foldengu folder1/ folder2/
```

---

## Installation

Run the setup script to append these functions to your `~/.zshrc`:

```bash
chmod +x append_to_zshrc.sh
./append_to_zshrc.sh
```

Then reload your shell:

```bash
source ~/.zshrc
```

---

## Requirements

Nothing to install. Everything used ships with standard Unix:

- `bash` — shell script execution
- `read` — interactive prompts
- `rm` / `rm -rf` — file and directory deletion
- Standard utilities: `test`, `regex`

Works on macOS, Linux, and any system with bash/zsh.

---

## How it works

Both functions parse arguments to detect the `ehe` flag (force mode). Valid paths are checked with `-f` (file) or `-d` (directory) tests. If force mode is active, the deletion happens silently. Otherwise, a confirmation prompt is shown—responding with anything other than `n` or `N` proceeds with deletion.

Multiple targets can be specified and are processed in sequence, with independent confirmation prompts for each.

---

## License

View-only. See root [`README.md`](../README.md).
```