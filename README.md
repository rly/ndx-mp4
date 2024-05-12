# ndx-mp4 Extension for NWB

NWB extension to store MP4 video data as bytes.

🚨 This extension does not work yet. Do not use.

## Overview

The NWB format stores video data as `ImageSeries` objects which can contain pixel values or one or more relative paths
to external video files. Storing video data is pixel values is inefficient compared to using a proprietary video codec
such as H.264. Storing video data as relative paths to external files requires maintaining the video files at those
exact relative paths, which makes managing and sharing these data more tedious. The `ndx-mp4` extension provides a way
to store video data as bytes in the MP4 file format compressed with the H.264 codec. This allows the video data to be
stored efficiently and directly in the NWB file, making it easier to manage and share the data. However, the use of the
H.264 codec may require licensing and the data may not be decodable or playable on all systems.

**Currently, only the H.264 codec is supported.** Future versions of this extension may support additional codecs.

This extension is experimental and may be subject to breaking changes in the future. We welcome feedback and
contributions to improve this extension in the [GitHub repository](https://github.com/rly/ndx-mp4).

## Motivation

The `ImageSeries` type can contain video data as a 3D (frame, width, height) or 4D array
(frame, width, height, channel) of pixel values. This data can be compressed using algorithms available to
the HDF5 or Zarr storage backends, such as gzip or blosc. However, storing video data as raw pixel values can be
inefficient, especially for long videos or videos with high resolution. Proprietary video codecs, such as H.264, can
compress video data more efficiently than generic compression algorithms, and may be more suitable for storing video
data in NWB files.

Alternatively, the `ImageSeries` type can contain one or more relative paths to external video files.
This allows the NWB file to reference
  video data stored in a separate file, but requires that the video file be accessible when the NWB file is read.

The MP4 (MPEG-4 Part 14) file format is a "container" format that most commonly stores video and audio data.
It uses the filename extension `.mp4`. The video and audio in the file may be encoded with various codecs.
Different operating systems and video players may have different codecs installed, so data stored in the MP4 format
may not be decodable or playable on all systems. Most modern browsers support the H.264 codec, also referred to as AVC
(Advanced Video Coding) or AVC1.

Storing video data as bytes in an NWB file allows the data to be packaged into a single file with other data types.
However,

Please note that the use of the MP4 format may require the use of proprietary codecs, which may have licensing restrictions.
For example, the H.264 codec is patented and requires a license to use. The use of the MP4 format and the codecs it may contain
should be considered carefully to ensure that the data can be accessed and used as intended.


## Installation

To encode or decode MP4 video data compressed with the H.264 codec, you will need to install
the `opencv-python` package. You can install these dependencies
using the following commands:

```bash
pip install opencv-python
```

TODO: h264 codec may not be installed in all systems. I think Windows and Mac are okay, but Linux may not be and may
require installation of opencv from conda-forge.


## Usage

Note that the output array of a color video will be in the shape (frame, height, width, channel) where the channel
is in the order BGR.

```python
from pynwb import NWBHDF5IO, NWBFile
from ndx_mp4 import MP4H264Video
import datetime
import numpy as np
import requests

# Create an NWB file
nwbfile = NWBFile(
    session_description="session_description",
    identifier="identifier",
    session_start_time=datetime.datetime.now(datetime.timezone.utc),
)

# Video URL
video_url = (
    "https://test-videos.co.uk/vids/sintel/mp4/h264/1080/Sintel_1080_10s_1MB.mp4"
)

# Download the video
response = requests.get(video_url)
response.raise_for_status()  # Ensure the download was successful
video_data = response.content
size_original_video = len(video_data)
print(f'Size of original video (MB): {size_original_video / 1024**2}')

# Option 1: Start with the video data as bytes
# Create a MP4H264Video object with the video data as bytes
data_obj_from_bytes = MP4H264Video(name="my_video_from_bytes", shape=(240, 1080, 1920, 3), fps=24.0, data=video_data)

# Decode the video data to a numpy array
video_array = data_obj_from_bytes.decode()
size_decoded_video = video_array.nbytes
print(f'Size of decoded video (MB): {size_decoded_video / 1024**2}')
print(f'Shape of decoded video array: {video_array.shape}')

# Option 2: Start with the video data as a numpy array
# Create a MP4H264Video object with the video data as a numpy array
# Note that the video data should be in the shape (frame, height, width, channel)
# And note that if the video data started as a video file decoded to bytes, the re-encoded video may not be identical
data_obj_from_array = MP4H264Video(name="my_video_from_array", shape=(240, 1080, 1920, 3), fps=24.0, data_array=video_array)

# But decoding the video data to a numpy array will be identical
video_array_roundtrip = data_obj_from_bytes.decode()
assert np.array_equal(video_array, video_array_roundtrip)

# Write the video data to a file
video_path = "my_video.mp4"
data_obj_from_bytes.write_to_file(video_path)

# Option 3: Start with the video data as a file
# Create a MP4H264Video object with the video data as a file
data_obj_from_file = MP4H264Video(name="my_video_from_file", shape=(240, 1080, 1920, 3), fps=24.0, data_file=video_path)
assert data_obj_from_file.data[:] == video_data

# Add the video data to the NWB file
nwbfile.add_acquisition(data_obj_from_bytes)
nwbfile.add_acquisition(data_obj_from_array)
nwbfile.add_acquisition(data_obj_from_file)

# Play the video frame by frame from the numpy array
# NOTE: opencv is not designed for video playback and this loop will not play the video in real time even if
# we set the frame delay to the video fps
import cv2
for frame in video_array:
    cv2.imshow('my_video', frame)
    if cv2.waitKey(int(1000 / 24.0)) == ord('q'):
        break

# Close the video window
cv2.destroyAllWindows()
cv2.waitKey(1)

# TODO this does not work yet: see https://github.com/hdmf-dev/hdmf-schema-language/issues/34
# Write the NWB file
with NWBHDF5IO("example_mp4.nwb", "w") as io:
    io.write(nwbfile)

# Read the NWB file
with NWBHDF5IO("example_mp4.nwb", "r") as io:
    nwbfile = io.read()
    read_data_obj_from_bytes = nwbfile.acquisition["my_video_from_bytes"]
    read_data_obj_from_array = nwbfile.acquisition["my_video_from_array"]
    read_data_obj_from_file = nwbfile.acquisition["my_video_from_file"]

    assert read_data_obj_from_bytes.data[:] == video_data
    assert read_data_obj_from_array.data[:] == video_data
    assert read_data_obj_from_file.data[:] == video_data

    # Decode the video data to a numpy array
    read_video_array = read_data_obj_from_bytes.decode()

    # Write the video data to a file
    read_data_obj_from_bytes.write_to_file("my_video2.mp4")

    # Play the video frame by frame from the numpy array
    for frame in read_video_array:
        cv2.imshow('my_video', frame)
        if cv2.waitKey(int(1000 / 24.0)) == ord('q'):
            break

    # Close the video window
    cv2.destroyAllWindows()
    cv2.waitKey(1)
```

---
This extension was created using [ndx-template](https://github.com/nwb-extensions/ndx-template).
