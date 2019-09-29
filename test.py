import requests 
import base64
# defining the api-endpoint  
API_ENDPOINT = "http://127.0.0.1:5000/snap"

# your source code here 
with open("./static/images/junior.png", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read())

# data to be sent to api 
data = {'image_data': encoded_string} 

# sending post request and saving response as response object 
r = requests.post(url = API_ENDPOINT, data = data) 

# extracting response text  
print("--------------------------------")
print(r.text ) 
print("--------------------------------")
