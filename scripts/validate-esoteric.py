#!/usr/bin/env python3
"""
Esoteric DSD Library Validation and Sync Script

Validates extracted DSD files against source SACD ISOs, fixes structural issues,
and generates a report for subsequent esoteric-flac sync.

Usage:
    python validate-esoteric.py --dry-run          # Show what would be done
    python validate-esoteric.py --fix              # Execute fixes
    python validate-esoteric.py --album "Carmen"   # Check specific album
"""

import os
import re
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional

# Default paths - can be overridden via CLI
DEFAULT_SOURCE = "/Volumes/Expansion/00_DSD/00_esoteric"
DEFAULT_TARGET = "/Volumes/Untitled/esoteric"


class EsotericValidator:
    def __init__(self, source_path: str, target_path: str, dry_run: bool = True):
        self.source_path = Path(source_path)
        self.target_path = Path(target_path)
        self.dry_run = dry_run
        
        self.report = {
            "generated": datetime.now().isoformat(),
            "source": str(self.source_path),
            "target": str(self.target_path),
            "dry_run": dry_run,
            "missing_discs": [],
            "missing_albums": [],
            "fixes_applied": [],
            "summary": {
                "albums_scanned": 0,
                "albums_ok": 0,
                "missing_discs_count": 0,
                "missing_albums_count": 0,
                "nested_folders_fixed": 0,
                "disc_renames": 0,
                "symlinks_removed": 0,
                "covers_copied": 0,
            }
        }
    
    def get_expected_disc_count(self, folder_name: str, source_path: Path = None) -> int:
        """Parse disc count from source folder name or count source disc folders"""
        # First try to get count from folder name pattern
        match = re.search(r'\(Esoteric,\s*(\d+)?x?(SACD|DSD)\)', folder_name)
        if match:
            count = match.group(1)
            if count:
                return int(count)
        
        # If no count in name and source path provided, count disc folders or ISOs
        if source_path and source_path.exists():
            disc_folders = self.find_disc_folders(source_path)
            if disc_folders:
                return len(disc_folders)
            # Count ISO files
            isos = list(source_path.glob("*.iso"))
            if isos:
                return len(isos)
        
        return 1
    
    def is_dsd_album(self, folder_name: str) -> bool:
        """Check if album is original DSD (not extracted from SACD)"""
        return bool(re.search(r'\(Esoteric,\s*[\d]*DSD\)', folder_name))
    
    def get_target_folder_name(self, source_name: str) -> str:
        """Convert source folder name to expected target folder name"""
        return re.sub(r'\(Esoteric,\s*\d*x?SACD\)', '(Esoteric, DSDe)', source_name)
    
    def find_disc_folders(self, album_path: Path) -> list:
        """Find all disc folders in an album"""
        disc_folders = []
        if not album_path.exists():
            return disc_folders
        
        for item in album_path.iterdir():
            if not item.is_dir():
                continue
            name = item.name
            
            # Pattern 1: "disc 1", "Disc1", "CD1", "Disk 2", etc.
            disc_match = re.match(r'^(disc|disk|cd)\s*(\d+)', name, re.IGNORECASE)
            if disc_match:
                disc_folders.append({
                    "path": item,
                    "name": item.name,
                    "disc_num": int(disc_match.group(2)),
                    "pattern": disc_match.group(1)
                })
                continue
            
            # Pattern 2: "Album Name (Disc 1)" - sacd_extract naming
            disc_match = re.search(r'\(Disc\s*(\d+)\)$', name, re.IGNORECASE)
            if disc_match:
                disc_folders.append({
                    "path": item,
                    "name": item.name,
                    "disc_num": int(disc_match.group(1)),
                    "pattern": "extracted"
                })
                continue
        
        return sorted(disc_folders, key=lambda x: x["disc_num"])
    
    def find_nested_extraction_folder(self, disc_path: Path) -> Optional[Path]:
        """Find nested folder created by sacd_extract inside disc folder"""
        if not disc_path.exists():
            return None
        subdirs = [d for d in disc_path.iterdir() if d.is_dir() and not d.is_symlink()]
        if list(disc_path.glob("*.dsf")):
            return None
        for subdir in subdirs:
            if list(subdir.glob("*.dsf")):
                return subdir
        return None
    
    def find_symlinks(self, path: Path) -> list:
        """Find all symlinks recursively in path"""
        symlinks = []
        if not path.exists():
            return symlinks
        for item in path.rglob("*"):
            if item.is_symlink():
                symlinks.append(item)
        return symlinks
    
    def find_cover_in_source(self, source_album: Path) -> Optional[Path]:
        """Find cover image in source album folder"""
        for name in ["cover.jpg", "folder.jpg", "Cover.jpg", "Folder.jpg"]:
            cover = source_album / name
            if cover.exists():
                return cover
        artwork = source_album / "Artwork"
        if artwork.exists():
            for name in ["cover.jpg", "folder.jpg", "front.jpg"]:
                cover = artwork / name
                if cover.exists():
                    return cover
        return None
    
    def flatten_nested_folder(self, disc_path: Path, nested_path: Path) -> bool:
        """Move files from nested folder up to disc folder"""
        if self.dry_run:
            print(f"  [DRY-RUN] Would flatten: {nested_path.name}/ -> {disc_path.name}/")
            return True
        try:
            for item in nested_path.iterdir():
                dest = disc_path / item.name
                if dest.exists():
                    print(f"  [WARNING] Destination exists, skipping: {dest}")
                    continue
                shutil.move(str(item), str(dest))
            nested_path.rmdir()
            print(f"  [FIXED] Flattened: {nested_path.name}/ -> {disc_path.name}/")
            return True
        except Exception as e:
            print(f"  [ERROR] Failed to flatten {nested_path}: {e}")
            return False
    
    def rename_disc_folder(self, old_path: Path, new_name: str) -> bool:
        """Rename disc folder to standardized name"""
        new_path = old_path.parent / new_name
        if self.dry_run:
            print(f"  [DRY-RUN] Would rename: {old_path.name} -> {new_name}")
            return True
        if new_path.exists():
            print(f"  [WARNING] Target exists, skipping rename: {new_path}")
            return False
        try:
            old_path.rename(new_path)
            print(f"  [FIXED] Renamed: {old_path.name} -> {new_name}")
            return True
        except Exception as e:
            print(f"  [ERROR] Failed to rename {old_path}: {e}")
            return False
    
    def remove_symlink(self, symlink_path: Path) -> bool:
        """Remove a symlink"""
        if self.dry_run:
            target = os.readlink(symlink_path) if symlink_path.is_symlink() else "unknown"
            print(f"  [DRY-RUN] Would remove symlink: {symlink_path.name} -> {target}")
            return True
        try:
            symlink_path.unlink()
            print(f"  [FIXED] Removed symlink: {symlink_path}")
            return True
        except Exception as e:
            print(f"  [ERROR] Failed to remove symlink {symlink_path}: {e}")
            return False
    
    def copy_cover(self, source_cover: Path, target_album: Path) -> bool:
        """Copy cover art to target album"""
        target_cover = target_album / "cover.jpg"
        if target_cover.exists():
            return False
        if self.dry_run:
            print(f"  [DRY-RUN] Would copy cover: {source_cover.name} -> cover.jpg")
            return True
        try:
            shutil.copy2(str(source_cover), str(target_cover))
            print(f"  [FIXED] Copied cover: {source_cover.name} -> cover.jpg")
            return True
        except Exception as e:
            print(f"  [ERROR] Failed to copy cover: {e}")
            return False
    
    def process_album(self, source_album: Path, filter_name: Optional[str] = None):
        """Process a single album"""
        source_name = source_album.name
        if filter_name and filter_name.lower() not in source_name.lower():
            return
        
        self.report["summary"]["albums_scanned"] += 1
        
        if self.is_dsd_album(source_name):
            print(f"\n[SKIP] DSD album (not extracted): {source_name}")
            return
        
        expected_discs = self.get_expected_disc_count(source_name)
        target_name = self.get_target_folder_name(source_name)
        target_album = self.target_path / target_name
        
        print(f"\n[ALBUM] {source_name}")
        print(f"  Expected discs: {expected_discs}")
        print(f"  Target: {target_name}")
        
        if not target_album.exists():
            print(f"  [MISSING] Album not found in target!")
            self.report["missing_albums"].append({
                "source_folder": str(source_album),
                "expected_target": target_name
            })
            self.report["summary"]["missing_albums_count"] += 1
            return
        
        sub_albums = self.find_sub_albums(source_album, target_album)
        if sub_albums:
            print(f"  [BOX SET] Processing {len(sub_albums)} sub-albums...")
            for src_sub, tgt_sub in sub_albums:
                self.process_sub_album(src_sub, tgt_sub, source_album)
            return
        
        self.process_single_album(source_album, target_album, expected_discs)
    
    def find_sub_albums(self, source_album: Path, target_album: Path) -> list:
        """Find sub-albums in box sets"""
        sub_albums = []
        for item in source_album.iterdir():
            if not item.is_dir():
                continue
            if item.name.lower() in ["artwork", "art", "scans", "art_box&booklet"]:
                continue
            has_iso = list(item.glob("*.iso"))
            is_sub_album = has_iso or "SACD" in item.name or "Esoteric" in item.name
            if is_sub_album:
                target_sub_name = self.get_target_folder_name(item.name)
                target_sub = target_album / target_sub_name
                if not target_sub.exists():
                    for tgt_item in target_album.iterdir():
                        if tgt_item.is_dir():
                            src_base = re.sub(r'\s*\(Esoteric.*\)$', '', item.name)
                            tgt_base = re.sub(r'\s*\(Esoteric.*\)$', '', tgt_item.name)
                            if src_base.lower() == tgt_base.lower():
                                target_sub = tgt_item
                                break
                sub_albums.append((item, target_sub))
        return sub_albums
    
    def process_sub_album(self, source_sub: Path, target_sub: Path, parent_source: Path):
        """Process a sub-album within a box set"""
        source_name = source_sub.name
        expected_discs = self.get_expected_disc_count(source_name, source_sub)
        print(f"\n  [SUB-ALBUM] {source_name}")
        print(f"    Expected discs: {expected_discs}")
        if not target_sub.exists():
            print(f"    [MISSING] Sub-album not found!")
            self.report["missing_albums"].append({
                "source_folder": str(source_sub),
                "expected_target": str(target_sub),
                "parent": str(parent_source)
            })
            self.report["summary"]["missing_albums_count"] += 1
            return
        self.process_single_album(source_sub, target_sub, expected_discs, indent="    ")
    
    def find_extraction_wrapper_folder(self, album_path: Path) -> Optional[Path]:
        """Find extraction wrapper folder (e.g., 'Wagner_ Das Rheingold/') that contains disc folders"""
        if not album_path.exists():
            return None
        for item in album_path.iterdir():
            if not item.is_dir() or item.is_symlink():
                continue
            # Skip if it looks like a disc folder
            if re.match(r'^(disc|disk|cd)\s*\d+', item.name, re.IGNORECASE):
                return None
            if re.search(r'\(Disc\s*\d+\)$', item.name, re.IGNORECASE):
                return None
            # Check if this folder contains disc folders
            if self.find_disc_folders(item):
                return item
        return None
    
    def process_single_album(self, source_album: Path, target_album: Path, 
                            expected_discs: int, indent: str = "  "):
        """Process validation and fixes for a single album"""
        album_ok = True
        
        symlinks = self.find_symlinks(target_album)
        for symlink in symlinks:
            if self.remove_symlink(symlink):
                self.report["fixes_applied"].append({
                    "type": "remove_symlink",
                    "path": str(symlink),
                    "album": target_album.name
                })
                self.report["summary"]["symlinks_removed"] += 1
        
        # Check for extraction wrapper folder (e.g., "Wagner_ Das Rheingold/")
        wrapper = self.find_extraction_wrapper_folder(target_album)
        working_folder = wrapper if wrapper else target_album
        
        if expected_discs == 1:
            dsf_files = list(target_album.glob("*.dsf"))
            disc_folders = self.find_disc_folders(working_folder)
            if disc_folders and not dsf_files:
                for disc_info in disc_folders:
                    nested = self.find_nested_extraction_folder(disc_info["path"])
                    if nested:
                        if self.flatten_nested_folder(disc_info["path"], nested):
                            self.report["fixes_applied"].append({
                                "type": "flatten_nested",
                                "album": target_album.name,
                                "from": f"{disc_info['name']}/{nested.name}/",
                                "to": f"{disc_info['name']}/"
                            })
                            self.report["summary"]["nested_folders_fixed"] += 1
            elif not dsf_files and not disc_folders:
                print(f"{indent}[WARNING] No DSF files found!")
                album_ok = False
        else:
            disc_folders = self.find_disc_folders(working_folder)
            actual_discs = len(disc_folders)
            print(f"{indent}Found disc folders: {actual_discs}")
            if wrapper:
                print(f"{indent}(inside extraction folder: {wrapper.name}/)")
            
            if actual_discs < expected_discs:
                found_nums = {d["disc_num"] for d in disc_folders}
                for disc_num in range(1, expected_discs + 1):
                    if disc_num not in found_nums:
                        iso_pattern = f"*disc{disc_num}*.iso"
                        isos = list(source_album.glob(iso_pattern))
                        if not isos:
                            isos = list(source_album.glob(f"*disc {disc_num}*.iso"))
                        if not isos:
                            isos = list(source_album.glob(f"*Disc{disc_num}*.iso"))
                        iso_path = str(isos[0]) if isos else "ISO not found"
                        print(f"{indent}[MISSING] Disk{disc_num}")
                        self.report["missing_discs"].append({
                            "album": target_album.name,
                            "source_iso": iso_path,
                            "expected_disc": f"Disk{disc_num}",
                            "source_folder": str(source_album)
                        })
                        self.report["summary"]["missing_discs_count"] += 1
                        album_ok = False
            
            for disc_info in disc_folders:
                disc_path = disc_info["path"]
                disc_num = disc_info["disc_num"]
                nested = self.find_nested_extraction_folder(disc_path)
                if nested:
                    if self.flatten_nested_folder(disc_path, nested):
                        self.report["fixes_applied"].append({
                            "type": "flatten_nested",
                            "album": target_album.name,
                            "from": f"{disc_info['name']}/{nested.name}/",
                            "to": f"{disc_info['name']}/"
                        })
                        self.report["summary"]["nested_folders_fixed"] += 1
                
                expected_name = f"Disk{disc_num}"
                if disc_info["name"] != expected_name:
                    if self.rename_disc_folder(disc_path, expected_name):
                        self.report["fixes_applied"].append({
                            "type": "rename_disc",
                            "album": target_album.name,
                            "from": disc_info["name"],
                            "to": expected_name
                        })
                        self.report["summary"]["disc_renames"] += 1
        
        target_cover = target_album / "cover.jpg"
        if not target_cover.exists():
            source_cover = self.find_cover_in_source(source_album)
            if source_cover:
                if self.copy_cover(source_cover, target_album):
                    self.report["fixes_applied"].append({
                        "type": "copy_cover",
                        "album": target_album.name,
                        "source": source_cover.name
                    })
                    self.report["summary"]["covers_copied"] += 1
            else:
                print(f"{indent}[WARNING] No cover found in source")
        
        if album_ok:
            self.report["summary"]["albums_ok"] += 1
    
    def run(self, filter_album: Optional[str] = None):
        """Run validation on all albums"""
        print(f"Source: {self.source_path}")
        print(f"Target: {self.target_path}")
        print(f"Mode: {'DRY-RUN' if self.dry_run else 'FIXING'}")
        print("=" * 60)
        
        if not self.source_path.exists():
            print(f"ERROR: Source path does not exist: {self.source_path}")
            return
        if not self.target_path.exists():
            print(f"ERROR: Target path does not exist: {self.target_path}")
            return
        
        for item in sorted(self.source_path.iterdir()):
            if item.is_dir():
                self.process_album(item, filter_album)
        self.print_summary()
    
    def print_summary(self):
        """Print summary of findings"""
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        s = self.report["summary"]
        print(f"Albums scanned:        {s['albums_scanned']}")
        print(f"Albums OK:             {s['albums_ok']}")
        print(f"Missing albums:        {s['missing_albums_count']}")
        print(f"Missing discs:         {s['missing_discs_count']}")
        print(f"Nested folders fixed:  {s['nested_folders_fixed']}")
        print(f"Disc renames:          {s['disc_renames']}")
        print(f"Symlinks removed:      {s['symlinks_removed']}")
        print(f"Covers copied:         {s['covers_copied']}")
    
    def save_report(self, output_dir: Path):
        """Save report to JSON and text files"""
        json_path = output_dir / "esoteric-sync-report.json"
        with open(json_path, "w") as f:
            json.dump(self.report, f, indent=2)
        print(f"\nJSON report saved: {json_path}")
        
        txt_path = output_dir / "esoteric-sync-report.txt"
        with open(txt_path, "w") as f:
            f.write("# Esoteric DSD Library Sync Report\n")
            f.write(f"# Generated: {self.report['generated']}\n")
            f.write(f"# Mode: {'DRY-RUN' if self.dry_run else 'APPLIED'}\n")
            f.write("=" * 60 + "\n\n")
            
            if self.report["missing_albums"]:
                f.write("## MISSING ALBUMS\n\n")
                for item in self.report["missing_albums"]:
                    f.write(f"MISSING_ALBUM: {item.get('expected_target', 'Unknown')}\n")
                    f.write(f"  Source: {item['source_folder']}\n\n")
            
            if self.report["missing_discs"]:
                f.write("## MISSING DISCS (require SACD extraction)\n\n")
                for item in self.report["missing_discs"]:
                    f.write(f"MISSING_DISC: {item['album']}\n")
                    f.write(f"  Expected: {item['expected_disc']}\n")
                    f.write(f"  Source ISO: {item['source_iso']}\n")
                    f.write(f"  Source folder: {item['source_folder']}\n\n")
            
            if self.report["fixes_applied"]:
                f.write("## FIXES APPLIED\n\n")
                for fix in self.report["fixes_applied"]:
                    f.write(f"{fix['type'].upper()}: {fix.get('album', '')}\n")
                    if fix["type"] in ["flatten_nested", "rename_disc"]:
                        f.write(f"  {fix['from']} -> {fix['to']}\n")
                    elif fix["type"] == "copy_cover":
                        f.write(f"  Source: {fix['source']}\n")
                    elif fix["type"] == "remove_symlink":
                        f.write(f"  Path: {fix['path']}\n")
                    f.write("\n")
            
            f.write("## SUMMARY\n\n")
            for key, value in self.report["summary"].items():
                f.write(f"{key}: {value}\n")
        print(f"Text report saved: {txt_path}")


def main():
    parser = argparse.ArgumentParser(description="Validate and fix Esoteric DSD library structure")
    parser.add_argument("--source", default=DEFAULT_SOURCE, help=f"Source path. Default: {DEFAULT_SOURCE}")
    parser.add_argument("--target", default=DEFAULT_TARGET, help=f"Target path. Default: {DEFAULT_TARGET}")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--fix", action="store_true", help="Apply fixes (default is dry-run)")
    parser.add_argument("--album", type=str, help="Filter to specific album name (partial match)")
    parser.add_argument("--report-dir", type=str, default=".", help="Directory to save reports")
    
    args = parser.parse_args()
    dry_run = not args.fix
    
    validator = EsotericValidator(source_path=args.source, target_path=args.target, dry_run=dry_run)
    validator.run(filter_album=args.album)
    validator.save_report(Path(args.report_dir))


if __name__ == "__main__":
    main()
