"""
PNG to JPG Converter
--------------------

This script is designed to traverse a directory tree and convert all PNG images
it finds to JPG format.

The script uses OpenCV to read and write images. It uses os to traverse the
directory tree. The script starts from the directory in which it is placed and
scans for PNG files. Upon finding a PNG file, it reads the image using OpenCV,
then writes the image back in JPG format with 100% quality.

The script maintains the original directory structure and names of the images.
The original PNG files are not deleted or modified by this script.

Usage Instructions:
------------------
Place this script in the directory you want to convert images in. Run it from
the command line as follows:
    py png_to_jpg.py

License:
-------
MIT License

Copyright (c) 2023 @10XTMY, molmez.io

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""
import os
import cv2
from tqdm import tqdm

input_dir = os.getcwd()


def main() -> None:
    """Main function"""

    for dir_data in os.walk(input_dir):
        dir_path, folders, files = dir_data
        for image_file in tqdm(files):
            if image_file.lower().endswith('.png'):
                image = cv2.imread(f'{dir_path}\{image_file}')
                filename = f'{image_file.rsplit(".", 1)[0]}'
                cv2.imwrite(f'{dir_path}\{filename}.jpg', image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])


if __name__ == "__main__":
    main()
