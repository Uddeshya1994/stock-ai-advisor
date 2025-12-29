import cv2

vid = cv2.VideoCapture('input_video.mp4')
frame_no = 0

while True:
    ret, frame = vid.read()
    if not ret:
        break
    if frame_no % 10 == 0:  # extract every 10th frame
        cv2.imwrite(f'frames/frame_{frame_no}.jpg', frame)
    frame_no += 1

vid.release()
