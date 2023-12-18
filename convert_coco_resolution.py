"""
This script allows the user to adjust the size of images and annotations in a COCO dataset.

The script accepts command-line arguments for input and output directories,
an annotation file in COCOv1 format, and a desired resolution for images.
If the output directory does not exist, it will be created.

Usage Instructions:
-------------------
Run the script from the command line as follows:
    py convert_coco_resolution.py path/to/images output/path path/to/annotation.json --resolution 800 800

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
import json
import argparse
from typing import Tuple, Union, List
from tqdm import tqdm


def resize_images(input_dir: str, output_dir: str, resolution: Union[Tuple[int, int], List[int]]) -> None:
    """
    Resize the images in the input directory and save them to the output directory.

    :param input_dir: path to image directory.
    :param output_dir: path to output directory.
    :param resolution: Tuple or list of two integers, denoting the desired image resolution (width, height).
    :return: None
    """

    # create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # walk through the directory tree
    for root, _, files in os.walk(input_dir):
        for file in tqdm(files, desc='Resizing Images'):

            # check if the file is a PNG or JPG image
            if file.lower().endswith(('.png', '.jpg')):
                try:
                    # read the image
                    image_path = os.path.join(root, file)
                    img = cv2.imread(image_path)

                    # resize the image
                    resized_img = cv2.resize(img, resolution)

                    # save the resized image to the output directory
                    output_path = os.path.join(output_dir, file)
                    cv2.imwrite(output_path, resized_img)

                except (cv2.error, IOError) as e:
                    print(f"error resizing image '{file}': {str(e)}")


def adjust_annotations(annotation_file: str, output_dir: str, resolution: Union[Tuple[int, int], List[int]]) -> str:
    """
    Adjust the bounding box coordinates in the COCO annotations.

    :param annotation_file: path to the original annotation file.
    :param resolution: Tuple or list of two integers, denoting the desired image resolution (width, height).
    :param output_dir: path to the output directory.
    :return: path to the adjusted annotation file.
    """

    output_file = os.path.splitext(os.path.basename(annotation_file))[0] + '_adjusted.json'
    output_path = os.path.join(output_dir, output_file)

    # create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # load the COCO annotations from the JSON file
    try:
        with open(annotation_file, 'r') as f:
            coco_data = json.load(f)

        # adjust the bounding box coordinates for each image
        for image in tqdm(coco_data['images'], desc='Adjusting Annotations'):
            image_id = image['id']
            width = image['width']
            height = image['height']

            # calculate the scaling factor for the x and y coordinates.
            # this is done by dividing the desired resolution by the original width and height.
            scale_x = resolution[0] / width
            scale_y = resolution[1] / height

            # adjust the bounding box coordinates
            for annotation in coco_data['annotations']:
                if annotation['image_id'] == image_id:
                    bbox = annotation['bbox']
                    # adjust the bounding box coordinates by multiplying them with the scaling factor.
                    bbox[0] *= scale_x  # x coordinate
                    bbox[1] *= scale_y  # y coordinate
                    bbox[2] *= scale_x  # width
                    bbox[3] *= scale_y  # height

            # update the image size in the COCO annotations
            image['width'] = resolution[0]
            image['height'] = resolution[1]

        # save the adjusted annotations to a new JSON file in the output directory
        output_file = os.path.splitext(os.path.basename(annotation_file))[0] + '_adjusted.json'
        output_path = os.path.join(output_dir, output_file)

        with open(output_path, 'w') as f:
            json.dump(coco_data, f)

    except (IOError, json.JSONDecodeError) as e:
        print(f"error adjusting annotations: {str(e)}")

    return output_path


def draw_bounding_boxes(image_dir: str, annotation_file: str) -> None:
    """
    Draw the bounding boxes on the first image.

    :param image_dir: path to the image directory.
    :param annotation_file: path to the annotation file.
    :return: None
    """

    try:
        # load the COCO annotations from the JSON file
        with open(annotation_file, 'r') as f:
            coco_data = json.load(f)

        # get the first image and its corresponding annotations
        image_id = coco_data['images'][0]['id']
        annotations = [ann for ann in coco_data['annotations'] if ann['image_id'] == image_id]

        # load the image
        image_name = coco_data['images'][0]['file_name']
        image_path = os.path.join(image_dir, image_name)

        try:
            img = cv2.imread(image_path)

            # draw the bounding boxes on the image
            for annotation in annotations:

                # bbox is a list of 4 values: x-coordinate, y-coordinate, width and height of the bounding box
                bbox = annotation['bbox']

                # use the map function to apply the int function to each item in the bbox list
                # this converts the values from float to int for cv2.rectangle
                x, y, width, height = map(int, bbox)

                # cv2.rectangle() parameters are as follows:
                # - img is the image on which to draw
                # - (x, y) is the top left corner of the rectangle
                # - (x + width, y + height) is the bottom right corner of the rectangle
                # - (0, 255, 0) is the color of the rectangle (in this case, green in BGR format)
                # - 2 is the thickness of the rectangle's border
                cv2.rectangle(img, (x, y), (x + width, y + height), (0, 255, 0), 2)

            # display the image with bounding boxes
            cv2.imshow('Bounding Boxes', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        except cv2.error as e:
            print(f"error displaying image with bounding boxes: {str(e)}")

    except (IOError, json.JSONDecodeError) as e:
        print(f"error loading COCO annotations: {str(e)}")


def main():
    """Main function"""

    # argument parser
    parser = argparse.ArgumentParser(description='Image and annotation resizing script')
    parser.add_argument('input_dir', type=str, help='Input directory containing images')
    parser.add_argument('output_dir', type=str, help='Output directory for resized images and adjusted annotations')
    parser.add_argument('annotation_file', type=str, help='Annotation file in COCOv1 format')
    parser.add_argument('--resolution', type=int, nargs=2, default=[512, 512],
                        help='Desired resolution for images (default: 512x512)')

    # parse the command-line arguments
    args = parser.parse_args()

    # check if the input directory exists
    if not os.path.exists(args.input_dir):
        print(f"error: Input directory '{args.input_dir}' does not exist")
        return

    # check if the output directory exists or create it
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    # check if the annotation file exists
    if not os.path.isfile(args.annotation_file):
        print(f"error: Annotation file '{args.annotation_file}' does not exist")
        return

    # create separate directories for images and annotations
    images_output_dir = os.path.join(args.output_dir, 'images')
    annotations_output_dir = os.path.join(args.output_dir, 'annotations')

    # perform image resizing
    resize_images(args.input_dir, images_output_dir, args.resolution)
    print('Image resizing completed successfully')

    # perform annotation adjustment
    annotation_output_file = adjust_annotations(args.annotation_file,
                                                annotations_output_dir,
                                                args.resolution)
    print('Annotation adjustment completed successfully')

    # test by drawing bounding boxes
    draw_bounding_boxes(images_output_dir, annotation_output_file)


if __name__ == '__main__':
    main()
