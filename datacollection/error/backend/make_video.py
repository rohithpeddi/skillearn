import os

import cv2


def make_video():
    images_folder = "~/Projects/PyCharm/skillearn/data/Coffee_P5_K1_R1/pv"
    video_name = "../../../data/video_flow.mp4"
    images = [img for img in os.listdir(images_folder) if img.endswith(".jpg")]
    images = sorted(images, key=lambda x: x[:-4])
    # images = [img for img in os.listdir(images_folder) if img.endswith(".jpg")]
    # images = sorted(images, key=lambda x: int(x[6:-4]))
    # images = [img for img in os.listdir(images_folder) if img.endswith(".png")]
    # images = sorted(images, key=lambda x: int(x[:-4]))
    frame = cv2.imread(os.path.join(images_folder, images[0]))
    height, width, layers = frame.shape
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    video = cv2.VideoWriter(video_name, fourcc, 30, (width, height))
    for image in images:
        video.write(cv2.imread(os.path.join(images_folder, image)))
    cv2.destroyAllWindows()
    video.release()


if __name__ == '__main__':
    make_video()
