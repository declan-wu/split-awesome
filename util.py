from PIL import Image, ImageFilter, ImageEnhance 
import boto3
import base64
from typing import List
import re

def enhance_image(img_path: str, new_img_path: str) -> None:
    """Enhance image and stores it in new_img_path"""
    image = Image.open(img_path)
    enhancer_sharpness = ImageEnhance.Sharpness(image)
    enhancer_brightness = ImageEnhance.Brightness(image)
    enhancer_contrast = ImageEnhance.Contrast(image)
    enhancer_brightness.enhance(2).save(new_img_path)

def single_float_regex(item):
    return bool(re.search('^\$?[0-9]*\.[0-9]{2}', item))

def quantity_first(item):
    return bool(re.search('^[1-9]*\s', item))

def full_match(item):
    return bool(re.search('.\$?[0-9]*\.[0-9]{2}', item)) and quantity_first(item)

def item_name_only(item, match):
    result = re.sub(match, '', item).strip()
    result = re.sub('\s\$', '', result)
    return result

def parser(test_arr):
    ret_arr = []
    line_item = {
        'quantity': '',
        'item': '',
        'price': ''
    }

    for idx, item in enumerate(test_arr):
        try:
            if full_match(item):
                price = re.search('[0-9]*\.[0-9]{2}', item).group()
                quantity = re.search('[1-9]*\s', item).group().strip()
                item = item_name_only(item, price)

                line_item['quantity'] = quantity 
                line_item['item'] = item
                line_item['price'] = price

                ret_arr.append(line_item)
                line_item = {
                    'quantity': '',
                    'item': '',
                    'price': ''
                }

            elif single_float_regex(item):
                price = re.search('[0-9]*\.[0-9]{2}', item).group()
                
                line_item['price'] = price

            elif quantity_first(item):
                quantity = re.search('[1-9]*\s', item).group().strip()
                item = re.sub(quantity, '', item)

                line_item['quantity'] = quantity
                line_item['item'] = item

            # check the total items in line_item
            if line_item['quantity'] != '' and line_item['price'] != '':
                ret_arr.append(line_item)
                line_item = {
                    'quantity': '',
                    'item': '',
                    'price': ''
                }
        except:
            pass
    return ret_arr

def detect_texts_local_file(base64_str):
    encoded_str = base64.b64decode(base64_str)
    client=boto3.client('rekognition', region_name='us-east-1')
    response = client.detect_text(Image={'Bytes': encoded_str})
    textDetections=response['TextDetections']
    total_words_detected =  len(textDetections)

    ret = []
    for text in textDetections:
        if text['Type'] == 'LINE':
            ret.append(text['DetectedText'])
    print(ret)
    return ret

def img_to_json(base64_str):
    """Convert a base64 string and extract useful information using AWS Rekognition"""
    line_arr = detect_texts_local_file(base64_str)
    return parser(line_arr)

if __name__ == '__main__':
    with open("./static/images/example.png", "rb") as image_file:
        base64_str = base64.b64encode(image_file.read())
    print(img_to_json(base64_str))
