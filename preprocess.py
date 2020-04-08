import os
import cv2
import random
import pathlib
from time import time
import cvlib as cv

# Paths needed for reading and storing data
current_dir = str(pathlib.Path(__file__).parent.absolute())
data_dir = '/data'
processed_dir = '/processed/'
datasets = {
    'real': '/original_sequences/actors/c40/videos/',
    'fake': '/manipulated_sequences/DeepFakeDetection/c40/videos/'
}


def create_processed_dirs():
    '''
    Creates the directory structures processed/fake and processed/real

    Returns:
        path to the folder where to processed frames will be stored
    '''
    processed_path = current_dir + processed_dir
    if not os.path.exists(processed_path):
        os.makedirs(processed_path)
    real_dir = processed_path + 'real'
    fake_dir = processed_path + 'fake'
    if not os.path.exists(real_dir):
        os.makedirs(real_dir)
    if not os.path.exists(fake_dir):
        os.makedirs(fake_dir)
    return processed_path


def preprocess_videos(dimensions=(150,150), sample=1, count=False, face_threshold=0.9, face_attempts=5):
    '''
    Runs through all the videos downloaded and stores the faces found in each video.

    Args:
        dimensions: What width and height the frame will be stored with
        sample: How many frames will be saved from each video
        count: How many videos will be processed from real and fake
        face_threshold: How strict the cvlib face recognition should be. Higher is stricter and yields clearer faces.
        face_attempts: How many frames will be tested for faces before giving up on a video

    Returns:
        None
    '''
    processed_path = create_processed_dirs()
    for label, label_path in datasets.items():  # Loop through labels (real, fake) with their corresponding dataset paths
        processed = 0
        path = current_dir + data_dir + label_path
        videos = os.listdir(path)
        avg_time = 0
        for c, video_name in enumerate(videos):
            start_time = time()
            video_path = path + video_name
            video = cv2.VideoCapture(video_path)
            image_path = processed_path + label + '/' + video_name.split('.')[0]

            # Saves faces from a random sampled subset of the video
            frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            frames = [i for i in range(frame_count)]
            random.shuffle(frames)  # Shuffles the frames in order to pick next frame randomly
            frames_saved = 0
            attempts = 0
            while frames_saved < sample and attempts < face_attempts:
                attempts +=1
                frame_index = frames[frames_saved]
                video.set(1,frame_index)
                name = f'{image_path}-{frames_saved+1}-'
                _, frame = video.read() 
                faces, confidences = cv.detect_face(frame, threshold=face_threshold)
                frames_saved += len(faces) > 0
                for j, (x0,y0,x1,y1) in enumerate(faces):
                    face = frame[y0:y1, x0:x1]
                    if len(face) > 0 and len(face[0] > 0):
                        face = cv2.resize(face, dimensions, interpolation = cv2.INTER_AREA)
                        filename = f'{name}face{j+1}.jpg'
                        cv2.imwrite(filename, face)
            video.release() 
            cv2.destroyAllWindows()

            #Print some data of the progress and time left
            time_spent = time()-start_time
            avg_time = (avg_time*(c)+time_spent)/(c+1)
            remaining = len(videos)-c
            print(f'{c+1}/{len(videos)} processed. {int(avg_time*remaining)}s left.', end='\r')
            processed += 1
            if processed >= count:
                break
            

    
preprocess_videos(count=400)