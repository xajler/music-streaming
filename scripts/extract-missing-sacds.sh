#!/bin/bash
# Extract missing SACD ISOs to DSD
# Generated: 2026-01-20

set -e

SACD_EXTRACT="sacd_extract"
SOURCE_BASE="/Volumes/Expansion/00_DSD/00_esoteric"
TARGET_BASE="/Volumes/Untitled/esoteric"

# Check if sacd_extract is available
if ! command -v $SACD_EXTRACT &> /dev/null; then
    echo "ERROR: sacd_extract not found in PATH"
    exit 1
fi

# Check if volumes are mounted
if [ ! -d "$SOURCE_BASE" ]; then
    echo "ERROR: Source volume not mounted: $SOURCE_BASE"
    exit 1
fi

if [ ! -d "$TARGET_BASE" ]; then
    echo "ERROR: Target volume not mounted: $TARGET_BASE"
    exit 1
fi

extract_iso() {
    local iso_path="$1"
    local output_dir="$2"
    local disc_name="$3"
    
    echo ""
    echo "=============================================="
    echo "Extracting: $disc_name"
    echo "ISO: $iso_path"
    echo "Output: $output_dir"
    echo "=============================================="
    
    if [ ! -f "$iso_path" ]; then
        echo "ERROR: ISO not found: $iso_path"
        return 1
    fi
    
    mkdir -p "$output_dir"
    
    # Extract to DSF format with CUE sheet
    # -2 = 2-channel, -s = DSF format, -C = export CUE
    $SACD_EXTRACT -2 -s -C -i "$iso_path" -o "$output_dir"
    
    echo "DONE: $disc_name"
}

echo "=============================================="
echo "SACD Extraction Script"
echo "=============================================="
echo "This will extract 13 missing discs to DSD"
echo ""

# Carmen - Disk2
extract_iso \
    "$SOURCE_BASE/4 Greta Operas Karajan&Callas (Esoteric, 9SACD)/Bizet - Carmen  (Callas 1964, 2012)  (Esoteric, 2SACD)/Bizet - Carmen disc2.iso" \
    "$TARGET_BASE/4 Greta Operas Karajan&Callas (Esoteric, DSDe)/Bizet - Carmen  (Callas 1964, 2012)  (Esoteric, DSDe)/Disk2" \
    "Carmen - Disk2"

# Aida - Disk2
extract_iso \
    "$SOURCE_BASE/4 Greta Operas Karajan&Callas (Esoteric, 9SACD)/Verdi - Aida (Karajan, WP) (Esoteric, 3SACD)/Verdi - Aida disc2.iso" \
    "$TARGET_BASE/4 Greta Operas Karajan&Callas (Esoteric, DSDe)/Verdi - Aida (Karajan, WP) (Esoteric, DSDe)/Disk2" \
    "Aida - Disk2"

# Aida - Disk3
extract_iso \
    "$SOURCE_BASE/4 Greta Operas Karajan&Callas (Esoteric, 9SACD)/Verdi - Aida (Karajan, WP) (Esoteric, 3SACD)/Verdi - Aida disc3.iso" \
    "$TARGET_BASE/4 Greta Operas Karajan&Callas (Esoteric, DSDe)/Verdi - Aida (Karajan, WP) (Esoteric, DSDe)/Disk3" \
    "Aida - Disk3"

# Wagner Ring - Das Rheingold Disk2
extract_iso \
    "$SOURCE_BASE/Wagner - Der Ring Des Nibelungen - Solti (2009) (Esoteric, 14SACD)/1. Vorabend - Das Rheingold 1853-54 (2 discs)/90022.iso" \
    "$TARGET_BASE/Wagner - Der Ring Des Nibelungen - Solti (2009) (Esoteric, DSDe)/1. Vorabend - Das Rheingold 1853-54 (2 discs)/Disk2" \
    "Wagner Rheingold - Disk2"

# Wagner Ring - Die Walkuere Disk2-4
extract_iso \
    "$SOURCE_BASE/Wagner - Der Ring Des Nibelungen - Solti (2009) (Esoteric, 14SACD)/2. Erster Tag - Die Walküre 1854-56 (4 discs)/90024.iso" \
    "$TARGET_BASE/Wagner - Der Ring Des Nibelungen - Solti (2009) (Esoteric, DSDe)/2. Erster Tag - Die Walküre 1854-56 (4 discs)/Disk2" \
    "Wagner Walkuere - Disk2"

