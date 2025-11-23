#!/bin/bash

# Akane Theme - Terminal Color Test Script
# This script displays all ANSI colors to verify the theme is applied correctly

echo "=== Akane Theme - Terminal Color Test ==="
echo ""

# Test basic colors
echo "Background and Foreground:"
echo -e "This text should be peach (#F4B999) on oxford-blue (#0E1E36) background"
echo ""

# Normal colors (0-7)
echo "Normal Colors (0-7):"
echo -e "\e[30m█████\e[0m  0: Black (oxford-blue #0E1E36)"
echo -e "\e[31m█████\e[0m  1: Red (amaranth #D2495B)"
echo -e "\e[32m█████\e[0m  2: Green (old-rose #BE6F76)"
echo -e "\e[33m█████\e[0m  3: Yellow (peach #F4B999)"
echo -e "\e[34m█████\e[0m  4: Blue (english-violet #574F72)"
echo -e "\e[35m█████\e[0m  5: Magenta (quinacridone-magenta #763C5D)"
echo -e "\e[36m█████\e[0m  6: Cyan (african-violet #9279AA)"
echo -e "\e[37m█████\e[0m  7: White (coral-pink #FA7E75)"
echo ""

# Bright colors (8-15)
echo "Bright Colors (8-15):"
echo -e "\e[90m█████\e[0m  8: Bright Black (dark-purple #4A2036)"
echo -e "\e[91m█████\e[0m  9: Bright Red (coral-pink #FA7E75)"
echo -e "\e[92m█████\e[0m 10: Bright Green (blush #C85670)"
echo -e "\e[93m█████\e[0m 11: Bright Yellow (peach #F4B999)"
echo -e "\e[94m█████\e[0m 12: Bright Blue (african-violet #9279AA)"
echo -e "\e[95m█████\e[0m 13: Bright Magenta (old-rose #BE6F76)"
echo -e "\e[96m█████\e[0m 14: Bright Cyan (blush #C85670)"
echo -e "\e[97m█████\e[0m 15: Bright White (peach #F4B999)"
echo ""

# 256-color palette test
echo "256-Color Palette (first 16 colors):"
for i in {0..15}; do
    echo -ne "\e[48;5;${i}m   \e[0m"
    [ $((($i + 1) % 8)) -eq 0 ] && echo ""
done
echo ""

# Text formatting
echo "Text Formatting:"
echo -e "\e[1mBold text\e[0m"
echo -e "\e[3mItalic text\e[0m"
echo -e "\e[4mUnderlined text\e[0m"
echo -e "\e[1;31mBold Red (errors)\e[0m"
echo -e "\e[3;35mItalic Magenta (special)\e[0m"
echo ""

# Color combinations
echo "Common Syntax Highlighting Examples:"
echo -e "\e[36m# Comment in violet\e[0m"
echo -e "\e[35mfunction\e[0m \e[1;36mmy_function\e[0m() {"
echo -e "    \e[32mlocal\e[0m \e[33mvariable\e[0m=\e[37m\"string value\"\e[0m"
echo -e "    \e[1;31mecho\e[0m \e[33m\$variable\e[0m"
echo -e "}"
echo ""

# Selection and cursor test
echo "Selection Colors:"
echo -e "Selected text should have \e[7mafrican-violet (#9279AA) background\e[0m"
echo ""

# Diagnostic colors
echo "Diagnostic Colors:"
echo -e "\e[31m✗ Error: amaranth (#D2495B)\e[0m"
echo -e "\e[37m⚠ Warning: coral-pink (#FA7E75)\e[0m"
echo -e "\e[36mℹ Info: african-violet (#9279AA)\e[0m"
echo -e "\e[32m✓ Success: old-rose (#BE6F76)\e[0m"
echo ""

echo "=== Test Complete ==="
echo "If colors match the descriptions, the theme is correctly applied!"
