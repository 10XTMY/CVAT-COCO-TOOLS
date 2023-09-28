"""
Image Sequence Player with Annotations
--------------------------------------

This script reads images from a specified directory and their corresponding
annotations from a specified COCO-format JSON file, draws the annotated bounding
boxes on the images, and displays them as a video using OpenCV. The user can
specify the input directory, the annotation file, the image format (either 'png'
or 'jpg'), and the frame rate from the command line.

Usage Instructions:
-------------------
Run the script from the command line as follows:
    $ python3 image_sequence_player.py --input_dir /path/to/images --annotations /path/to/annotations.json --format jpg --fps 24

License:
--------
MIT License

Copyright (c) 2023 10XTMY, molmez.io

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

import argparse
import cv2
import os
import json


def arg_parser() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Program to play a sequence of images as a video with annotations.")
    parser.add_argument('--input_dir', type=str, required=True, help="Path to the image directory")
    parser.add_argument('--annotations', type=str, required=True, help="Path to the COCO-format annotations file")
    parser.add_argument('--format', type=str, choices=['png', 'jpg'], required=True, help="Image format ('png' or 'jpg')")
    parser.add_argument('--fps', type=int, default=24, help="Frame rate (frames per second)")
    return parser.parse_args()


def draw_annotations(image, annotations):
    """Draw bounding boxes for a list of annotations on the image."""
    # Create a fresh copy of the image
    image_copy = image.copy()

    for ann in annotations:
        bbox = ann['bbox']
        x, y, width, height = [int(val) for val in bbox]
        top_left = (x, y)
        bottom_right = (x + width, y + height)
        image_copy = cv2.rectangle(image_copy, top_left, bottom_right, (255, 0, 0), 2)

    return image_copy


def play_image_sequence(input_dir: str, annotation_file: str, image_format: str, fps: int) -> None:
    """Play a sequence of images as a video with annotations."""
    image_files = [f for f in sorted(os.listdir(input_dir)) if f.lower().endswith(f'.{image_format}')]

    if not image_files:
        raise ValueError(f"No images found in {input_dir} with format .{image_format}")

    with open(annotation_file) as f:
        annotations_data = json.load(f)

    # create a dictionary mapping from image id to image file name
    image_id_to_name = {image['id']: image['file_name'] for image in annotations_data['images']}

    # create a dictionary mapping from image file name to annotations
    annotations_dict = {}
    for ann in annotations_data['annotations']:
        image_id = ann['image_id']
        image_name = image_id_to_name[image_id]
        if image_name not in annotations_dict:
            annotations_dict[image_name] = []
        annotations_dict[image_name].append(ann)

    for image_file in image_files:
        image_path = os.path.join(input_dir, image_file)
        image = cv2.imread(image_path)

        # if there are annotations for this image, draw them
        if image_file in annotations_dict:
            image = draw_annotations(image, annotations_dict[image_file])

        cv2.imshow('Image Sequence', image)
        if cv2.waitKey(int(1000/fps)) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    args = arg_parser()
    play_image_sequence(args.input_dir, args.annotations, args.format, args.fps)
