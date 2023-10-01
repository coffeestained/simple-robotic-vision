
"""CV2 Utils"""
def match_template(current_frame, template):
    res = cv2.matchTemplate(current_frame, template, cv2.TM_CCOEFF_NORMED)
    threshold = .8
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):
        cv2.rectangle(current_frame, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
    return current_frame

def detect_motion(diff):
    # Dilute the image a bit to make differences more visible; more suitable for contour detection
    kernel = np.ones((11, 11))
    diff_dilated = cv.dilate(diff, kernel, 1)

    # Only take different areas that are different enough (>20 / 255)
    threshed_image = cv.threshold(src=diff_dilated, thresh=30, maxval=255, type=cv2.THRESH_BINARY)[1]

    # Draw Countours from Motion Detection to Edges Image
    contours, _ = cv2.findContours(image=threshed_image, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)
    drawn_contours = cv2.drawContours(image=threshed_image, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)

    return drawn_contours
