# ReXodus
Download all of your media content from Reddit - regardless of posting source

## Supported sources
ReXodus currentl supports downloading from the following image/video hosts:
* Reddit images, galleries, and videos
* Imgur images, galleries, and videos
* Erome images, galleries, and videos
* Redgifs images and videos
* GfyCat videos and gifs
* Attempts to parse and download from other unknown sources

## How to install and use this repository
To install these files, copy the contents of this repository to the directory of your choice. If you have git and pip installed, you can run `pip install git+https://github.com/increasingardor/ReXodus.git`.

In either case, then run `pip install -r requirements.txt` to install the packages dependencies.

The config.py file has places for API credentials from Imgur, Reddit, GfyCat, and Redgifs, which can be obtained from their respective developer sites, and are needed to run this code.

Then run `python rexodus.py` (or `py rexodus.py` on Windows) to launch the GUI.

The GUI is very simple - enter your Reddit username (or the Reddit username of the user you are cataloging) on the left, then click the Browse button and choose a location to save the downloads to - ReXodus will create a directory for each hosting provider within that directory. You may uncheck any of the providers you do not want files from. Click Get Files, and watch the download counter in the lower right corner go up, and the filenames scroll by in the lower left.

ReXodus checks for the existence of a file before downloading, so if you have already downloaded it the file will be skipped; it looks for duplicate filenames from each individual provider, so you *can* have files named the same from Imgur and from Reddit, for instance, and both will be saved (as they are in separate directories).

## Disclaimer
ReXodus is not guaranteed to to continue to work, as these providers may change their APIs, directory structures, page structure, or hosts at any time. Use at your own risk and discretion.
