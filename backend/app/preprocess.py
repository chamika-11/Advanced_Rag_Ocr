import cv2
import numpy as np
from PIL import Image

def preprocess_image(image_path,mild_mode=True):
    image=cv2.imread(image_path)

    gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

    if gray.shape[1]<800:
        scale=1000/gray.shape[1]
        gray=cv2.resize(gray,None,fx=scale,fy=scale,interpolation=cv2.INTER_CUBIC)

    if mild_mode:
        denoised=cv2.fastNlMeansDenoising(gray,h=10)
        return denoised
    
    else:       
        denoised=cv2.fastNlMeansDenoising(gray, h=10)

        # _, thresh = cv2.threshold(denoised,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

        #deskew the image (process whereby skew is removed by rotating an image by the same amount as its skew but in the opposite direction)
        deskewed=deskew_image(denoised)

        thresh=cv2.adaptiveThreshold(
            deskewed,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,31,10
        )

        return thresh


def deskew_image(image):
    coords=np.column_stack(np.where(image>0))
    if coords.shape[0]==0:
        return image
    
    angle=cv2.minAreaRect(coords)[-1]

    if angle<-45:
        angle=-(90+angle)
    else:
        angle=-angle

    (h,w) =image.shape[:2]
    center=(w//2,h//2)
    M=cv2.getRotationMatrix2D(center,angle,1.0)
    rotated=cv2.warpAffine(image,M,(w,h),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)

    return rotated





