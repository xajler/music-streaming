#!/usr/bin/env python3
"""
Inventory script for Esoteric DSD Library
Compares source (SACD ISOs) with target (extracted DSDs)
"""

import os
import re
from pathlib import Path
from collections import defaultdict
import json

SOURCE_PATH = Path("/Volumes/Expansion/00_DSD/00_esoteric")
TARGET_PATH = Path("/Volumes/Untitled/esoteric")

def count_isos(folder: Path) -> list:
    """Count ISO files recursively up to depth 2"""
    isos = []
    for item in folder.rglob("*.iso"):
        # Only include ISOs within 2 levels
        rel = item.relative_to(folder)
        if len(rel.parts) <= 2:
            isos.append(item)
    return isos

def count_dsf_folders(folder: Path) -> list:
    """Find folders containing DSF files"""
    dsf_folders = []
    for item in folder.rglob("*.dsf"):
        parent = item.parent
        if parent not in dsf_folders:
            dsf_folders.append(parent)
    return dsf_folders

def find_disc_folders(album_path: Path) -> list:
    """Find disc folders (Disk1, disc 1, CD1, etc.)"""
    disc_folders = []
    if not album_path.exists():
        return disc_folders
    
    for item in album_path.iterdir():
        if not item.is_dir():
            continue
        name = item.name
        # Pattern: disc/disk/cd + number
        if re.match(r'^(disc|disk|cd)\s*\d+', name, re.IGNORECASE):
            disc_folders.append(item)
        # Pattern: Disc 1 in name (e.g., "Carmen (Disc 1)")
        elif re.search(r'\(Disc\s*\d+\)$', name, re.IGNORECASE):
            disc_folders.append(item)
    
    return disc_folders

def get_expected_discs(folder_name: str) -> int:
    """Parse expected disc count from folder name"""
    # Match patterns like (Esoteric, 2SACD), (Esoteric, 14SACD), (2 discs)
    match = re.search(r'\((\d+)\s*(?:x)?(?:SACD|DSD|discs?)\)', folder_name, re.IGNORECASE)
    if match:
        return int(match.group(1))
    # Match (Esoteric, SACD) - single disc
    if re.search(r'\(Esoteric,\s*(?:SACD|DSD)\)', folder_name) or \
       re.search(r'\(Esoteric,\s*DSDe?\)', folder_name):
        return 1
    return 1

def analyze_album(source_folder: Path, target_folder: Path) -> dict:
    """Analyze a single album comparing source and target"""
    result = {
        "name": source_folder.name,
        "expected_discs": get_expected_discs(source_folder.name),
        "source_isos": [],
        "target_discs": [],
        "sub_albums": [],
        "issues": []
    }
    
    # Check for sub-albums (box sets)
    sub_albums = [d for d in source_folder.iterdir() 
                  if d.is_dir() and not d.name.startswith('.') 
                  and d.name not in ['Artwork', 'Track List Book', 'Scans']]
    
    # Filter to actual album folders (not just supporting folders)
    real_sub_albums = [d for d in sub_albums 
                       if list(d.glob("*.iso")) or 
                          list(d.glob("**/*.dsf")) or
                          any(sd.is_dir() for sd in d.iterdir() if not sd.name.startswith('.'))]
    
    if real_sub_albums and len(real_sub_albums) > 1:
        # Box set - analyze each sub-album
        for sub in real_sub_albums:
            sub_target = target_folder / sub.name.replace("SACD)", ")").replace("DSD)", ")")
            # Try variations of the target name
            if not sub_target.exists():
                sub_target = target_folder / sub.name.replace("(Esoteric, ", "(Esoteric, DSDe, ").replace("SACD)", "DSDe)")
            if not sub_target.exists():
                for t in target_folder.iterdir() if target_folder.exists() else []:
                    if sub.name.split("(")[0].strip() in t.name:
                        sub_target = t
                        break
            
            sub_analysis = analyze_single_album(sub, sub_target)
            result["sub_albums"].append(sub_analysis)
    else:
        # Single album or album with supporting folders only
        single = analyze_single_album(source_folder, target_folder)
        result["source_isos"] = single["source_isos"]
        result["target_discs"] = single["target_discs"]
        result["issues"] = single["issues"]
    
    return result

