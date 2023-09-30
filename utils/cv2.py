
"""CV2 Utils"""
def match_template(source, template):
    res = cv2.matchTemplate(source, template, cv2.TM_CCOEFF_NORMED)
    threshold = .8
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):
        cv2.rectangle(source, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
    return source
