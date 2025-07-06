# Commit and push all changes
echo "Committing and pushing changes..."
git add .
git commit -m "Auto-commit before release upload" || echo "No changes to commit"
git push

# Define repository and asset name
REPO=dadski72/BMS_BLE_DX-HA
ASSET_NAME=bms_ble_dx.zip

# Get the latest commit hash as the new tag
echo "Getting latest commit hash for new release tag..."
COMMIT_HASH=$(git rev-parse --short HEAD)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
#TAG="${COMMIT_HASH}_${TIMESTAMP}"
TAG="${COMMIT_HASH}"
echo "Creating new release with tag: $TAG"

# Create a new release with the current commit
echo "Creating GitHub release..."
gh release create $TAG --repo $REPO --title "Release $TAG" --notes "Automated release for commit $TAG" --prerelease

# Remove existing zip file if it exists
if [ -f "$ASSET_NAME" ]; then
    echo "Removing existing $ASSET_NAME..."
    rm "$ASSET_NAME"
fi

# Create the zip file with proper directory structure
echo "Creating zip file: $ASSET_NAME"
7z a -tzip "$ASSET_NAME" "./custom_components/bms_ble/*" -r

# Verify the zip file was created successfully
if [ -f "$ASSET_NAME" ]; then
    echo "Zip file created successfully. Size: $(du -h "$ASSET_NAME" | cut -f1)"
    echo "Contents preview:"
    7z l "$ASSET_NAME" | head -15
else
    echo "ERROR: Failed to create zip file!"
    exit 1
fi

echo "Uploading asset: $ASSET_NAME to release $TAG"
gh release upload $TAG $ASSET_NAME --repo $REPO --clobber
echo "Upload completed successfully!"
