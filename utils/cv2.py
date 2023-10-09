import cv2, numpy as np

"""CV2 Utils"""
def format_image(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2GRAY)
    height, width = frame.shape[:2]
    print(height, width)
    frame = cv2.GaussianBlur(frame, (3, 3), 0)
    #return cv2.medianBlur(frame, 3)
    return frame

def match_template(current_frame, template, dev_mode):
    template = format_image(template)
    w, h = template.shape[::-1]
    res = cv2.matchTemplate(current_frame, template, cv2.TM_CCOEFF_NORMED)

    # Specify a threshold
    threshold = 0.8

    # Store the coordinates of matched area in a numpy array
    loc = np.where(res >= threshold)

    # Draw a rectangle around the matched region.
    for pt in zip(*loc[::-1]):
        cv2.rectangle(current_frame, pt, (pt[0] + w, pt[1] + h), (0, 255, 255), 2)

    if dev_mode:
        cv2.imwrite('output/res.png', res)
        cv2.imwrite('output/Result.png', current_frame)
        cv2.imwrite('output/template.png', template)
    return current_frame

def motion_detection(diff):
    # Dilute the image a bit to make differences more visible; more suitable for contour detection
    kernel = np.ones((11, 11))
    diff_dilated = cv2.dilate(diff, kernel, 1)

    # Only take different areas that are different enough (>30 / 255)
    threshed_image = cv2.threshold(src=diff_dilated, thresh=30, maxval=255, type=cv2.THRESH_BINARY)[1]

    # Draw Countours from Motion Detection to Edges Image
    contours, _ = cv2.findContours(image=threshed_image, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)
    drawn_contours = cv2.drawContours(image=threshed_image, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)

    return drawn_contours
