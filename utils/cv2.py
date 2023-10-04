import cv2, numpy as np

"""CV2 Utils"""
def format_image(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2GRAY)
    #frame = cv2.GaussianBlur(frame, (3, 3), 0)
    return cv2.medianBlur(frame, 3)

def match_template(current_frame, template, dev_mode):
    template = format_image(template)
    print(template, current_frame)
    res = cv2.matchTemplate(current_frame, template, cv2.TM_CCOEFF_NORMED)
    threshold = .8
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):
        cv2.rectangle(current_frame, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
    if dev_mode:
        cv2.imshow('Result', current_frame)
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
