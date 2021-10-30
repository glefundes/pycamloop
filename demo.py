import cv2
import logging
import datetime
import argparse

from camloop import camloop

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "demo",
        nargs="?",
        default="timestamp",
        type=str,
        help="function that will be used to process frames. Possible values are: [timestamp, grayscale, face-detection]",
    )
    parser.add_argument(
        "--source", default=0, help="source for the cv2.VideoCapture instance"
    )
    parser.add_argument("--mirror", action="store_true", help="flip frame horizontally")
    parser.add_argument(
        "-o",
        "--out",
        default=".",
        help="output directory for images/videos generated by the loop",
    )
    parser.add_argument(
        "--save-sequence",
        default=None,
        choices=["mp4", "gif"],
        help="format used to render and export a video of the loop",
    )
    parser.add_argument(
        "--fps",
        default=None,
        type=float,
        help="FPS used when rendering a video of the loop (only relevant when --save-sequence is specified)",
    )
    parser.add_argument(
        "-l", "--log-level", default=logging.INFO, help="log level verbosity"
    )
    args = parser.parse_args()

    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=args.log_level,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    config = {
        "source": args.source,
        "mirror": args.mirror,
        "output": args.out,
        "sequence_format": args.save_sequence,
        "fps": args.fps,
    }

    if args.demo == "timestamp":

        @camloop(config)
        def demo_timestamp(frame):
            frame = cv2.putText(
                frame,
                f"{datetime.datetime.now().isoformat()}",
                (0, frame.shape[0] - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                color=(255, 0, 0),
                thickness=2,
            )
            return frame

        demo_timestamp()

    elif args.demo == "grayscale":

        @camloop(config)
        def demo_grayscale(frame):
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return frame

        demo_grayscale()

    elif args.demo == "face-detection":

        @camloop(config)
        def demo_facedet(frame, face_cascade):
            grayscale_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(grayscale_frame, 1.2, 5)
            for bbox in faces:
                x1, y1 = bbox[:2]
                x2 = x1 + bbox[2]
                y2 = y1 + bbox[3]
                cv2.rectangle(frame, (x1, y1), (x2, y2), (180, 0, 180), 5)
            return frame

        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        demo_facedet(face_cascade)