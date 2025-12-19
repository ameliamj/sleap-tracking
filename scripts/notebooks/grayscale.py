import cv2
import time
import os
import argparse


if __name__ == '__main__':
    # get the params
    start = time.time()
    
    parser = argparse.ArgumentParser("for the file names")
    parser.add_argument("--input-path", type=str, default="test_forgot_to_name", help="input path")
    parser.add_argument("--output-path", type=str, default="test_forgot_to_name", help="output path")
    args = parser.parse_args()

        
    start = time.time()
    # Input and output file paths
    # input_path = '/gpfs/radev/pi/saxena/aj764/Training_COOP_Fiber/060225_COOPTRAIN_LARGEARENA_KF024G-KF025Y_SessNum4/060225_COOPTRAIN_LARGEARENA_KF024G-KF025Y_SessNum4_Camera3.mp4'
    # output_path = '/gpfs/radev/pi/saxena/aj764/Training_COOP_Fiber/060225_COOPTRAIN_LARGEARENA_KF024G-KF025Y_SessNum4/060225_COOPTRAIN_LARGEARENA_KF024G-KF025Y_SessNum4_Camera3_gray.mp4'

    # Open the input video
    cap = cv2.VideoCapture(args.input_path)

    # Check if video opened successfully
    if not cap.isOpened():
        print("Error: Cannot open video file.")
        print(os.path.exists(args.input_path))
        print(os.path.exists('/gpfs/radev/pi/saxena/aj764/fiber_vids/'))
        exit()

    # Get video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec

    # Create VideoWriter object for the grayscale output
    out = cv2.VideoWriter(args.output_path, fourcc, fps, (frame_width, frame_height), isColor=False)

    print("Was able to load the video file at least")

    # Process each frame
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert to grayscale
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Write the frame to output
        out.write(gray_frame)

    # Release everything
    cap.release()
    out.release()
    print(f"Grayscale video saved to {args.output_path}")
    print(time.time() - start)