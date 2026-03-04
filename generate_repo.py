#!/usr/bin/env python3
"""
Generate Kodi repository files: addons.xml, addons.xml.md5, and addon zip files.

Usage:
    python generate_repo.py

This script scans for addon directories containing addon.xml,
generates the combined addons.xml, its MD5 checksum, and creates
properly-named zip files in a separate 'zips/' directory.
"""

import hashlib
import os
import re
import shutil
import zipfile
from xml.etree import ElementTree as ET


REPO_DIR = os.path.dirname(os.path.abspath(__file__))
ZIPS_DIR = os.path.join(REPO_DIR, "zips")

# Addon directories to include in the repository
ADDON_DIRS = [
    "plugin.video.vietmediaF",
    "repo_vietmediaf_fork",
]

# Files/directories to exclude from zip
ZIP_EXCLUDE_DIRS = {
    "__pycache__", ".git", ".vscode", ".idea",
}

ZIP_EXCLUDE_EXTENSIONS = {
    ".pyc", ".pyo", ".pyd", ".zip",
}

ZIP_EXCLUDE_FILES = {
    ".DS_Store", "Thumbs.db", ".gitignore",
}


def should_exclude(name, is_dir=False):
    """Check if a file/directory should be excluded from the zip."""
    if is_dir:
        return name in ZIP_EXCLUDE_DIRS
    if name in ZIP_EXCLUDE_FILES:
        return True
    _, ext = os.path.splitext(name)
    return ext in ZIP_EXCLUDE_EXTENSIONS


def get_addon_info(addon_dir):
    """Read addon.xml and return (addon_id, version, xml_content)."""
    addon_xml_path = os.path.join(REPO_DIR, addon_dir, "addon.xml")
    if not os.path.exists(addon_xml_path):
        print(f"  [SKIP] {addon_dir}: addon.xml not found")
        return None

    with open(addon_xml_path, "r", encoding="utf-8") as f:
        content = f.read()

    tree = ET.parse(addon_xml_path)
    root = tree.getroot()
    addon_id = root.get("id")
    version = root.get("version")

    print(f"  [OK] {addon_id} v{version}")
    return addon_id, version, content


def generate_addons_xml(addon_infos):
    """Generate addons.xml from collected addon info."""
    lines = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', "<addons>"]

    for _, _, xml_content in addon_infos:
        cleaned = re.sub(r'<\?xml[^?]*\?>\s*', '', xml_content).strip()
        lines.append(cleaned)

    lines.append("</addons>")

    addons_xml = "\n".join(lines)
    addons_xml_path = os.path.join(REPO_DIR, "addons.xml")

    with open(addons_xml_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(addons_xml)

    print(f"\n[CREATED] addons.xml ({len(addon_infos)} addons)")
    return addons_xml


def generate_addons_xml_md5(addons_xml_content):
    """Generate addons.xml.md5 file."""
    md5_hash = hashlib.md5(addons_xml_content.encode("utf-8")).hexdigest()
    md5_path = os.path.join(REPO_DIR, "addons.xml.md5")

    with open(md5_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(md5_hash)

    print(f"[CREATED] addons.xml.md5 ({md5_hash})")
    return md5_hash


def create_addon_zip(addon_dir, addon_id, version):
    """Create a Kodi-compatible zip file in the zips/ directory.

    Output: zips/{addon_id}/{addon_id}-{version}.zip
    Completely separate from the source addon directory.
    """
    source_dir = os.path.join(REPO_DIR, addon_dir)

    # Output to zips/{addon_id}/
    zip_out_dir = os.path.join(ZIPS_DIR, addon_id)
    os.makedirs(zip_out_dir, exist_ok=True)

    zip_filename = f"{addon_id}-{version}.zip"
    zip_path = os.path.join(zip_out_dir, zip_filename)

    # Remove old zip if exists
    if os.path.exists(zip_path):
        os.remove(zip_path)

    file_count = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if not should_exclude(d, is_dir=True)]

            for filename in files:
                if should_exclude(filename):
                    continue

                filepath = os.path.join(root, filename)
                arcname = os.path.join(
                    addon_id,
                    os.path.relpath(filepath, source_dir)
                )
                zf.write(filepath, arcname)
                file_count += 1

    zip_size_kb = os.path.getsize(zip_path) / 1024
    print(f"[CREATED] zips/{addon_id}/{zip_filename} ({zip_size_kb:.1f} KB, {file_count} files)")


def main():
    print("=" * 60)
    print("Kodi Repository Generator")
    print("=" * 60)
    print(f"\nRepo directory: {REPO_DIR}")
    print(f"Zips directory: {ZIPS_DIR}")
    print(f"\nScanning addon directories...")

    addon_infos = []
    for addon_dir in ADDON_DIRS:
        info = get_addon_info(addon_dir)
        if info:
            addon_infos.append((addon_dir, info))

    if not addon_infos:
        print("\n[ERROR] No addons found!")
        return

    # Generate addons.xml
    addons_xml = generate_addons_xml([info for _, info in addon_infos])

    # Generate addons.xml.md5
    generate_addons_xml_md5(addons_xml)

    # Create zip files
    print()
    zip_files = []
    for addon_dir, (addon_id, version, _) in addon_infos:
        create_addon_zip(addon_dir, addon_id, version)
        zip_files.append((addon_id, version))

    # Copy zips to root for Kodi file manager visibility
    print()
    for addon_id, version in zip_files:
        zip_filename = f"{addon_id}-{version}.zip"
        src = os.path.join(ZIPS_DIR, addon_id, zip_filename)
        dst = os.path.join(REPO_DIR, zip_filename)
        shutil.copy2(src, dst)
        print(f"[COPIED] {zip_filename} -> root/")

    print(f"\n{'=' * 60}")
    print("Done! Remember to commit and push to update the repository.")
    print("=" * 60)


if __name__ == "__main__":
    main()
