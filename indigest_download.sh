#!/bin/bash
set -euo pipefail

################################################################################
#                                                                              #
# indigest_download                                                            #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program downloads PDFs linked from a given HTML file using a            #
# cookies.txt file.                                                            #
#                                                                              #
# copyright (C) 2025 Will Breaden Madden, wbm@protonmail.ch                    #
#                                                                              #
# This software is released under the terms of the GNU General Public License  #
# version 3 (GPLv3).                                                           #
#                                                                              #
# This program is free software: you can redistribute it and/or modify it      #
# under the terms of the GNU General Public License as published by the Free   #
# Software Foundation, either version 3 of the License, or (at your option)    #
# any later version.                                                           #
#                                                                              #
# This program is distributed in the hope that it will be useful, but WITHOUT  #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or        #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for     #
# more details.                                                                #
#                                                                              #
# For a copy of the GNU General Public License, see                            #
# <http://www.gnu.org/licenses>.                                               #
#                                                                              #
################################################################################

version="2025-07-21T2204Z"

# Configuration
downloads_directory="downloads"              # directory to store downloads
HTML_file="page.html"                        # HTML file with PDF links
cookies_file="cookies.txt"                   # exported cookies.txt
user_agent="Mozilla/5.0 (X11; Linux x86_64)" # User-Agent
prefix="Indico_"                             # prefix for download directories and optionally for files
regularise_filenames=true                    # change filenames to include the prefix

# Verify that the HTML and cookie files exist at the working directory.
if [[ ! -f "${HTML_file}" ]]; then
    echo "Error: HTML file '${HTML_file}' not found." >&2
    exit 1
fi

if [[ ! -f "${cookies_file}" ]]; then
    echo "Error: Cookies file '${cookies_file}' not found." >&2
    exit 1
fi

# Ensure a downloads directory exists at the working directory and change to it.
mkdir -p "${downloads_directory}"
pushd "${downloads_directory}" > /dev/null

# Extract URLs for PDFs from the HTML file.
mapfile -t URLS < <(
    grep -Eo 'https://[^"]+\.pdf' "../${HTML_file}" \
        | tr -d '\r' \
        | sort -u
)
if (( ${#URLS[@]} == 0 )); then
    echo "No PDF links found in '${HTML_file}'." >&2
    popd > /dev/null
    exit 1
fi

# Download PDFs.
echo "Downloading PDFs..."
for URL in "${URLS[@]}"; do
    # Extract the event ID or fall back to "unknown".
    if [[ ${URL} =~ /event/([0-9]+)/ ]]; then
        event_ID="${BASH_REMATCH[1]}"
    else
        echo "Warning: could not parse event ID from URL ${URL}" >&2
        event_ID="unknown"
    fi
    # Ensure the per-event directory exists.
    directory="${prefix}${event_ID}"
    mkdir -p "${directory}"
    # Derive the filename from the URL.
    filename="${URL##*/}"
    echo "Downloading ${filename} to ${downloads_directory}/${directory}..."
    # Download.
    if ! wget \
        --load-cookies "../${cookies_file}" \
        --user-agent "${user_agent}" \
        --continue \
        --no-clobber \
        --directory-prefix="${directory}" \
        "${URL}"
    then
        echo "Warning: failed to download '${filename}'." >&2
    fi
done

# Regularise filenames, adding prefix if configured to do so.
if [[ "${regularise_filenames}" == true ]]; then
    echo "Adding prefix to filenames..."
    for directory in Indico_*; do
        if [[ -d "${directory}" ]]; then
            echo "Processing directory: ${directory}"
            # Rename each PDF of the directory.
            for filepath in "${directory}"/*.pdf; do
                # Skip if no PDFs are found.
                [[ -e "${filepath}" ]] || continue
                filename="${filepath##*/}"
                # If the PDF is already prefixed, skip it.
                if [[ "${filename}" == "${directory}"_* ]]; then
                    echo "  Skipping already prefixed file: ${filename}"
                    continue
                fi
                newname="${directory}_${filename}"
                echo "  Renaming ${filename} to ${newname}"
                mv -- "${filepath}" "${directory}/${newname}"
            done
        fi
    done
fi

# Return to original directory.
popd > /dev/null

echo "Downloading complete at directory '${downloads_directory}'."
