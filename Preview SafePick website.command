#!/bin/bash
# Double-click this file in Finder to see the SafePick website at http://localhost:8080
# Keep the Terminal window that opens; close it (or press Control + C) to stop.
cd "$(dirname "$0")" || exit 1

# Find Node the same way your Terminal does (nvm or Homebrew)
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" >/dev/null 2>&1

if command -v node >/dev/null 2>&1; then
  node preview.mjs
elif command -v python3 >/dev/null 2>&1; then
  echo "Node wasn't found, so using Python instead."
  echo "SafePick website: http://localhost:8080   (Control + C to stop)"
  (sleep 1; open "http://localhost:8080") &
  python3 -m http.server 8080 --bind 127.0.0.1 --directory site
else
  echo "Node and Python weren't found. Install one of them to preview the site."
fi
