import cv2
import numpy as np
import mss

start_point = None
end_point = None
drawing = False


def mouse_callback(event, x, y, flags, param):
    global start_point, end_point, drawing

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_point = (x, y)

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            end_point = (x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        end_point = (x, y)

        print("\nSelected region:")
        print(f"top: {min(start_point[1], end_point[1])}")
        print(f"left: {min(start_point[0], end_point[0])}")
        print(f"width: {abs(end_point[0] - start_point[0])}")
        print(f"height: {abs(end_point[1] - start_point[1])}")


with mss.mss() as sct:

    monitor = sct.monitors[1]
    screenshot = np.array(sct.grab(monitor))

    clone = screenshot.copy()

    cv2.namedWindow("select region")
    cv2.setMouseCallback("select region", mouse_callback)

    while True:

        img = clone.copy()

        if start_point and end_point:
            cv2.rectangle(img, start_point, end_point, (0, 255, 0), 2)

        cv2.imshow("select region", img)

        key = cv2.waitKey(1)

        if key == 27:  # ESC
            break

    cv2.destroyAllWindows()