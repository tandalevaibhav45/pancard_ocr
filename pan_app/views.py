from ultralytics import YOLO
import json
import re
import fitz
import numpy as np
import requests
import cv2 as cv
import math
import base64
import io
import pdf2image
from .log_file import logger3
from django.http import  JsonResponse
from .pan_config import model_path
from rest_framework.decorators import api_view
from .PanImage_enhance_extraction import inputimg_processing,croping_extraction
from .PanImage_BusinessRule import name_correction,date_pattern,pan_no_correct
from .readImage_from_server import read_image_from_server
from.Pan_erro_handle import ServerError,YoloModelNotFoundError,PredictionFailed,InputImageEnhanceError,ExtractingImageError,CroppImageError,BusinessRuleError,PredictionFunError



# def read_image_from_page(file_url, page_number):
#     '''This function reads the image from a PDF file at the given URL and returns it in BASE64 format'''
#     response = requests.get(file_url)
#     if response.status_code == 200:
#         image_bytes = io.BytesIO(response.content)
#         pdf_document = fitz.open("pdf", image_bytes)
#         page = pdf_document[page_number]
#         images = page.get_images(full=True)
#         image_index = images[0][0]
#         image_bytes = pdf_document.extract_image(image_index)["image"]
#         image_array = np.frombuffer(image_bytes, dtype=np.uint8)
#         image = cv.imdecode(image_array, cv.IMREAD_COLOR)
#         return image, page_number
#     else:
#         print("Failed to fetch the PDF file.")

def read_image_from_page(file_url, page_number):
    response = requests.get(file_url)
    if response.status_code == 200:
        image_bytes= response.content
        images=pdf2image.convert_from_bytes(image_bytes,fmt='png')
        buffer = io.BytesIO()
        images[page_number].save(buffer, format="PNG")
        image_bytes = buffer.getvalue()
        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv.imdecode(image_array, cv.IMREAD_COLOR)
        return image, page_number
    else:
        print("Failed to fetch the PDF file.")

@api_view(["POST"])
def ext_data_from_pan(request):
    '''This function is used for extracting data from PAN card'''
    try:
        doc_type=request.data["doc_type"]
        if doc_type=="multiple doc ext":
            url_path=request.data["doc_url"]
            text_data =predict_model(model_path,url_path)
            text_data = json.loads(text_data.content.decode('utf-8'))
            return text_data
        elif doc_type=="rectification ext":
            page_number=request.data["page_no"]
            url_path=request.data["doc_url"]
            img_array=read_image_from_page(url_path, page_number)
            text_data = predict_model(model_path,img_array[0])
            return text_data
        else:
            url_path = request.data["doc_url"]
            img_narrey = read_image_from_server(url_path)
            text_data = predict_model(model_path,img_narrey)
            return text_data
  
    except ServerError:
        error_response = {"error": "Image could not be read from the server.", "status" :False}
    except YoloModelNotFoundError:
        error_response = {"error": "YOLO Pan card model not found.", "status" :False}
    except PredictionFailed:
        error_response = {"error": "YOLO prediction model failed over given image.", "status" :False}
    except InputImageEnhanceError:
        error_response = {"error": "Error occurred while enhancing input image.", "status" :False}
    except CroppImageError:
        error_response = {"error": "Error occurred while cropping image.", "status" :False}
    except ExtractingImageError:
        error_response = {"error": "Error occurred while extracting image.", "status" :False}
    except BusinessRuleError:
        error_response = {"error": "Error occurred applying business rule over [Name, Father's name, Pan number, Signature, DOB].", "status" :False}
    except PredictionFunError:
        error_response = {"error": "Error occured in predicion function.", "status" :False}
    except Exception as e:
        logger3.error(f'{e} on line {e.__traceback__.tb_lineno}')
        error_response = {"data": "Plese check URL->server might be down or Internal Server Error", "status": False}
    return JsonResponse(error_response)


