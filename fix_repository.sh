#!/bin/bash

echo "🔧 Fixing repository by removing large files..."

# Create a backup branch
git branch backup-before-cleanup

# Use BFG or filter-branch to remove large files
echo "📦 Removing large files from git history..."

# Remove venv and node_modules from all history
git filter-branch --force --index-filter \
  'git rm -r --cached --ignore-unmatch venv frontend/node_modules' \
  --prune-empty --tag-name-filter cat -- --all

# Clean up
git for-each-ref --format="%(refname)" refs/original/ | xargs -n 1 git update-ref -d
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo "✅ Repository cleaned!"
echo "📊 New repository size:"
du -sh .git

echo ""
echo "🚀 Now push to GitHub:"
echo "git push origin main --force"