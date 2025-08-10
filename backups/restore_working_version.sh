#!/bin/bash
echo "🔄 Restoring working version of ResuMatch..."

# Check if backup exists
if [ ! -d "backups/working-version-$(date +%Y%m%d)" ]; then
    echo "❌ No backup found for today. Please specify backup date."
    echo "Available backups:"
    ls -la backups/
    exit 1
fi

BACKUP_DIR="backups/working-version-$(date +%Y%m%d)"

echo "�� Restoring from: $BACKUP_DIR"

# Restore files
cp -r $BACKUP_DIR/*.py ./
cp -r $BACKUP_DIR/templates_backup/* ./templates/
cp -r $BACKUP_DIR/examples_backup/* ./examples/
cp -r $BACKUP_DIR/job_templates_backup/* ./job_templates/
cp $BACKUP_DIR/*.json ./
cp $BACKUP_DIR/*.md ./
cp $BACKUP_DIR/requirements.txt ./
cp $BACKUP_DIR/.env* ./ 2>/dev/null || true

echo "✅ Restore complete!"
echo "🚀 You can now run: python app.py"
