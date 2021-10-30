import os
import cv2
import time
import imageio
import logging
import datetime
import functools
import traceback

from pathlib import Path


class TimedFunction:
    def __init__(self, function, args, expires_at):
        self.expires_at = expires_at
        self.function = function
        self.args = args

    def __call__(self, frame):
        return self.function(frame, *self.args)

    def expired(self):
        return datetime.datetime.now() > self.expires_at


def paint_screenshot_message(frame, fp):
    return cv2.putText(
        frame,
        f"Screenshot saved at: {fp}",
        (16, 16),
        cv2.FONT_HERSHEY_PLAIN,
        0.9,
        color=(0, 120, 200),
        thickness=1,
    )


def export_sequence(sequence, fp, fmt, duration, fps=None):
    if fmt == "gif":
        sequence = [cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) for frame in sequence]
        if fps is not None:
            imageio.mimsave(fp, sequence, format="GIF", fps=fps)
        else:
            frame_duration = duration / len(sequence)
            imageio.mimsave(fp, sequence, format="GIF", duration=frame_duration)

    elif fmt == "mp4":
        if fps is None:
            fps = len(sequence) / duration
        height, width, _ = sequence[0].shape
        video = cv2.VideoWriter(
            fp, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height)
        )
        for frame in sequence:
            video.write(frame)
        video.release()


def validate_sequence_format(fmt):
    SUPPORTED_FORMATS = ["gif", "mp4"]
    if fmt is None:
        return None

    output_format = fmt.lower().lstrip(".")
    if output_format not in SUPPORTED_FORMATS:
        logging.warning(
            f"Specified format: '{output_format}' not supported. Currently supported formats are: {SUPPORTED_FORMATS}. Output sequence will not be saved"
        )
        return None

    return output_format


def validate_output_path(output_path):
    if output_path is None:
        return None

    output_path_abs = Path(output_path).resolve()
    if not output_path_abs.exists():
        logging.warning(
            f"Specified output directory not found ({str(output_path_abs)}). Files will not be saved"
        )
        return None

    return str(output_path_abs)


def camloop(config={}):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            logging.info("initializing camera...")
            source = config.get("source", 0)
            cap = cv2.VideoCapture(source)

            override_resolution = config.get("resolution", None)
            if override_resolution is not None:
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, override_resolution[0])
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, override_resolution[1])
            stime = time.time()

            output_path = validate_output_path(config.get("output", "."))
            sequence_export_format = validate_sequence_format(
                config.get("sequence_format", None)
            )

            sequence_frames = []
            preprocess_stages = []
            try:
                while True:
                    ret, frame = cap.read()
                    if ret:
                        # PREPROCESSING
                        if config.get("mirror", False):
                            frame = cv2.flip(frame, 1)

                        preprocess_stages = [
                            p for p in preprocess_stages if not p.expired()
                        ]
                        for stage in preprocess_stages:
                            frame = stage(frame)

                        # FUNCTION CALLING
                        if f is not None:
                            frame = f(frame, *args, **kwargs)
                            if output_path is not None:
                                sequence_frames.append(frame)

                        # POSTPROCESSING
                        cv2.imshow("frame", frame)

                        # KEY PARSING
                        pkey = cv2.waitKey(1)
                        # Capture screenshot
                        if (
                            pkey == ord(config.get("screenshot_key", "s"))
                            and output_path is not None
                        ):
                            fp = os.path.join(
                                output_path,
                                f"{datetime.datetime.now().isoformat()+'.jpg'}",
                            )
                            paint_ss_message_function = TimedFunction(
                                paint_screenshot_message,
                                [fp],
                                datetime.datetime.now() + datetime.timedelta(seconds=3),
                            )
                            preprocess_stages.append(paint_ss_message_function)
                            cv2.imwrite(fp, frame)

                        # End loop
                        elif pkey == ord(config.get("exit_key", "q")):
                            total_duration = time.time() - stime
                            cap.release()
                            cv2.destroyAllWindows()

                            if (
                                sequence_export_format is not None
                                and output_path is not None
                            ):
                                fp = os.path.join(
                                    output_path,
                                    f"{datetime.datetime.now().isoformat()+f'.{sequence_export_format}'}",
                                )
                                logging.info(f"exporting file: {fp}")
                                export_sequence(
                                    sequence_frames,
                                    fp,
                                    sequence_export_format,
                                    total_duration,
                                    fps=config.get("fps", None),
                                )
                                logging.info("done!")
                            break
                    else:
                        traceback.print_exc()
                        raise Exception(f"Could not reach source: {source}")
            except Exception:
                traceback.print_exc()
                cap.release()
                cv2.destroyAllWindows()

        return wrapper

    return decorator
