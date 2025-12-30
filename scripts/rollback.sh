#!/bin/bash
# Quick rollback script - reverts to last known good commit

LAST_GOOD_COMMIT="300f3fe"
LAST_GOOD_MESSAGE="Fix indentation errors"

echo "================================"
echo "VerifAI Rollback Script"
echo "================================"
echo ""
echo "This will rollback to:"
echo "  Commit: $LAST_GOOD_COMMIT"
echo "  Message: $LAST_GOOD_MESSAGE"
echo "  Status: App starts, local testing works"
echo ""
read -p "Continue with rollback? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Rolling back..."
    git reset --hard $LAST_GOOD_COMMIT
    git push --force
    echo ""
    echo "✅ Rollback complete!"
    echo "Railway will redeploy in ~90 seconds"
    echo ""
    echo "Note: You'll still need to fix the HTTPS issue,"
    echo "but at least the app will be running."
else
    echo "Rollback cancelled"
fi
