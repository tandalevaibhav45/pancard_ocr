import requests
import cv2 as cv
import numpy as np
import io
import fitz
from .log_file import logger3
from.Pan_erro_handle import ServerError

def read_image_from_server(image_url):
        '''This function reads an image from a server and returns it in the form of a Numpy array'''
        extension=image_url.rsplit('.')[-1]
        response = requests.get(image_url)
        try:
            if extension == 'pdf':
                    # Make an HTTP GET request to fetch the image data from the server
                    response = requests.get(image_url)
                    # Check if the request was successful
                    extension=image_url.rsplit('.')[-1]
                    if extension == 'pdf':
                        image_bytes = io.BytesIO(response.content)
                        pdf_document = fitz.open("pdf", image_bytes)
                        page = pdf_document[0]
                        images = page.get_images(full=True)
                        image_index = images[0][0]
                        image_bytes = pdf_document.extract_image(image_index)["image"]
                        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
                        image = cv.imdecode(image_array, cv.IMREAD_COLOR)
                        return image
            elif extension in ['jpg','png','PNG','JPG','jpeg']:
                if response.status_code == 200:
                    # Convert the binary image data to a NumPy array
                    image_array = np.frombuffer(response.content, dtype=np.uint8)
                    # Decode the NumPy array to an OpenCV image
                    image = cv.imdecode(image_array, cv.IMREAD_COLOR)
                    return image
            else:
                print("Please check the extension of the image.")
                return None
        except Exception as e:
            logger3.error(f'{e} on line {e.__traceback__.tb_lineno}')
            raise ServerError("")