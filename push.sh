#!/bin/bash
echo "================================"
echo "Smart Griev - Git Push"
echo "================================"
echo ""

echo "Staging all changes..."
git add -A

echo ""
echo "Creating commit..."
git commit -m "Complete Smart Grievance setup with Windows scripts, auth persistence, and admin officer management"

echo ""
echo "Pushing to repository..."
git push origin main

echo ""
echo "================================"
echo "Code pushed successfully!"
echo "================================"
