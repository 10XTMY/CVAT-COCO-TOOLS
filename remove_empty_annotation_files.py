"""
COCO Annotated Dataset Cleaner
------------------------------

This script is designed to clean a COCO 1.0 labeled dataset by removing all
images that do not have associated annotations. It reads the image and
annotation directories, identifies the unannotated images, and moves them
into a "_trash" directory for non-destructive cleaning. It also outputs a
new JSON annotation file that excludes the unannotated images.

The script uses argparse for command line argument parsing, allowing users
to specify the image directory and annotation file to be cleaned.

Usage Instructions:
-------------------
Run the script from the command line as follows:
    py remove_empty_annotation_files.py /path/to/images /path/to/annotations.json

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
import argparse
import json
import os
import shutil


def arg_parser() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Program to clean COCO dataset by removing unannotated images.')
    parser.add_argument('input_image_directory', type=str, help='Image directory to be cleaned')
    parser.add_argument('input_annotation_file', type=str, help='Path to the annotation file')
    return parser.parse_args()


def load_annotations(file_path: str) -> dict:
    """Load the COCO annotations from file"""
    with open(file_path, 'r') as f:
        return json.load(f)


def save_annotations(annotations: dict, file_path: str) -> None:
    """Save annotations to a file"""
    with open(file_path, 'w') as f:
        json.dump(annotations, f)


def main() -> None:
    """Main function"""
    args = arg_parser()

    image_dir = args.input_image_directory
    annotation_file = args.input_annotation_file

    # load the COCO annotations
    annotations = load_annotations(annotation_file)

    # create a dictionary of image id to file name
    image_dict = {image['id']: image['file_name'] for image in annotations['images']}

    # create a set of image ids that have annotations
    annotated_image_ids = {ann['image_id'] for ann in annotations['annotations']}

    # find the image ids that do not have annotations
    unannotated_image_ids = set(image_dict.keys()) - annotated_image_ids

    # filter out images that do not exist and update annotations
    existing_unannotated_image_files = []
    for image_id in unannotated_image_ids:
        file_name = image_dict[image_id]
        if os.path.exists(os.path.join(image_dir, file_name)):
            existing_unannotated_image_files.append(file_name)
        else:
            print(f"file {file_name} does not exist and will be removed from annotations.")
            annotations['images'] = [image for image in annotations['images'] if image['id'] != image_id]

    # save the new annotations
    save_annotations(annotations, os.path.join(os.path.dirname(annotation_file), 'new_annotations.json'))

    # move the existing unannotated image files to a _trash directory
    os.makedirs(os.path.join(image_dir, '_trash'), exist_ok=True)
    for file_name in existing_unannotated_image_files:
        shutil.move(os.path.join(image_dir, file_name), os.path.join(image_dir, '_trash', file_name))


if __name__ == "__main__":
    main()
