#!/bin/bash

# Akane Theme - Color Consistency Verification Script
# This script checks that all configuration files use the same color palette

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Akane Theme - Color Consistency Verification          ║"
echo "╔════════════════════════════════════════════════════════════╗"
echo ""

# Define the core color palette
declare -A COLORS=(
    ["oxford-blue"]="0e1e36"
    ["peach"]="f4b999"
    ["african-violet"]="9279aa"
    ["english-violet"]="574f72"
    ["quinacridone-magenta"]="763c5d"
    ["old-rose"]="be6f76"
    ["blush"]="c85670"
    ["coral-pink"]="fa7e75"
    ["amaranth"]="d2495b"
    ["dark-purple"]="4a2036"
)

# Files to check
FILES=(
    "colors/akane.lua"
    "ghostty.conf"
    "kitty.conf"
    "alacritty.toml"
    "vscode.json"
)

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "Checking color palette consistency across all configuration files..."
echo ""

# Check each color in each file
total_checks=0
passed_checks=0
failed_checks=0

for color_name in "${!COLORS[@]}"; do
    color_value="${COLORS[$color_name]}"
    echo -e "${BLUE}Checking color:${NC} $color_name (${color_value})"

    found_in=()
    missing_from=()

    for file in "${FILES[@]}"; do
        if [ -f "$file" ]; then
            # Case-insensitive search for color value
            if grep -qi "$color_value" "$file"; then
                found_in+=("$file")
            else
                missing_from+=("$file")
            fi
        else
            echo -e "  ${YELLOW}⚠${NC} File not found: $file"
        fi
        ((total_checks++))
    done

    # Report results for this color
    if [ ${#found_in[@]} -gt 0 ]; then
        echo -e "  ${GREEN}✓${NC} Found in: ${found_in[*]}"
        ((passed_checks+=${#found_in[@]}))
    fi

    if [ ${#missing_from[@]} -gt 0 ]; then
        echo -e "  ${RED}✗${NC} Missing from: ${missing_from[*]}"
        ((failed_checks+=${#missing_from[@]}))
    fi

    echo ""
done

# Summary
echo "════════════════════════════════════════════════════════════"
echo "Summary:"
echo "════════════════════════════════════════════════════════════"
echo -e "Total checks: $total_checks"
echo -e "${GREEN}Passed: $passed_checks${NC}"
if [ $failed_checks -gt 0 ]; then
    echo -e "${RED}Failed: $failed_checks${NC}"
else
    echo -e "${GREEN}Failed: 0${NC}"
fi
echo ""

# Check ANSI color mapping consistency
echo "════════════════════════════════════════════════════════════"
echo "ANSI Color Mapping Check (Terminal configs)"
echo "════════════════════════════════════════════════════════════"
echo ""

declare -A ANSI_COLORS=(
    [0]="0e1e36"  # Black -> oxford-blue
    [1]="d2495b"  # Red -> amaranth
    [2]="be6f76"  # Green -> old-rose
    [3]="f4b999"  # Yellow -> peach
    [4]="574f72"  # Blue -> english-violet
    [5]="763c5d"  # Magenta -> quinacridone-magenta
    [6]="9279aa"  # Cyan -> african-violet
    [7]="fa7e75"  # White -> coral-pink
    [8]="4a2036"  # Bright Black -> dark-purple
    [9]="fa7e75"  # Bright Red -> coral-pink
    [10]="c85670" # Bright Green -> blush
    [11]="f4b999" # Bright Yellow -> peach
    [12]="9279aa" # Bright Blue -> african-violet
    [13]="be6f76" # Bright Magenta -> old-rose
    [14]="c85670" # Bright Cyan -> blush
    [15]="f4b999" # Bright White -> peach
)

terminal_files=("ghostty.conf" "kitty.conf" "alacritty.toml" "vscode.json")
ansi_passed=0
ansi_failed=0

for i in "${!ANSI_COLORS[@]}"; do
    expected="${ANSI_COLORS[$i]}"
    echo "ANSI $i -> $expected:"

    for file in "${terminal_files[@]}"; do
        if [ -f "$file" ]; then
            if grep -qi "$expected" "$file"; then
                echo -e "  ${GREEN}✓${NC} $file"
                ((ansi_passed++))
            else
                echo -e "  ${RED}✗${NC} $file (missing $expected)"
                ((ansi_failed++))
            fi
        fi
    done
    echo ""
done

echo "════════════════════════════════════════════════════════════"
echo "ANSI Mapping Summary:"
echo -e "${GREEN}Passed: $ansi_passed${NC}"
if [ $ansi_failed -gt 0 ]; then
    echo -e "${RED}Failed: $ansi_failed${NC}"
else
    echo -e "${GREEN}Failed: 0${NC}"
fi
echo ""

# Final verdict
echo "════════════════════════════════════════════════════════════"
if [ $failed_checks -eq 0 ] && [ $ansi_failed -eq 0 ]; then
    echo -e "${GREEN}✓ ALL CHECKS PASSED!${NC}"
    echo "All configuration files are using consistent colors."
    exit 0
else
    echo -e "${RED}✗ SOME CHECKS FAILED!${NC}"
    echo "Please review the missing colors and update the configurations."
    exit 1
fi