def analyze_single_album(source: Path, target: Path) -> dict:
    """Analyze a single album (not a box set)"""
    result = {
        "name": source.name,
        "expected_discs": get_expected_discs(source.name),
        "source_isos": [],
        "target_discs": [],
        "issues": []
    }
    
    # Find ISOs in source
    isos = list(source.glob("*.iso"))
    result["source_isos"] = [iso.name for iso in isos]
    
    # Find extracted discs in target
    if target.exists():
        # Check for disc folders
        disc_folders = find_disc_folders(target)
        if disc_folders:
            result["target_discs"] = [d.name for d in disc_folders]
        else:
            # Check if DSF files directly in folder (single disc)
            dsf_files = list(target.glob("*.dsf"))
            if dsf_files:
                result["target_discs"] = ["(root)"]
            else:
                # Check inside sub-folders (nested extraction)
                for sub in target.iterdir():
                    if sub.is_dir() and list(sub.rglob("*.dsf")):
                        nested_discs = find_disc_folders(sub)
                        if nested_discs:
                            result["target_discs"].extend([f"{sub.name}/{d.name}" for d in nested_discs])
                        elif list(sub.glob("*.dsf")):
                            result["target_discs"].append(sub.name)
    
    # Determine issues
    source_count = len(result["source_isos"]) if result["source_isos"] else result["expected_discs"]
    target_count = len(result["target_discs"])
    
    if not target.exists():
        result["issues"].append(f"TARGET_MISSING: {target}")
    elif target_count < source_count:
        missing = source_count - target_count
        result["issues"].append(f"MISSING_DISCS: {missing} of {source_count}")
    elif any("/" in d for d in result["target_discs"]):
        result["issues"].append("NESTED_STRUCTURE")
    
    return result

def main():
    inventory = {
        "source_path": str(SOURCE_PATH),
        "target_path": str(TARGET_PATH),
        "albums": [],
        "summary": {
            "total_albums": 0,
            "total_source_isos": 0,
            "total_target_discs": 0,
            "albums_complete": 0,
            "albums_missing_discs": 0,
            "albums_missing_entirely": 0
        }
    }
    
    total_isos = 0
    total_extracted = 0
    
    for source_album in sorted(SOURCE_PATH.iterdir()):
        if not source_album.is_dir() or source_album.name.startswith('.'):
            continue
        if source_album.name == 'README.md':
            continue
            
        # Find matching target folder
        target_name = source_album.name
        # Replace SACD/DSD with DSDe in target name
        target_name = re.sub(r'\(Esoteric,\s*(\d+)?x?(SACD|DSD)\)', r'(Esoteric, DSDe)', target_name)
        target_name = re.sub(r'\(Esoteric,\s*DSD\)', r'(Esoteric, DSD)', target_name)  # Keep DSD as-is for some
        
        target_album = TARGET_PATH / target_name
        
        # Try to find if exact name doesn't match
        if not target_album.exists():
            base_name = source_album.name.split("(Esoteric")[0].strip()
            for t in TARGET_PATH.iterdir():
                if base_name in t.name:
                    target_album = t
                    break
        
        analysis = analyze_album(source_album, target_album)
        inventory["albums"].append(analysis)
        
        # Count ISOs and extractions
        if analysis["sub_albums"]:
            for sub in analysis["sub_albums"]:
                iso_count = len(sub["source_isos"])
                disc_count = len(sub["target_discs"])
                total_isos += iso_count if iso_count else sub["expected_discs"]
                total_extracted += disc_count
        else:
            iso_count = len(analysis["source_isos"])
            disc_count = len(analysis["target_discs"])
            total_isos += iso_count if iso_count else analysis["expected_discs"]
            total_extracted += disc_count
        
        inventory["summary"]["total_albums"] += 1
    
    inventory["summary"]["total_source_isos"] = total_isos
    inventory["summary"]["total_target_discs"] = total_extracted
    
    # Print summary
    print("=" * 70)
    print("ESOTERIC LIBRARY INVENTORY")
    print("=" * 70)
    print(f"Source: {SOURCE_PATH}")
    print(f"Target: {TARGET_PATH}")
    print()
    
    # Print albums with issues
    print("ALBUMS WITH ISSUES:")
    print("-" * 70)
    
    for album in inventory["albums"]:
        has_issues = False
        
        if album["sub_albums"]:
            # Box set
            box_issues = []
            for sub in album["sub_albums"]:
                if sub["issues"]:
                    box_issues.append((sub["name"], sub["issues"], sub["source_isos"], sub["target_discs"]))
            
            if box_issues:
                has_issues = True
                print(f"\n[BOX SET] {album['name']}")
                for sub_name, issues, isos, discs in box_issues:
                    print(f"  [{sub_name}]")
                    print(f"    Source ISOs: {isos if isos else '(DSD files)'}")
                    print(f"    Target discs: {discs}")
                    for issue in issues:
                        print(f"    ISSUE: {issue}")
        else:
            if album["issues"]:
                has_issues = True
                print(f"\n[ALBUM] {album['name']}")
                print(f"  Expected: {album['expected_discs']} discs")
                print(f"  Source ISOs: {album['source_isos'] if album['source_isos'] else '(DSD files)'}")
                print(f"  Target discs: {album['target_discs']}")
                for issue in album["issues"]:
                    print(f"  ISSUE: {issue}")
    
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total albums scanned: {inventory['summary']['total_albums']}")
    print(f"Total source discs (ISOs): {total_isos}")
    print(f"Total extracted discs: {total_extracted}")
    print(f"Missing extractions: {total_isos - total_extracted}")
    
    # Save JSON
    with open("/Users/x/src/music-streaming/scripts/esoteric-inventory.json", "w") as f:
        json.dump(inventory, f, indent=2)
    print(f"\nJSON saved to: /Users/x/src/music-streaming/scripts/esoteric-inventory.json")

if __name__ == "__main__":
    main()
