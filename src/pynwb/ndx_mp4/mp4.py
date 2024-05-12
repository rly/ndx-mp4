import tempfile
from warnings import warn
import numpy as np
from hdmf.utils import docval
from pynwb import get_class, register_class


BaseVideo = get_class("BaseVideo", "ndx-mp4")


@register_class("MP4H264Video", "ndx-mp4")
class MP4H264Video(BaseVideo):
    """
    With convenience functions for encoding/decoding MP4 H.264 (AVC) video data from numpy arrays.

    Exactly one of `data`, `data_array`, or `data_file` must be specified when creating an instance of this class.

    Adapted from the MP4AVCCodec class in Neurosift:
    https://github.com/flatironinstitute/neurosift/blob/2509fbdcdf105fcf102a9829adce92afb451fe04/python/neurosift/codecs/MP4AVCCodec.py
    """

    codec_id = "mp4avc"

    @docval(
        {
            "name": "name",
            "type": str,
            "doc": "The name of the video data object.",
        },
        {
            "name": "shape",
            "type": ("array_data", "data"),
            "doc": "The shape (dimensions) of the video, e.g., (frames, height, width, 3).",
        },
        {
            "name": "fps",
            "type": float,
            "doc": "The frames per second of the video.",
        },
        {
            "name": "data",
            "type": bytes,
            "doc": "The video data as a scalar dataset of bytes.",
            "default": None,
        },
        {
            "name": "data_array",
            "type": np.ndarray,
            "doc": "The video data as a numpy array with dtype uint8. Will be converted to bytes using `encode`.",
            "default": None,
        },
        {
            "name": "data_file",
            "type": str,
            "doc": "The file path to the video data file.",
            "default": None,
        }
    )
    def __init__(self, **kwargs):
        # Check that exactly one of 'data', 'data_array', or 'data_file' is specified
        data = kwargs.get("data")
        data_array = kwargs.pop("data_array")
        data_file = kwargs.pop("data_file")
        if sum([data is not None, data_array is not None, data_file is not None]) != 1:
            raise ValueError("Exactly one of 'data', 'data_array', or 'data_file' must be specified")

        if data_array is not None:
            data = self.encode(data_array, fps=kwargs["fps"])
        if data_file is not None:
            data = self.read_from_file(data_file)
        kwargs["data"] = data  # TODO store as np.void(data)

        super().__init__(**kwargs)

    @classmethod
    def read_from_file(cls, file_path: str) -> bytes:
        """
        Read the video data from an MP4 file and returns the byte stream.

        Parameters
        ----------
        file_path : str
            The file path to read the video data from.

        Returns
        -------
        bytes
            The video data as a byte stream.
        """
        if not file_path.endswith(".mp4"):
            raise ValueError(f"File path '{file_path}' must be a valid MP4 file with extension '.mp4'.")
        with open(file_path, 'rb') as f:
            return f.read()

    def write_to_file(self, file_path: str):
        """
        Write the video data to an MP4 file.

        Parameters
        ----------
        file_path : str
            The file path to write the video data to.
        """
        if not file_path.endswith(".mp4"):
            warn(f"File path '{file_path}' does not end with '.mp4'. This may cause issues with some video players.")
        with open(file_path, 'wb') as f:
            f.write(self.data)

    def encode(cls, array: np.ndarray, fps: float) -> bytes:
        """
        Encode a numpy array to MP4 H.264 (AVC) video data.

        This function writes the video data and fps to a temporary MP4 file using opencv and returns the file byte
        stream.

        Parameters
        ----------
        array : np.ndarray
            The numpy array to encode. Must be a uint8 array with shape (frames,
            height, width, 3) or (frames, height, width).
        fps : float
            The frames per second of the video.

        Returns
        -------
        bytes
            The encoded MP4 video data as a byte stream.
        """
        import cv2

        if array.dtype != np.uint8:
            raise ValueError("MP4H264VideoData only supports uint8 arrays")

        if array.ndim not in (3, 4):
            raise ValueError("MP4H264VideoData only supports 3D or 4D arrays")

        if array.ndim == 3:
            is_color = False
        else:
            is_color = True

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_output_fname = f'{tmpdir}/output.mp4'
            fourcc = cv2.VideoWriter_fourcc(*'avc1')  # type: ignore
            writer = cv2.VideoWriter(tmp_output_fname, fourcc, fps, (array.shape[2], array.shape[1]), isColor=is_color)
            for i in range(array.shape[0]):
                writer.write(array[i])
            writer.release()

            data = cls.read_from_file(tmp_output_fname)
            return data

    def decode(self, out=None) -> np.ndarray:
        """
        Decode MP4 AVC video data to a numpy array.

        Parameters
        ----------
        out: np.ndarray, optional
            Optional pre-allocated output array. Must be a uint8 array with shape
            (frames, height, width, 3) or (frames, height, width).

        Returns
        -------
        np.ndarray
            The decoded video data as a numpy array with dtype uint8 and shape (frames, height, width, 3) or
            (frames, height, width).
        """
        import cv2

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_input_fname = f'{tmpdir}/input.mp4'
            self.write_to_file(tmp_input_fname)

            cap = cv2.VideoCapture(tmp_input_fname)
            frames = []
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frames.append(frame)
            ret = np.array(frames, dtype=np.uint8)
            if out is not None:
                out[...] = ret
                return out
            return ret
