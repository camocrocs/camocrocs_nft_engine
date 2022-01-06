from PIL import Image, ImageOps
import random
import json
import pprint
from pathlib import Path
from math import floor
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from shutil import copyfile
import csv
from configparser import Config

config = Config()

pp = pprint.PrettyPrinter(indent=2)
NONE = "None"
TOTAL_IMAGES = config.total_images
DATA = 'data'

# Set seed to the last block on https://etherscan.io/blocks?p=2 so we get a predictable
# output each run until the seed is changed
random.seed(13424811)

def load_data(trait):
    names = []
    files = []
    rarities = []
    with open(f'{DATA}/{trait}.csv', newline='') as fd:
        reader = csv.reader(fd, skipinitialspace=True)
        for name,file,rarity in reader:
            names.append(name)
            files.append(file)
            rarities.append(float(rarity))
    namecounts = dict(zip(names, [0] * len(names)))
    name_to_file_map = dict(zip(names, files))
    return names,rarities,namecounts,name_to_file_map

def generate_images(traits):
    with ProcessPoolExecutor() as executor:
        executor.map(create_an_image, traits, chunksize=floor(TOTAL_IMAGES/4))
    #for t in traits:
    #    create_an_image(t)

def create_an_image(trait):
    # This is called once per trait
    im_bg = Image.open(f'{basepath}/{bg_path}/{bg_files[trait[TRAIT_BG]]}.png').convert('RGBA')
    im_face = Image.open(f'{basepath}/{face_path}/{face_files[trait[TRAIT_FACE]]}/{body_files[trait[TRAIT_BODY]]}.png').convert('RGBA')
    im_tooth = Image.open(f'{basepath}/{tooth_path}/{tooth_files[trait[TRAIT_TOOTH]]}.png').convert('RGBA')
    im_eyes = Image.open(f'{basepath}/{eye_path}/{eye_files[trait[TRAIT_EYE]]}.png').convert('RGBA')
    im_head = Image.open(f'{basepath}/{head_path}/{head_files[trait[TRAIT_HEAD]]}.png').convert('RGBA')
    im_mouth = Image.open(f'{basepath}/{mouth_path}/{mouth_files[trait[TRAIT_MOUTH]]}.png').convert('RGBA')
    im_nose = Image.open(f'{basepath}/{nose_path}/{nose_files[trait[TRAIT_NOSE]]}.png').convert('RGBA')
    im_body = Image.open(f'{basepath}/{body_path}/{body_files[trait[TRAIT_BODY]]}.png').convert('RGBA')
    im_cloth_inner = Image.open(f'{basepath}/{cloth_inner_path}/{cloth_inner_files[trait[TRAIT_CLOTH_INNER]]}.png').convert('RGBA')
    im_neck = Image.open(f'{basepath}/{neck_path}/{neck_files[trait[TRAIT_NECK]]}.png').convert('RGBA')
    im_cloth_outer = Image.open(f'{basepath}/{cloth_outer_path}/{cloth_outer_files[trait[TRAIT_CLOTH_OUTER]]}.png').convert('RGBA')
    im_hand = Image.open(f'{basepath}/{hand_path}/{hand_files[trait[TRAIT_HAND]]}.png').convert('RGBA')

    blending_order = [im_bg, im_body, im_cloth_inner, im_neck, im_cloth_outer, im_face,
                      im_tooth, im_eyes, im_head, im_nose, im_mouth, im_hand]

    # Create each composite
    composite = Image.alpha_composite(blending_order[0], blending_order[1])
    for img in blending_order[2:]:
        composite = Image.alpha_composite(composite, img)

    # Convert to RGB
    composite = composite.convert('RGB').resize((resize_res, resize_res), Image.LANCZOS)

    file_name = f'{str(trait[TOKENID])}{config.image_options.extn}'
    composite.save(f'{image_outputpath}/{file_name}', quality=jpg_quality)

    # Save thumbnail
    thumb = composite.convert('RGB').resize((thumbnail_res, thumbnail_res))
    thumb_file = f'{str(trait[TOKENID])}{config.thumbnail_options.extn}'
    thumb.save(f'{thumbnail_outputpath}/{thumb_file}', quality=jpg_quality)

    pp.pprint("{0} generated".format(trait[TOKENID]))

