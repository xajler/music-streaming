#!/bin/bash
# Convert DSD (DSF) files to FLAC for esoteric-flac
# Generated: 2026-01-20

set -e

DSD_BASE="/Volumes/Untitled/esoteric"
FLAC_BASE="/Volumes/Untitled/esoteric-flac"

# Check ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "ERROR: ffmpeg not found"
    exit 1
fi

convert_disc() {
    local dsd_path="$1"
    local flac_path="$2"
    local disc_name="$3"
    
    echo ""
    echo "=============================================="
    echo "Converting: $disc_name"
    echo "From: $dsd_path"
    echo "To: $flac_path"
    echo "=============================================="
    
    if [ ! -d "$dsd_path" ]; then
        echo "ERROR: Source not found: $dsd_path"
        return 1
    fi
    
    mkdir -p "$flac_path"
    
    # Convert each DSF file to FLAC
    for dsf in "$dsd_path"/*.dsf; do
        if [ -f "$dsf" ]; then
            filename=$(basename "$dsf" .dsf)
            output="$flac_path/${filename}.flac"
            
            if [ -f "$output" ]; then
                echo "  Skipping (exists): $filename"
            else
                echo "  Converting: $filename"
                ffmpeg -i "$dsf" -af "lowpass=24000" -sample_fmt s32 -ar 176400 "$output" -y -loglevel error
            fi
        fi
    done
    
    # Copy CUE and XML files if present
    for ext in cue xml; do
        for f in "$dsd_path"/*.$ext; do
            if [ -f "$f" ]; then
                cp "$f" "$flac_path/" 2>/dev/null || true
            fi
        done
    done
    
    echo "DONE: $disc_name"
}

echo "=============================================="
echo "DSD to FLAC Conversion"
echo "=============================================="
echo "Converting 13 discs..."

# Carmen Disk2
convert_disc \
    "$DSD_BASE/4 Greta Operas Karajan&Callas (Esoteric, DSDe)/Bizet - Carmen  (Callas 1964, 2012)  (Esoteric, DSDe)/Disk2" \
    "$FLAC_BASE/4 Greta Operas Karajan&Callas (Esoteric)/Bizet - Carmen  (Callas 1964, 2012)  (Esoteric)/Disk2" \
    "Carmen - Disk2"

# Aida Disk2 and Disk3
convert_disc \
    "$DSD_BASE/4 Greta Operas Karajan&Callas (Esoteric, DSDe)/Verdi - Aida (Karajan, WP) (Esoteric, DSDe)/Disk2" \
    "$FLAC_BASE/4 Greta Operas Karajan&Callas (Esoteric)/Verdi - Aida (Karajan, WP) (Esoteric)/Disk2" \
    "Aida - Disk2"

convert_disc \
    "$DSD_BASE/4 Greta Operas Karajan&Callas (Esoteric, DSDe)/Verdi - Aida (Karajan, WP) (Esoteric, DSDe)/Disk3" \
    "$FLAC_BASE/4 Greta Operas Karajan&Callas (Esoteric)/Verdi - Aida (Karajan, WP) (Esoteric)/Disk3" \
    "Aida - Disk3"

# Wagner Ring
RING_DSD="$DSD_BASE/Wagner - Der Ring Des Nibelungen - Solti (2009) (Esoteric, DSDe)"
RING_FLAC="$FLAC_BASE/Wagner - Der Ring Des Nibelungen - Solti (2009) (Esoteric)"

# Rheingold Disk2
convert_disc \
    "$RING_DSD/1. Vorabend - Das Rheingold 1853-54 (2 discs)/Disk2" \
    "$RING_FLAC/1. Vorabend - Das Rheingold 1853-54 (2 discs)/Disk2" \
    "Wagner Rheingold - Disk2"

# Walkure Disk2-4
convert_disc \
    "$RING_DSD/2. Erster Tag - Die Walküre 1854-56 (4 discs)/Disk2" \
    "$RING_FLAC/2. Erster Tag - Die Walküre 1854-56 (4 discs)/Disk2" \
    "Wagner Walkure - Disk2"

convert_disc \
    "$RING_DSD/2. Erster Tag - Die Walküre 1854-56 (4 discs)/Disk3" \
    "$RING_FLAC/2. Erster Tag - Die Walküre 1854-56 (4 discs)/Disk3" \
    "Wagner Walkure - Disk3"

convert_disc \
    "$RING_DSD/2. Erster Tag - Die Walküre 1854-56 (4 discs)/Disk4" \
    "$RING_FLAC/2. Erster Tag - Die Walküre 1854-56 (4 discs)/Disk4" \
    "Wagner Walkure - Disk4"

# Siegfried Disk2-4
convert_disc \
    "$RING_DSD/3. Zweiter Tag - Siegfried 1856-71 (4 discs)/Disk2" \
    "$RING_FLAC/3. Zweiter Tag - Siegfried 1856-71 (4 discs)/Disk2" \
    "Wagner Siegfried - Disk2"

convert_disc \
    "$RING_DSD/3. Zweiter Tag - Siegfried 1856-71 (4 discs)/Disk3" \
    "$RING_FLAC/3. Zweiter Tag - Siegfried 1856-71 (4 discs)/Disk3" \
    "Wagner Siegfried - Disk3"

convert_disc \
    "$RING_DSD/3. Zweiter Tag - Siegfried 1856-71 (4 discs)/Disk4" \
    "$RING_FLAC/3. Zweiter Tag - Siegfried 1856-71 (4 discs)/Disk4" \
    "Wagner Siegfried - Disk4"

# Gotterdammerung Disk2-4
convert_disc \
    "$RING_DSD/4. Dritter Tag - Götterdämmerung 1869-74 (4 discs)/Disk2" \
    "$RING_FLAC/4. Dritter Tag - Götterdämmerung 1869-74 (4 discs)/Disk2" \
    "Wagner Gotterdammerung - Disk2"

convert_disc \
    "$RING_DSD/4. Dritter Tag - Götterdämmerung 1869-74 (4 discs)/Disk3" \
    "$RING_FLAC/4. Dritter Tag - Götterdämmerung 1869-74 (4 discs)/Disk3" \
    "Wagner Gotterdammerung - Disk3"

convert_disc \
    "$RING_DSD/4. Dritter Tag - Götterdämmerung 1869-74 (4 discs)/Disk4" \
    "$RING_FLAC/4. Dritter Tag - Götterdämmerung 1869-74 (4 discs)/Disk4" \
    "Wagner Gotterdammerung - Disk4"

echo ""
echo "=============================================="
echo "CONVERSION COMPLETE"
echo "=============================================="
echo "Converted 13 discs from DSD to FLAC"