"""
This function are used to crop the image using coordinate and using dataextraction functions extract the data
Input:Image,coordinate
Output:-Text data
"""
def crop_image_from_inputimg(source,value,label_name,original_img):
    '''This function is used to crop the image using label name'''
    try:
        original_im_height,original_im_width,_ = original_img.shape
        _,edited_im_width = source.shape
        '''If condition works when image is less than dimension(400x250) to get the resized image'''
        if original_im_width<500 and original_im_height<350 or original_im_width>1500 and original_im_height>1000:
            width_factor = original_im_width / edited_im_width
            width_factor = round(width_factor, 2)
            """for landscape"""
            left,top,width,height = int(int(float(value["x1"])) // width_factor),int(int(float(value["y1"]) // width_factor)),int(int(float(value["x2"])) // width_factor),int(int(float(value["y2"]) // width_factor))
        else:
            """Getting the cordinated x1,y1,x2,y2"""
            left,top,width,height = math.floor(value["x1"]),math.floor(value["y1"]),math.floor(value["x2"]),math.floor(value["y2"])
        """Crop the image using cordinates"""
        cropped_image_obj = source[top:height, left:width]
        if label_name == "Signature":
            image_bytes = cv.imencode('.png',cropped_image_obj)[1].tobytes()
            text_data = base64.b64encode(image_bytes).decode("utf-8")
        else:
            """Extraction of data"""
            text_data = croping_extraction(cropped_image_obj,original_im_height,original_im_width)
        coordinates_imgs = [left, top, width, height]
        return text_data, coordinates_imgs
    except Exception as e:
        logger3.error(f'{e} on line {e.__traceback__.tb_lineno}')
        raise CroppImageError("")


def load_yolo_model(model_name):
    '''This function loads the yolo model'''
    try:
        """using YOLO to get the model from lib"""
        model = YOLO(model_name)
        return model
    except Exception as e:
        logger3.error(f'{e} on line {e.__traceback__.tb_lineno}')
        raise YoloModelNotFoundError("")
    
def model_prediction(model,source):
    '''This code is used to predict the class name in the image'''
    try:
        """Prediction on input images"""
        results = model.predict(source , conf=0.10, iou=0.1, agnostic_nms=True)[0]
        data = json.loads(results.tojson())
        return data
    except Exception as e:
        logger3.error(f'{e} on line {e.__traceback__.tb_lineno}')
        raise PredictionFailed("")
    
def apply_buisness_rule(label_name,value,confidance_score1,source,original_img):
        '''This function is used to applying business rules to the extracted fields'''
        global predicted_data
        try:
            """Crop image data"""
            if confidance_score1>=0.8:
                    text_data, _ = crop_image_from_inputimg(source, value,label_name,original_img)
                    if label_name == 'DOB':
                        try:
                            label_name = "DOB"
                            text_data = date_pattern(text_data)
                            repeated_pattern = "\/|-|\."
                            pattern = r"\d{{1,2}}({0})\d{{1,2}}({0})\d{{1,4}}".format(repeated_pattern)
                            matc_data = re.match(pattern, text_data)
                            matc_data = matc_data.group()
                            text_data = matc_data.replace("\"","")
                        except Exception as e:
                            text_data = text_data

                    elif label_name in ["Name","Father Name"]:
                        if label_name == "Father Name":
                            label_name = "Father's name"
                        text_data = name_correction(text_data)
                    elif label_name in ["Pan Number"]:
                        label_name = "PAN Number"
                        text_data = pan_no_correct(text_data)
                    text_data = re.sub(r"[>\n]", " ", text_data).strip()

                    return text_data,label_name
        except BusinessRuleError as e:
            logger3.error(f'{e} on line {e.__traceback__.tb_lineno}')
        except Exception as e:
            logger3.error(f'{e} on line {e.__traceback__.tb_lineno}')
            
def predict_model(model_name, source):
    '''This function is used to predict the OCR output using trained models'''
    model  = load_yolo_model(model_name)
    data  = model_prediction(model,source)
    original_img = source
    source = inputimg_processing(source)
    """List for prdicted data extaction"""
    predicted_data = []
    for val in data:
        label_name,value,confidance_score1,confidance_score = val["name"],val["box"],val["confidence"],round((val["confidence"] * 100), 2)
        text_data,label_name = apply_buisness_rule(label_name,value,confidance_score1,source,original_img)
        if label_name != "Photo": predicted_data.append({"label": label_name, "extractedValue": text_data, "confidence_score": confidance_score})
    predicted_data=sorted(predicted_data, key=lambda x: x["label"])
    predicted_data = {'ext_data':predicted_data}
    predicted_data["status"]=True
    return JsonResponse(predicted_data)