# Function to generate a unique set of traits to create a single image
# This checks the generated trait against global traits list and regenerates
# as many times required until unique
def create_combo():
    trait = {}
    #trait[TRAIT_BG] = random.choices(bg, bg_weights)[0]
    trait[TRAIT_FACE] = random.choices(face, face_weights)[0]
    #trait[TRAIT_TOOTH] = random.choices(tooth, tooth_weights)[0]
    trait[TRAIT_HEAD] = random.choices(head, head_weights)[0]
    trait[TRAIT_MOUTH] = random.choices(mouth, mouth_weights)[0]
    trait[TRAIT_EYE] = random.choices(eye, eye_weights)[0]
    trait[TRAIT_NOSE] = random.choices(nose, nose_weights)[0]
    trait[TRAIT_BODY] = random.choices(body, body_weights)[0]
    trait[TRAIT_CLOTH_OUTER] = random.choices(cloth_outer, cloth_outer_weights)[0]
    trait[TRAIT_CLOTH_INNER] = NONE if trait[TRAIT_CLOTH_OUTER] == 'Space Suit' else random.choices(cloth_inner, cloth_inner_weights)[0]
    trait[TRAIT_NECK] = random.choices(neck, neck_weights)[0]
    trait[TRAIT_HAND] = random.choices(hand, hand_weights)[0]
    trait[TRAIT_SIGNATURE] = NONE

    if trait in traits:
        return create_combo()
    else:
        return trait

# Function to double check if all traits are unique
def all_unique(x):
    seen = list()
    return not any(i in seen or seen.append(i) for i in x)

## List of all available attributes
# Backgrounds
bg_path = "bg"
bg, bg_weights, bg_count, bg_files = load_data(bg_path)

# Nose
nose_path = "nose"
nose, nose_weights, nose_count, nose_files = load_data(nose_path)

# Head
head_path = "head"
head, head_weights, head_count, head_files = load_data(head_path)

# Eyes
eye_path = "eyes"
eye, eye_weights, eye_count, eye_files = load_data(eye_path)

# Mouth
mouth_path = "mouth"
mouth, mouth_weights, mouth_count, mouth_files = load_data(mouth_path)

# Hand
hand_path = "hand"
hand, hand_weights, hand_count, hand_files = load_data(hand_path)

# Face expressions
face_path = "face"
face, face_weights, face_count, face_files = load_data(face_path)
# Unlike other traits, the face_files value points to a base folder
# So $(face_path)/normal/ is a folder, containing one image per body type
# $(face_path)/normal/normal.png = normal face with normal color
# $(face_path)/sad/jaguar.png = sad face with jaguar color

# Neck
neck_path = "neck"
neck, neck_weights, neck_count, neck_files = load_data(neck_path)

# Clothing
cloth_inner_path = "clothing_inner"
cloth_inner, cloth_inner_weights, cloth_inner_count, cloth_inner_files = load_data(cloth_inner_path)

# Outerwear
cloth_outer_path = "clothing_outer"
cloth_outer, cloth_outer_weights, cloth_outer_count, cloth_outer_files = load_data(cloth_outer_path)

# Body
body_path = "body"
body, body_weights, body_count, body_files = load_data(body_path)

# Choose body at random, then get matching traits like this:
# Base = $(body_path)/$(chosen_body).png
# Choose face at random, then get it with
# Face = $(face_path)/$(chosen_face)/$(chosen_body).png

# Teeth
tooth_path = "teeth"
tooth, tooth_weights, tooth_count, tooth_files = load_data(tooth_path)

