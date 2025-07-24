#!/bin/bash
# Script to initialize Git repository for finance-agent

# Make sure we're in the project directory
cd "$(dirname "$0")"

# Initialize Git if not already done
if [ ! -d .git ]; then
  echo "Initializing Git repository..."
  git init
else
  echo "Git repository already initialized."
fi

# Add all files according to .gitignore
echo "Adding files to Git..."
git add .

# Show status
echo -e "\nGit status:"
git status

echo -e "\nTo commit your changes, run:"
echo "git commit -m \"Initial commit of Personal Finance Tracker\""
echo -e "\nTo add a remote repository, run:"
echo "git remote add origin <your-repository-url>"
echo -e "\nTo push your code, run:"
echo "git push -u origin main"