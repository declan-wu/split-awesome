from PIL import Image, ImageFilter, ImageEnhance 
import boto3
import base64
from typing import List

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

def img_to_text(base64_str: str, img_path: str, new_img_path: str, bucket: str, s3_filename: str):
    """Convert a base64 string and extract useful information using AWS Rekognition"""
    base64_to_img(base64_str, img_path)
    enhance_image(img_path, new_img_path)
    upload_to_s3(new_img_path, bucket, s3_filename)
    #TODO: apply regex to process the response from AWS
    return detect_text_from_img(bucket, s3_filename)

# for testing purpose
if __name__ == '__main__':
    with open("static/images/test.png", "rb") as image_file:
        base64_str = base64.b64encode(image_file.read())
    img_path = "./static/images/example.png"
    new_img_path = "./static/images/new_image.png"
    bucket = "split-wise-receipts-lhl"
    s3_filename = "new_image.png"
    res_arr = img_to_text(base64_str, img_path, new_img_path, bucket, s3_filename)
    food_items = {"result": res_arr}
    print (food_items)