import cv2
import random
import wcag_contrast_ratio as contrast

font_face = cv2.FONT_HERSHEY_SIMPLEX
scale = 0.5
thickness = 1
baseline = cv2.LINE_AA
BLACK = (0, 0, 0)
PADDING_TOP = 15
PADDING_BOTTOM = 10
PADDING_LEFT = 10
PADDING_RIGHT = 250


def get_caption_positions(caption):
    box = caption['bounding_box']
    top = int(box[0]) + PADDING_TOP
    left = int(box[1]) + PADDING_LEFT
    right = int(left + box[2])
    bottom = int(top + box[3])
    return (top, left), (bottom, right)


def get_valid_color(min_contrast_ratio=4.5, text_color=BLACK):
    """
    Only picks color with a contrast ratio higher than 4.5 by default

    More info here: https://www.w3.org/TR/WCAG20-TECHS/G18.html
    """
    contrast_ration = 0
    while contrast_ration < min_contrast_ratio:
        color_range = range(255)
        color = (
            random.choice(color_range),
            random.choice(color_range),
            random.choice(color_range),
        )
        contrast_ration = contrast.rgb_as_int(text_color, color)
    return color


def tag_element(img, p1, p2, tag):
    """
    p1 = (x1, y1)
    p2 = (x2, y2) from the rectangle

    More here: https://stackoverflow.com/questions/23720875/how-to-draw-a-rectangle-around-a-region-of-interest-in-python
    """
    text_p = (p1[0], p1[1] - 5)

    size = cv2.getTextSize(tag, font_face, scale, thickness)
    label_background_start = (text_p[0], text_p[1] - 15)
    label_background_pos = (
        label_background_start[0] + size[0][0],
        label_background_start[1] + size[0][1] + 8,
    )

    color = get_valid_color()
    cv2.rectangle(img, label_background_start, label_background_pos, color, -1)
    cv2.putText(img, tag, text_p, font_face, scale, BLACK, thickness, baseline)
    cv2.rectangle(img, p1, p2, color, 2)

    return img


def prepare_image(img):
    return cv2.copyMakeBorder(
        img,
        PADDING_TOP,
        PADDING_BOTTOM,
        PADDING_LEFT,
        PADDING_RIGHT,
        cv2.BORDER_CONSTANT,
        value=BLACK
    )
