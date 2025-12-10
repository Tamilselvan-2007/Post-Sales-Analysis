import requests
import base64
from pathlib import Path

# Create a simple test image (1x1 white pixel)
test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'

# Convert to base64
image_base64 = base64.b64encode(test_image_data).decode('utf-8')
data_uri = f"data:image/png;base64,{image_base64}"

# Make request to detection endpoint
url = "http://localhost:5000/detect/missing"
payload = {"image_base64": data_uri}

print(f"Sending request to {url}...")
response = requests.post(url, json=payload)

print(f"Status Code: {response.status_code}")
print(f"Response Headers: {dict(response.headers)}")
print(f"Response Text: {response.text[:500]}...")
