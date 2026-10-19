# LatestFrameCamera and RTSP reconnect logic

import threading
import time
import os

# tell OpenCV's FFmpeg backend to use TCP for RTSP streaming
# set this before importing OpenCV
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

import cv2

class LatestFrameCamera:
    """ Read camera frames in a background thread, keeping only the lastest one """
    def __init__(self, stream_url):
        self.stream_url = stream_url
        self.frame = None

        # prevent the camera thread and main thread from accessing
        # the shared frame at the same time
        self.lock = threading.Lock()

        # control whether the background capture loop should keep running
        self.running = True

        # start reading immediately 
        # a daemon thread does not keep the process alive by itself
        self.thread = threading.Thread(
            target=self._read_frames, 
            daemon=True
        )
        self.thread.start()

    def _read_frames(self):
        """ Connect to the camera and reconnect when the stream fails """

        while self.running:
            # open the RTSP stream using OpenCV's FFmpeg backend
            cap = cv2.VideoCapture(self.stream_url, cv2.CAP_FFMPEG)

            # request a small capture buffer to reduce delay
            # support for this setting depends on the backend
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            if not cap.isOpened():
                print("Could not connect — retrying in 2 seconds...")
                cap.release()
                time.sleep(2)
                continue

            print("RTSP connected using TCP.")

            while self.running:
                # ret indicates whether a frame was read successfully
                ret, frame = cap.read()

                if not ret:
                    print("Stream dropped — reconnecting...")
                    break

                # Replace any old frame with the newest camera frame.
                with self.lock:
                    self.frame = frame

            # release the connection before attempting to reconnect
            cap.release()
            time.sleep(2)

    def get_latest_frame(self):
        """ Return an independent copy of the latest available frame """

        with self.lock:
            # return None untill the camera has captured its first frame
            return None if self.frame is None else self.frame.copy()

    def stop(self):
        """ request capture shutdown and wait up to the three seconds. """
        self.running = False
        self.thread.join(timeout=3)