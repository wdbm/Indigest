#!/usr/bin/env python3

'''
################################################################################
#                                                                              #
# indigest_extract_text                                                        #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program extracts text from PDF files.                                   #
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

usage:
    indigest_extract_text [options]

options:
    -h,--help               display help message
    --version               display version and exit
    --directory=DIRECTORY   directory of PDFs to process [default: downloads]
    --textfile=FILENAME     output text filename [default: text.txt]
'''

import docopt
import glob
import os
import sys

from PyPDF2 import PdfReader
from PyPDF2.errors import EmptyFileError

__version__ = "2025-07-21T2204Z"

def PDF_to_text(path_PDFs, path_text_files):
    '''
    Extract text from a PDF file at a specified path and write that text to a
    text file at a specified path.
    '''
    # Skip if the file does not exist or is zero‐length.
    if not os.path.isfile(path_PDFs):
        print(f"Warning: PDF not found, skipping: {path_PDFs}", file=sys.stderr)
        return
    if os.path.getsize(path_PDFs) == 0:
        print(f"Warning: PDF is empty, skipping: {path_PDFs}", file=sys.stderr)
        return

    # Try to open and parse the file.
    try:
        reader = PdfReader(path_PDFs)
    except EmptyFileError:
        print(f"Warning: Cannot read empty file, skipping: {path_PDFs}", file=sys.stderr)
        return
    except Exception as e:
        print(f"Warning: Error reading PDF {path_PDFs}: {e}", file=sys.stderr)
        return

    # Extract text and prepend the text with the filename.
    with open(path_text_files, "w", encoding="utf-8", errors="replace") as out:
        out.write(f"--- {path_PDFs} ---\n\n")
        for page in reader.pages:
            text = page.extract_text()
            if text:
                out.write(text)
                out.write("\n\n")
    print(f"Wrote: {path_text_files}")

def concatenate_texts(output_file="text.txt", header_style="plain"):
    '''
    Concatenate text files.
    '''
    pattern = os.path.join("downloads", "**", "*.txt")
    txt_files = sorted(glob.glob(pattern, recursive=True))
    if not txt_files:
        print("No text files to concatenate.")
        return

    # Concatenate the text of each file, including the respective filenames in
    # the resultant text.
    with open(output_file, "w", encoding="utf-8") as out:
        for txt in txt_files:
            rel = os.path.relpath(txt)
            if header_style == "markdown":
                out.write(f"# {rel}\n\n")
            else:
                out.write(f"=== {rel} ===\n\n")
            with open(txt, "r", encoding="utf-8", errors="replace") as inp:
                out.write(inp.read())
                out.write("\n\n")
    print(f"Wrote combined file: {output_file}")

def main():
    options = docopt.docopt(__doc__)
    if options['--version']:
        print(__version__)
        sys.exit(0)
    directory = options["--directory"]
    text_filename = options["--textfile"]

    if not os.path.isdir(directory):
        print(f"Error: directory '{directory}' not found.", file=sys.stderr)
        sys.exit(1)

    found_any = False
    for dirpath, _, filenames in os.walk(directory):
        for fname in filenames:
            if not fname.lower().endswith(".pdf"):
                continue
            found_any = True
            pdf_path = os.path.join(dirpath, fname)
            print(f"Processing file: {pdf_path}")
            base, _ = os.path.splitext(fname)
            txt_path = os.path.join(dirpath, f"{base}.txt")
            PDF_to_text(pdf_path, txt_path)

    if not found_any:
        print(f"No PDF files found under directory '{directory}'.")
        return

    concatenate_texts(output_file=text_filename, header_style="plain")

if __name__ == "__main__":
    main()
