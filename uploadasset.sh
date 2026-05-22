# Commit and push all changes
echo "Committing and pushing changes..."
git add .
git commit -m "Auto-commit before release upload" || echo "No changes to commit"
git push

# Define repository and asset name
REPO=dadski72/BMS_BLE_DX-HA
ASSET_NAME=bms_ble.zip

# Use the integration manifest version as the release tag. Home Assistant blocks
# custom integrations whose manifest version is a commit hash.
echo "Getting manifest version for new release tag..."
TAG=$(python3 -c 'import json; print(json.load(open("custom_components/bms_ble/manifest.json"))["version"])')
echo "Creating new release with tag: $TAG"

# Create a new release with the current commit
echo "Creating GitHub release..."
gh release create "$TAG" --repo "$REPO" --title "Release $TAG" --notes "Automated release $TAG"

# Remove existing zip file if it exists
if [ -f "$ASSET_NAME" ]; then
    echo "Removing existing $ASSET_NAME..."
    rm "$ASSET_NAME"
fi

# Create the zip file with proper directory structure
echo "Creating zip file: $ASSET_NAME"
cd custom_components/bms_ble || exit 1
7zz a -tzip "../../../$ASSET_NAME" . -r '-x!__pycache__' '-x!*.pyc'
cd - >/dev/null || exit 1

# Verify the zip file was created successfully
if [ -f "$ASSET_NAME" ]; then
    echo "Zip file created successfully. Size: $(du -h "$ASSET_NAME" | cut -f1)"
    echo "Contents preview:"
    7zz l "$ASSET_NAME" | head -15
else
    echo "ERROR: Failed to create zip file!"
    exit 1
fi

echo "Uploading asset: $ASSET_NAME to release $TAG"
gh release upload "$TAG" "$ASSET_NAME" --repo "$REPO" --clobber
echo "Upload completed successfully!"
