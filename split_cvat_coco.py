"""
Script for splitting a dataset into training and validation sets.
This script takes in the source annotation file, source image directory,
output directory, and split ratio as arguments. The output directory should
be the parent directory where the images and annotations directories will be created.

Usage Instructions:
-------------------
Run the script from the command line as follows:
    py split_cvat_coco.py path/to/images path/to/annotation.json output/path --split_ratio 0.8

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
import json
import random
import shutil
import argparse
from tqdm import tqdm
from typing import List, Dict, Set, Tuple


def arg_parser() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Program to split dataset for training and validation.")
    parser.add_argument('src_image_dir', help="Path to the source image directory")
    parser.add_argument('src_annotation_file', help="Path to the source annotation file")
    parser.add_argument('output_dir', help="Path to the output directory")
    parser.add_argument('--split_ratio', type=float, default=0.8,
                        help='The proportion of the dataset that should be used for training')
    return parser.parse_args()


def split_dataset(images: List[Dict], annotations: List[Dict],
                  train_ids: Set[int], val_ids: Set[int]) -> Tuple[List[Dict], List[Dict], List[Dict], List[Dict]]:
    """
    Splits the dataset into training and validation sets based on the provided image ids.

    :param images: list of dictionaries representing images
    :param annotations: list of dictionaries representing annotations
    :param train_ids: set of image ids to be used for the training set
    :param val_ids: set of image ids to be used for the validation set
    :return: a tuple of lists: training images, validation images, training annotations, and validation annotations
    """

    print('splitting images...')
    train_images = [img for img in tqdm(images) if img['id'] in train_ids]
    val_images = [img for img in tqdm(images) if img['id'] in val_ids]

    print('splitting annotations...')
    train_annotations = [ann for ann in tqdm(annotations) if ann['image_id'] in train_ids]
    val_annotations = [ann for ann in tqdm(annotations) if ann['image_id'] in val_ids]

    return train_images, val_images, train_annotations, val_annotations


def save_files_and_move_images(data: Dict, image_list: List[Dict], annotation_list: List[Dict], folder: str,
                               file_name: str, src_image_dir: str, output_dir: str) -> None:
    """
    Saves the annotations as json files and moves the images to the output directory.

    :param data: dictionary representing the source annotation file
    :param image_list: list of dictionaries representing images
    :param annotation_list: list of dictionaries representing annotations
    :param folder: folder name (train or val)
    :param file_name: output file name
    :param src_image_dir: path to the source image directory
    :param output_dir: path to the output directory
    """

    print('moving images...')
    for image in tqdm(image_list):
        shutil.move(os.path.join(src_image_dir, image['file_name']), os.path.join(output_dir, 'images', folder))

    print('saving annotations...')
    json_path = os.path.join(output_dir, 'annotations', file_name)
    with open(json_path, 'w') as json_file:
        json.dump({
            'licenses': data['licenses'],
            'info': data['info'],
            'categories': data['categories'],
            'images': image_list,
            'annotations': annotation_list
        }, json_file)


def validate_split(train_json_path: str, val_json_path: str, train_img_dir: str, val_img_dir: str) -> None:
    """
    Checks that the train and val json files are valid and all images referenced in them exist.

    :param train_json_path: path to the training annotation file
    :param val_json_path: path to the validation annotation file
    :param train_img_dir: path to the directory of training images
    :param val_img_dir: path to the directory of validation images
    """

    for json_path, img_dir, data_name in [(train_json_path, train_img_dir, 'train'),
                                          (val_json_path, val_img_dir, 'val')]:
        with open(json_path, "r") as f:
            data = json.load(f)

        # check JSON structure
        for key in ['licenses', 'info', 'categories', 'images', 'annotations']:
            if key not in data:
                print(f'{data_name}.json is missing key: {key}')

        # create set of image_ids in images and annotations
        image_ids = {image['id'] for image in data['images']}
        annotation_image_ids = {annotation['image_id'] for annotation in data['annotations']}

        # check if there are annotation image_ids that don't correspond to an image in the same file
        if not annotation_image_ids.issubset(image_ids):
            print(f'there are annotation image_ids in {data_name}.json that don\'t correspond to an image.')

        # check if all image files exist
        image_files = {image['file_name'] for image in data['images']}
        existing_files = {f for f in os.listdir(img_dir) if os.path.isfile(os.path.join(img_dir, f))}

        missing_files = image_files.difference(existing_files)
        if missing_files:
            print(f'the following files listed in {data_name}.json are missing in the {data_name} image directory:')
            for missing_file in missing_files:
                print(missing_file)

    print('Output files validation complete. Successfully split dataset.')


def main() -> None:
    """Main function"""

    args = arg_parser()

    # ensure output directories exist
    os.makedirs(os.path.join(args.output_dir, 'annotations'), exist_ok=True)
    os.makedirs(os.path.join(args.output_dir, 'images', 'train'), exist_ok=True)
    os.makedirs(os.path.join(args.output_dir, 'images', 'val'), exist_ok=True)

    # load the annotation file
    with open(args.src_annotation_file) as f:
        data = json.load(f)

    # separate images and annotations
    images = data['images']
    annotations = data['annotations']

    # separate a set of unique ids
    image_ids = list(set([img['id'] for img in images]))
    random.shuffle(image_ids)

    # split ids
    split_idx = int(args.split_ratio * len(image_ids))
    train_ids = set(image_ids[:split_idx])
    val_ids = set(image_ids[split_idx:])

    train_images, val_images, train_annotations, val_annotations = split_dataset(images, annotations, train_ids,
                                                                                 val_ids)

    # save as new json files and copy images
    for image_list, annotation_list, folder, file_name in [(train_images, train_annotations, 'train', 'train.json'),
                                                           (val_images, val_annotations, 'val', 'val.json')]:
        save_files_and_move_images(data, image_list, annotation_list, folder, file_name, args.src_image_dir,
                                   args.output_dir)

    validate_split(
        os.path.join(args.output_dir, 'annotations', 'train.json'),
        os.path.join(args.output_dir, 'annotations', 'val.json'),
        os.path.join(args.output_dir, 'images', 'train'),
        os.path.join(args.output_dir, 'images', 'val')
    )


if __name__ == "__main__":
    main()
