
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)

<br />
<p align="center">
  <h3 align="center">camloop</h3>

  <p align="center">
Forget the boilerplate from OpenCV camera loops and get to coding the interesting stuff
    <br />

</p>



<!-- TABLE OF CONTENTS -->
## Table of Contents
* [Usage](#usage)
 	* [Install](#install)
	* [Quickstart](#quickstart)
	* [More advanced use cases](#more-advanced-use-cases)
 	* [Configuring the loop](#configuring-the-loop)
 	* [Demo](#demo)
* [About the project](#about-the-project)
* [TODO](#todo)
* [License](#license)
* [Contact](#contact)

<!-- USAGE -->

<!-- USAGE -->
## Usage
This is a simple project developed to reduce complexity and time writing boilerplate code when prototyping computer vision applications. Stop worrying about opening/closing video caps, handling key presses, etc, and just focus on doing the cool stuff!

The project was developed in Python 3.8 and tested with physical local webcams. If you end up using it in any other context, please consider letting me know if it worked or not for whatever use case you had :)

### Install
The project is distributed by pypi, so just:
```bash
$ pip install pycamloop
```
As usual, conda or venv are recommended to manage your local environments.

### Quickstart
To run a webcam loop and process each frame, just define a function that takes as argument the frame as obtained from cv2.VideoCapture's `cap()` method (i.e: a np.array) and wrap it with the `@camloop` decorator.
You just need to make sure your function takes the frame as an argument, and returns it so the loop can show it:
```python
from camloop import camloop

@camloop()
def grayscale_example(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return frame

# calling the function will start the loop and show the results with the cv2.imshow method
grayscale_example()
```
The window can be exited at any time by pressing "q" on the keyboard. You can also take screenshots at any time by pressing the "s" key. By default they will be saved  in the current directory (see [configuring the loop](#configuring-the-loop) for information on how to customize this and other options).


### More advanced use cases
Now, let's say that instead of just converting the frame to grayscale and visualizing it, you want to pass some other arguments, perform more complex operations, and/or persist information every loop. All of this can be done inside the function wrapped by the `camloop` decorator, and external dependencies can be passed as arguments to your function.
For example, let's say we want to run a face detector and save the results to a file called `"face-detection-results.txt"`:

```python
from camloop import camloop

# for simplicity, we use cv2's own haar face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def face_detection_example(frame, face_cascade, results_fp=None):
    grayscale_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(grayscale_frame, 1.2, 5)
    for bbox in faces:
        x1, y1 = bbox[:2]
        x2 = x1 + bbox[2]
        y2 = y1 + bbox[3]
        cv2.rectangle(frame, (x1, y1), (x2, y2), (180, 0, 180), 5)

    if results_fp is not None:
	    with open(results_fp, 'a+') as f:
	        f.write(f"{datetime.datetime.now().isoformat()} - {len(faces)} face(s) found: {faces}\n")
    return frame

face_detection_example(face_cascade, results_fp="face-detection-results.txt")
```
 Camloop can handle any arguments and keyword arguments you define in your function, **as long as the frame is the first one**. In calling the wrapped function, pass the extra arguments with the exception of the frame which is handled implicitly.

### Configuring the loop
Since  most of the boilerplate is now hidden, `camloop` exposes a configuration object that allows the user to modify several aspects of it's behavior. The options are:

| parameter       | type   | default | description                                                                                                                                                           |
|-----------------|--------|---------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `source`          | int    | 0       | Index of the camera to use as source for the loop (passed to cv2.VideoCapture())                                                                                      |
| `mirror`          | bool   | False   | Whether to flip the frames horizontally                                                                                                                               |
| `resolution`          | tuple[int, int]   | None   | Desired resolution (H,W) of the frames. Passed to the cv2.VideoCapture.set method. Default values and acceptance of custom ones depend on the webcam.                                                                                                                   |
| `output`          | string | '.'     | Directory where to save artifacts by default (ex: captured screenshots)                                                                                               |
| `sequence_format` | string | None    | Format for rendering sequence of frames. Acceptable formats are "gif" or "mp4". If specified a video/gif will be saved to the output folder                           |
| `fps`             | float  | None    | FPS value used for the rendering of the sequence of frames. If unspecified, the program will try to estimate if from the length of the recording and number of frames |
| `exit_key`        | string | 'q'     | Keyboard key used to exit the loop                                                                                                                                    |
| `screenshot_key`  | string | 's'     | Keyboard key used to capture a screenshot                                                                                                                             |

If you want to use something other than the defaults, define a dictionary object with the desired configuration and pass it to the camloop decorator.

For example, here we want to mirror the frames horizontally, and save an MP4 video of the recording at 23.7 FPS to the `test` directory:

```python
from camloop import camloop

config = {
    'mirror': True,
    'output': "test/",
    'fps': 23.7,
    'sequence_format': "mp4",
}

@camloop(config)
def grayscale_example(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return frame

grayscale_example()
```

### Demo
Included in the repo is a demonstration script that can be run out-of-the-box to checkout camloop and it's main functions. There are a few different samples you can checkout, including the grayscale and face detection examples seen in this README).

To run the demo, install camloop and clone the repo:

```bash
$ pip install pycamloop
$ git clone https://github.com/glefundes/pycamloop.git
$ cd pycamloop/
```
Then run it by specifying which demo you want and passing any of the optional arguments (`python3 demo.py -h` for more info on them). In this case, we're mirroring the frames from the "face detection" demo and saving the a video of the recording in the "demo-videos" directory:

```bash
$ mkdir demo-videos
$ python3 demo.py face-detection --mirror --save-sequence mp4 -o demo-videos/
```

<!-- ABOUT THE PROJECT -->
## About The Project
I work as a computer vision engineer and often find myself having to prototype or debug projects locally using my own webcam as a source. This, of course, means I have to frequently code the same boilerplate OpenCV camera loop in multiple places.
Eventually I got tired of copy-pasting the same 20 lines from file to file and decided to write a 100-ish package to make my work a little more efficient, less boring and code overall less bloated. That's pretty much it. Also, it was a nice chance to practice playing with decorators.


<!-- ABOUT THE PROJECT -->
## TODO
- Verify functionality with other types of video sources (video files, streams, etc)

<!-- LICENSE -->
## License
Distributed under the MIT License. See `LICENSE` for more information.

<!-- CONTACT -->
## Contact

Gabriel Lefundes Vieira - lefundes.gabriel@gmail.com
