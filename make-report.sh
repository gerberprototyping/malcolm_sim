#!/bin/bash

#                  A                  B                      C                  D                         E                       F                      G
# SRC_FILES=("rtl/de10_lite.vhd" "rtl/core/csr.vhd" "rtl/lcm/lcmx_v5.vhd" "rtl/lcm/lcm2b.vhd"  "sw/projects/lcm/lcmx.dlx" "sw/projects/lcm/rom.mif" "sw/projects/lcm/lcm12.dlx")
TMP_FILE=".tmp.md"
OUT_FILE="GerberOlsen_CS5110_FinalProject.pdf"


cat > $TMP_FILE << EOF
---
title: Final Project - Malcolm Simulator
subtitle: CS 5110
author: Andrew Gerber, Jordan Olsen
date: \today{}
geometry: margin=1in
documentclass: scrartcl
---

$(cat report.md)

\\pagebreak
EOF


# ALPHABET=({A..Z})
# ALPHABET_INDEX=0
# for FILENAME in "${SRC_FILES[@]}"; do
#     FILE_EXT=$(echo "$FILENAME" | sed -E s,.*\\.,,I )
#     if [ "$FILE_EXT" == "sv" ]; then
#         FILE_EXT="verilog"
#     elif [ "$FILE_EXT" == "dlx" ]; then
#         FILE_EXT="s"
#     elif [ "$FILE_EXT" == "mif" ]; then
#         FILE_EXT="s"
#     fi
#     FILE_CONTENT=$(cat "$FILENAME")
#     cat >> $TMP_FILE << EOF

# \\pagebreak

# # Appendix ${ALPHABET[ALPHABET_INDEX]}
# ## $FILENAME
# \`\`\`$FILE_EXT
# $FILE_CONTENT
# \`\`\`

# EOF
#     ((ALPHABET_INDEX++))
# done


pandoc "$TMP_FILE" -o "$OUT_FILE"

rm "$TMP_FILE"
