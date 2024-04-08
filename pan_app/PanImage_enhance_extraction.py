import cv2 as cv
import numpy as np
import pytesseract
from PIL import Image
from .log_file import logger3
from.Pan_erro_handle import InputImageEnhanceError,ExtractingImageError
from .pan_config import pytesseract

def inputimg_processing(source):
    '''This function  is used to process the image that user inputs'''
    try:
        inpt_im_height,inpt_im_width,_ = source.shape
        """This function is used to change the color space of an image. This parameter specifies the color conversion code"""
        gray_resized = cv.cvtColor(source, cv.COLOR_BGR2GRAY)
        '''If condition works when image is less than dimension(400x250) to get the resized image'''
        if inpt_im_width<500 and inpt_im_height<350:
            gray_resized = cv.resize(gray_resized, (inpt_im_width*2,inpt_im_height*2))
            return gray_resized
        elif inpt_im_width>1500 and inpt_im_height>1000:
            gray_resized = cv.resize(gray_resized, (inpt_im_width//2,inpt_im_height//2))
            return gray_resized
        else:
            blurred = cv.GaussianBlur(gray_resized, (3, 9), 1)
            """thresold used for image segmentation cv.THRESH_OTSU: This is the thresholding method. cv.THRESH_OTSU automatically calculates an optimal threshold value based on the image histogram using Otsu's method"""
            thresh1 = cv.adaptiveThreshold(blurred, 200, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY,25, 11)
            """kernel used for image filtering"""
            kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
            sharpened = cv.filter2D(thresh1, -2, kernel)
            kernel_dilation = np.ones((3, 3), np.uint8)
            """cv.dilate: This function performs dilation, which is another morphological operation used to expand the size of white regions in a binary image"""
            dilated = cv.dilate(sharpened, kernel_dilation, iterations=0)
            dilated = np.array(dilated)
            return dilated
    except Exception as e:
        logger3.error(f'{e} on line {e.__traceback__.tb_lineno}')
        raise InputImageEnhanceError("")
    
def croping_extraction(bg_added_arrey,original_im_height,original_im_width):
    '''This function is used to the extraction result of cropped images.'''
    try:   
        '''If condition works when image is less than dimension(400x250) to get the resized image'''
        if original_im_width<500 and original_im_height<350:
            '''Convert into BGR to RGB for pillow'''
            bg_added_arrey = Image.fromarray(cv.cvtColor(bg_added_arrey, cv.COLOR_BGR2RGB))  
            eroded_img = bg_added_arrey.resize((bg_added_arrey.width * 4, bg_added_arrey.height * 4))
        else:
            height, width = bg_added_arrey.shape
            bg_added_arrey = cv.resize(bg_added_arrey, (width*2,height*2))
            """This function is used to change the color space of an image. This parameter specifies the color conversion code"""
            blurred = cv.GaussianBlur(bg_added_arrey, (1, 3), 1)
            """thresold used for image segmentation cv.THRESH_OTSU: This is the thresholding method. cv.THRESH_OTSU automatically calculates an optimal threshold value based on the image histogram using Otsu's method"""
            thresh1 = cv.adaptiveThreshold(blurred, 200, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY,25, 11)
            kernel = np.ones((1,1), np.uint8)
            eroded_img = cv.erode(thresh1, kernel, iterations=1)
            """this function is used for extract the value"""
        extracted_text = pytesseract.image_to_string(eroded_img, config=" --psm 6")
        return extracted_text
    except Exception as e:
        logger3.error(f'{e} on line {e.__traceback__.tb_lineno}')
        raise ExtractingImageError("")