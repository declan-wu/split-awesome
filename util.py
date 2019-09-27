from PIL import Image, ImageFilter, ImageEnhance 
import boto3
import base64
from typing import List
import re

def base64_to_img(base64_str: str, file_path: str) -> None:
    """Convert base64 string into image and stores it in file_path"""
    with open(file_path, "wb") as fh:
        fh.write(base64.b64decode(base64_str))

def enhance_image(img_path: str, new_img_path: str) -> None:
    """Enhance image and stores it in new_img_path"""
    image = Image.open(img_path)
    enhancer_sharpness = ImageEnhance.Sharpness(image)
    enhancer_brightness = ImageEnhance.Brightness(image)
    enhancer_contrast = ImageEnhance.Contrast(image)
    enhancer_brightness.enhance(2).save(new_img_path)

def upload_to_s3(file_to_upload: str, bucket: str, s3_filename: str) -> None:
    """Upload an image to AWS S3 bucket as name: s3_filename"""
    client = boto3.client('s3', region_name='us-west-1')
    client.upload_file(file_to_upload, bucket, s3_filename)

def detect_text_from_img(bucket: str, s3_filename: str) -> List[str]:
    """Firing AWS Rekognition image text detection and return list of strings representing the lines"""
    #TODO: need to handle errors if the response is empty or confidence level is too low
    client = boto3.client('rekognition')
    response = client.detect_text(Image={'S3Object':{'Bucket':bucket,'Name':s3_filename}})
    textDetections=response['TextDetections']
    total_words_detected =  len(textDetections)

    ret = []
    for text in textDetections:
        if text['Type'] == 'LINE':
            ret.append(text['DetectedText'])
    return ret

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

def img_to_json(base64_str: str, img_path: str, new_img_path: str, bucket: str, s3_filename: str):
    """Convert a base64 string and extract useful information using AWS Rekognition"""
    base64_to_img(base64_str, img_path)
    upload_to_s3(img_path, bucket, s3_filename)
    # enhance_image(img_path, new_img_path)
    # upload_to_s3(new_img_path, bucket, s3_filename)
    #TODO: apply regex to process the response from AWS
    line_arr = detect_text_from_img(bucket, s3_filename)
    return parser(line_arr)

# for testing purpose
# if __name__ == '__main__':
#     print(img_to_json())
