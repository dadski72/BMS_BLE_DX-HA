# Define repository and asset name
REPO=dadski72/BMS_BLE_DX-HA
ASSET_NAME=bms_ble.zip
MANIFEST=custom_components/bms_ble/manifest.json

# Auto-bump the integration version before releasing. Defaults to a patch bump;
# pass "major", "minor", or "patch" as the first argument to choose the part.
# Home Assistant blocks custom integrations whose manifest version is a commit
# hash, so the manifest version doubles as the release tag.
BUMP_PART="${1:-patch}"
echo "Bumping manifest version ($BUMP_PART)..."
TAG=$(python3 - "$MANIFEST" "$BUMP_PART" <<'PY'
import json, re, sys

path, part = sys.argv[1], sys.argv[2]
if part not in {"major", "minor", "patch"}:
    sys.exit(f"Invalid bump part: {part!r} (use major, minor, or patch)")

text = open(path, encoding="utf-8").read()
current = json.loads(text)["version"]
m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", current)
if not m:
    sys.exit(f"Cannot auto-bump non-numeric version: {current!r}")

major, minor, patch = (int(x) for x in m.groups())
if part == "major":
    major, minor, patch = major + 1, 0, 0
elif part == "minor":
    minor, patch = minor + 1, 0
else:
    patch += 1
new = f"{major}.{minor}.{patch}"

# Replace only the version value to preserve the manifest's formatting.
text, n = re.subn(
    rf'("version"\s*:\s*)"{re.escape(current)}"', rf'\1"{new}"', text
)
if n != 1:
    sys.exit("Failed to update version in manifest")
open(path, "w", encoding="utf-8").write(text)
print(new)
PY
) || exit 1
echo "New version / release tag: $TAG"

# Commit and push all changes (including the version bump above).
echo "Committing and pushing changes..."
git add .
git commit -m "Release $TAG" || echo "No changes to commit"
git push

echo "Creating new release with tag: $TAG"

# Create the release for this tag, or reuse it if it already exists so the
# script can be re-run (e.g. to re-upload the asset) without failing.
if gh release view "$TAG" --repo "$REPO" >/dev/null 2>&1; then
    echo "Release $TAG already exists; reusing it and updating the asset."
else
    echo "Creating GitHub release..."
    gh release create "$TAG" --repo "$REPO" --title "Release $TAG" --notes "Automated release $TAG" || exit 1
fi

# Remove existing zip file if it exists
if [ -f "$ASSET_NAME" ]; then
    echo "Removing existing $ASSET_NAME..."
    rm "$ASSET_NAME"
fi

# Create the zip file with proper directory structure
echo "Creating zip file: $ASSET_NAME"
cd custom_components/bms_ble || exit 1
# Repo root is two levels up from here, so write the zip there (not three).
7zz a -tzip "../../$ASSET_NAME" . -r '-x!__pycache__' '-x!*.pyc'
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
