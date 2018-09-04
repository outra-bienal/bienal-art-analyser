import cv2
import random
import wcag_contrast_ratio as contrast
from dense_cap import DEEP_AI, DEEP_AI_2

from core.tag_image import *

captions = DEEP_AI['DenseCap']['output']['captions'][:15]
#captions = DEEP_AI_2['DenseCap']['output']['captions'][:15]

font_face = cv2.FONT_HERSHEY_SIMPLEX
scale = 0.5
thickness = 1
baseline = cv2.LINE_AA
BLACK = (0, 0, 0)
PADDING_TOP = 15
PADDING_BOTTOM = 10
PADDING_LEFT = 10
PADDING_RIGHT = 250


def draw():
    img = cv2.imread('/home/bernardo/Desktop/Bienal10_7.jpg')
    #img = cv2.imread('/home/bernardo/Desktop/Bienal10_2.jpg')
    for caption in captions:
        label = caption['caption']
        p1, p2 = get_caption_positions(img, caption)
        img = tag_element(img, p1, p2, label)
    cv2.imwrite('out.png', img)


if __name__ == '__main__':
    draw()
