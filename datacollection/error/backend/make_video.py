import os
import threading

import cv2


def make_video(dir_path, component):
    video_name = "{}/{}.mp4".format(dir_path, component)
    image_dir_path = os.path.join(dir_path, component)
    images = [img for img in os.listdir(image_dir_path) if img.endswith(".jpg")]
    images = sorted(images, key=lambda x: int((x[:-4].split("_"))[-1]))
    frame = cv2.imread(os.path.join(image_dir_path, images[0]))
    height, width, layers = frame.shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(video_name, fourcc, 30, (width, height))
    for image in images:
        video.write(cv2.imread(os.path.join(image_dir_path, image)))
    video.release()


if __name__ == '__main__':
    dir_path = "{}/Coffee_PL1_P1_R1".format("/home/ptg/CODE/data")
    video_list = []
    video_list.append("pv")
    video_list.append("vlc_lf")
    video_list.append("vlc_ll")
    video_list.append("vlc_rr")
    video_list.append("vlc_rf")
    threads_ = []
    for vl in video_list:
        threads_.append(threading.Thread(target=make_video, args=(dir_path, vl,)))
    for t in threads_:
        t.start()
    for t in threads_:
        t.join()
