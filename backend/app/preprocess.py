import cv2
import numpy as np
from PIL import Image

def preprocess_image(image_path):
    image=cv2.imread(image_path)

    #convert to grayscale
    gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

    #remove noise
    denoised=cv2.fastNlMeansDenoising(gray, h=30)

    #thresholding
    _, thresh = cv2.threshold(denoised,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    #deskew the image (process whereby skew is removed by rotating an image by the same amount as its skew but in the opposite direction)
    deskewed=deskew_image(thresh)

    return deskewed


def deskew_image(image):
    coords=np.column_stack(np.where(image>0))
    angle=cv2.minAreaRect(coords)[-1]

    if angle<-45:
        angle= -(90+angle)
    else:
        angle= -angle

    (h,w) =image.shape[:2]
    center=(w//2,h//2)

    M=cv2.getRotationMatrix2D(center,angle,1.0)
    rotated=cv2.warpAffince(image,M,(w,h),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)

    return rotated





