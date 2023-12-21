"""
Image to MP4
--------------------------------------

This script takes a folder of JPG or PNG images and outputs a video file in MP4 format.

Usage Instructions:
-------------------
Run the script from the command line as follows:

    python image_to_mp4.py path/to/images output/path output_filename.mp4 --width 1920 --height 804 --fps 60

License:
--------
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
import sys
import argparse
import traceback
import numpy as np
import cv2
from tqdm import tqdm
from pathlib import Path


def parse_arguments():
    parser = argparse.ArgumentParser(description='Create a video from a sequence of images.')
    parser.add_argument('input_dir', type=str, help='Path to the directory containing the images.')
    parser.add_argument('output', type=str, help='Output directory.')
    parser.add_argument('filename', type=str, help='Output file name.')
    parser.add_argument('--width', type=int, default=512, help='Width of output video')
    parser.add_argument('--height', type=int, default=512, help='Height of the output video.')
    parser.add_argument('--fps', type=int, default=25, help='Frames per second')
    return parser.parse_args()


def main():
    args = parse_arguments()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)

    output_filename = args.filename if args.filename.endswith('.mp4') else f'{args.filename}.mp4'
    output_destination = os.path.join(output_dir.resolve(), output_filename)

    frame_per_second = args.fps
    w, h = args.width, args.height

    try:
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        writer = cv2.VideoWriter(output_destination, fourcc, frame_per_second, (w, h), True)
    except Exception as error:
        print(error)
        traceback.print_exc()
        sys.exit(1)
    else:
        frame_count = 0
        print('processing images...')
        for file in tqdm(os.listdir(input_dir)):
            if file.lower().endswith(('.png', '.jpg')):
                frame_path = input_dir / file
                frame = cv2.imread(str(frame_path))
                if frame is not None:
                    frame = cv2.resize(frame, (w, h))
                    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    try:
                        # writer.write(np.array(frame)[:, :, ::-1])
                        writer.write(frame)
                    except Exception as error:
                        print(error)
                        traceback.print_exc()
                        sys.exit(1)
                    else:
                        frame_count += 1
                else:
                    print(f'{file} is either corrupt or not an image. Skipping...')
        writer.release()
        print(f'job complete, frame count: {frame_count}')


if __name__ == '__main__':
    main()
