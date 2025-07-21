# Indigest

Indigest downloads a collection of PDF files from a source like Indico and creates a text digest of them. The source could be Indico PDF slide presentations downloaded from a subset of Indico meetings and the output could be a text digest which can be quickly searched or included in the knowledgebase of a language model.

The script `indigest_download.sh` parses a HTML file which contains URL links to PDF files. This HTML file could be the output from [Indicomb](https://gitlab.cern.ch/indicomb/indicomb), for example. The script then attempts to download the files to respective subdirectories. It can be restarted if interrupted. It accepts a [`cookies.txt`](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt) file. Care must be taken to ensure that good security practices are used when using the [CERN SSO](https://home.cern/news/news/computing/computer-security-new-single-sign). The script then regularises the filenames, prepending them with an optional prefix.

The script `indigest_extract_text.py` uses `PyPDF2` (`pip3 install PyPDF2`) to extract text from the PDFs to respective text files at respective subdirectories before concatenating the files into a single text file.