extract_iso \
    "$SOURCE_BASE/Wagner - Der Ring Des Nibelungen - Solti (2009) (Esoteric, 14SACD)/2. Erster Tag - Die Walküre 1854-56 (4 discs)/90025.iso" \
    "$TARGET_BASE/Wagner - Der Ring Des Nibelungen - Solti (2009) (Esoteric, DSDe)/2. Erster Tag - Die Walküre 1854-56 (4 discs)/Disk3" \
    "Wagner Walkuere - Disk3"

extract_iso \
    "$SOURCE_BASE/Wagner - Der Ring Des Nibelungen - Solti (2009) (Esoteric, 14SACD)/2. Erster Tag - Die Walküre 1854-56 (4 discs)/90026.iso" \
    "$TARGET_BASE/Wagner - Der Ring Des Nibelungen - Solti (2009) (Esoteric, DSDe)/2. Erster Tag - Die Walküre 1854-56 (4 discs)/Disk4" \
    "Wagner Walkuere - Disk4"

# Wagner Ring - Siegfried Disk2-4
extract_iso \
    "$SOURCE_BASE/Wagner - Der Ring Des Nibelungen - Solti (2009) (Esoteric, 14SACD)/3. Zweiter Tag - Siegfried 1856-71 (4 discs)/90028.iso" \
    "$TARGET_BASE/Wagner - Der Ring Des Nibelungen - Solti (2009) (Esoteric, DSDe)/3. Zweiter Tag - Siegfried 1856-71 (4 discs)/Disk2" \
    "Wagner Siegfried - Disk2"

extract_iso \
    "$SOURCE_BASE/Wagner - Der Ring Des Nibelungen - Solti (2009) (Esoteric, 14SACD)/3. Zweiter Tag - Siegfried 1856-71 (4 discs)/90029.iso" \
    "$TARGET_BASE/Wagner - Der Ring Des Nibelungen - Solti (2009) (Esoteric, DSDe)/3. Zweiter Tag - Siegfried 1856-71 (4 discs)/Disk3" \
    "Wagner Siegfried - Disk3"

extract_iso \
    "$SOURCE_BASE/Wagner - Der Ring Des Nibelungen - Solti (2009) (Esoteric, 14SACD)/3. Zweiter Tag - Siegfried 1856-71 (4 discs)/90030.iso" \
    "$TARGET_BASE/Wagner - Der Ring Des Nibelungen - Solti (2009) (Esoteric, DSDe)/3. Zweiter Tag - Siegfried 1856-71 (4 discs)/Disk4" \
    "Wagner Siegfried - Disk4"

# Wagner Ring - Goetterdaemmerung Disk2-4
extract_iso \
    "$SOURCE_BASE/Wagner - Der Ring Des Nibelungen - Solti (2009) (Esoteric, 14SACD)/4. Dritter Tag - Götterdämmerung 1869-74 (4 discs)/90032.iso" \
    "$TARGET_BASE/Wagner - Der Ring Des Nibelungen - Solti (2009) (Esoteric, DSDe)/4. Dritter Tag - Götterdämmerung 1869-74 (4 discs)/Disk2" \
    "Wagner Goetterdaemmerung - Disk2"

extract_iso \
    "$SOURCE_BASE/Wagner - Der Ring Des Nibelungen - Solti (2009) (Esoteric, 14SACD)/4. Dritter Tag - Götterdämmerung 1869-74 (4 discs)/90033.iso" \
    "$TARGET_BASE/Wagner - Der Ring Des Nibelungen - Solti (2009) (Esoteric, DSDe)/4. Dritter Tag - Götterdämmerung 1869-74 (4 discs)/Disk3" \
    "Wagner Goetterdaemmerung - Disk3"

extract_iso \
    "$SOURCE_BASE/Wagner - Der Ring Des Nibelungen - Solti (2009) (Esoteric, 14SACD)/4. Dritter Tag - Götterdämmerung 1869-74 (4 discs)/90034.iso" \
    "$TARGET_BASE/Wagner - Der Ring Des Nibelungen - Solti (2009) (Esoteric, DSDe)/4. Dritter Tag - Götterdämmerung 1869-74 (4 discs)/Disk4" \
    "Wagner Goetterdaemmerung - Disk4"

echo ""
echo "=============================================="
echo "EXTRACTION COMPLETE"
echo "=============================================="
echo "Extracted 13 discs"
echo ""
echo "Next steps:"
echo "1. Run validate-esoteric.py --fix to fix folder structure"
echo "2. Convert DSD to FLAC for esoteric-flac"
