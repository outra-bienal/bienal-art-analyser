import cv2
import random
import wcag_contrast_ratio as contrast

font_face = cv2.FONT_HERSHEY_SIMPLEX
scale = 0.45
thickness = 1
baseline = cv2.LINE_AA
BLACK = (0, 0, 0)
PADDING_TOP = 1
PADDING_BOTTOM = 1
PADDING_LEFT = 1
PADDING_RIGHT = 50


def get_caption_positions(img, caption):
    """
    Deep AI scales image limiting a max of 800 for height or width
    Here we're reversing this scale so we can draw the boxes in the image
    """
    height, width, channels = img.shape
    scale = 1 / (float(800) / max(height, width))
    box = caption['bounding_box']
    top = int(box[0] * scale)
    left = int(box[1] * scale)
    right = int(left + box[3] * scale)
    bottom = int(top + box[2] * scale)
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
    text_p = (p1[0], p1[1] + 12)

    size = cv2.getTextSize(tag, font_face, scale, thickness)
    label_background_start = (text_p[0], text_p[1] - 12)
    label_background_pos = (
        label_background_start[0] + size[0][0],
        label_background_start[1] + size[0][1] + 8,
    )

    color = get_valid_color()
    cv2.rectangle(img, p1, p2, color, 2)
    cv2.rectangle(img, label_background_start, label_background_pos, color, -1)
    cv2.putText(img, tag, text_p, font_face, scale, BLACK, thickness, baseline)

    return img