## Generate traits
traits = []
TRAIT_BG = "Background"
TRAIT_NOSE = "Nose Accessory"
TRAIT_HEAD = "Head Gear"
TRAIT_EYE = "Eye Accessory"
TRAIT_MOUTH = "Mouth Accessory"
TRAIT_FACE = "Expression"
TRAIT_NECK = "Neck Accessory"
TRAIT_CLOTH_INNER = "Clothing"
TRAIT_CLOTH_OUTER = "Outerwear"
TRAIT_BODY = "Body Camo"
TRAIT_TOOTH = "Teeth"
TRAIT_HAND = "Hand"
TRAIT_SIGNATURE = "Signature"
TOKENID = "tokenId"

## Image generation
basepath = config.layers_path
outputpath = config.output_path
image_outputpath = f'{outputpath}/{config.image_options.path}'
thumbnail_outputpath = f'{outputpath}/{config.thumbnail_options.path}'

Path(image_outputpath).mkdir(parents=True, exist_ok=True)
Path(thumbnail_outputpath).mkdir(parents=True, exist_ok=True)
jpg_quality = config.image_options.jpg_quality
resize_res = config.image_options.width
thumbnail_res = config.thumbnail_options.width

def generate_traits():
    # Trigger the above function and generate a list of unique traits
    for i in range(TOTAL_IMAGES):
        traits.append(create_combo())

    # Trigger the above function and ensure everything is unique
    are_traits_unique = all_unique(traits)
    pp.pprint("Total Traits: {0}, Are Unique?: {1}".format(len(traits), are_traits_unique))

    # Add token id to traits - do this after the unique check because
    # everything will look unique otherwise due to the token id
    i = 0
    for item in traits:
        item[TOKENID] = i
        item[TRAIT_BG] = random.choices(bg, bg_weights)[0]
        item[TRAIT_TOOTH] = random.choices(tooth, tooth_weights)[0]
        i = i + 1

    # Get a grand total of each trait across all images
    for item in traits:
        bg_count[item[TRAIT_BG]] += 1
        face_count[item[TRAIT_FACE]] += 1
        tooth_count[item[TRAIT_TOOTH]] += 1
        hand_count[item[TRAIT_HAND]] += 1
        eye_count[item[TRAIT_EYE]] += 1
        mouth_count[item[TRAIT_MOUTH]] += 1
        nose_count[item[TRAIT_NOSE]] += 1
        head_count[item[TRAIT_HEAD]] += 1
        hand_count[item[TRAIT_HAND]] += 1
        neck_count[item[TRAIT_NECK]] += 1
        body_count[item[TRAIT_BODY]] += 1
        cloth_inner_count[item[TRAIT_CLOTH_INNER]] += 1
        cloth_outer_count[item[TRAIT_CLOTH_OUTER]] += 1

    ## Write stats to json
    with open(f'{outputpath}/stats.json', 'w') as outfile:
        json.dump(bg_count, outfile, indent=4)
        outfile.write('\n')
        json.dump(face_count, outfile, indent=4)
        outfile.write('\n')
        json.dump(tooth_count, outfile, indent=4)
        outfile.write('\n')
        json.dump(eye_count, outfile, indent=4)
        outfile.write('\n')
        json.dump(mouth_count, outfile, indent=4)
        outfile.write('\n')
        json.dump(nose_count, outfile, indent=4)
        outfile.write('\n')
        json.dump(head_count, outfile, indent=4)
        outfile.write('\n')
        json.dump(neck_count, outfile, indent=4)
        outfile.write('\n')
        json.dump(body_count, outfile, indent=4)
        outfile.write('\n')
        json.dump(cloth_inner_count, outfile, indent=4)
        outfile.write('\n')

    ## Write metadata to json
    with open(f'{outputpath}/full_metadata.json', 'w') as outfile:
        json.dump(traits, outfile, indent=4)

if __name__ == '__main__':
    generate_traits()
    generate_images(traits)
