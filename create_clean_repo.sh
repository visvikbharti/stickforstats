#!/bin/bash

echo "🔄 Creating clean repository..."

# Move current .git to backup
mv .git .git.backup

# Initialize fresh repository
git init

# Add all files (gitignore will exclude large directories)
git add .

# Create initial commit
git commit -m "Initial commit: StickForStats full stack application

- Django backend with REST API
- React frontend with Material-UI
- 13 statistical analysis modules
- Deployment scripts for Hetzner
- Production-ready configuration"

# Add remote
git remote add origin https://github.com/visvikbharti/stickforstats.git

# Push to GitHub
echo ""
echo "✅ Clean repository created!"
echo "📤 Now push to GitHub with:"
echo "git push -u origin main"