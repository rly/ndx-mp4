# -*- coding: utf-8 -*-
import os.path

from pynwb.spec import NWBNamespaceBuilder, export_spec, NWBGroupSpec, NWBAttributeSpec, NWBDatasetSpec


def main():
    ns_builder = NWBNamespaceBuilder(
        name="""ndx-mp4""",
        version="""0.1.0""",
        doc="""NWB extension to store MP4 video data as bytes""",
        author=[
            "Ryan Ly",
        ],
        contact=[
            "rly@lbl.gov",
        ],
    )
    ns_builder.include_namespace("core")

    base_video_data = NWBGroupSpec(
        neurodata_type_def="BaseVideo",
        neurodata_type_inc="NWBDataInterface",
        doc=("An abstract base type for storing video data as bytes. Video can be grayscale or color (RGB)."),
        datasets=[
            NWBDatasetSpec(
                name="data",
                doc="The video data as a scalar dataset of bytes.",
                dtype="bytes",
            ),
            NWBDatasetSpec(
                name="shape",
                doc="The shape (dimensions) of the video, e.g., (frames, height, width, 3).",
                dtype="uint8",
                shape=[
                    [3,],
                    [4,],
                ],
                dims=[
                    [
                        "frames",
                        "height",
                        "width",
                    ],
                    [
                        "frames",
                        "height",
                        "width",
                        "channels",
                    ],
                ]
            ),
        ],
        attributes=[
            NWBAttributeSpec(
                name="fps",
                doc="The frames per second of the video.",
                dtype="float",
            ),
        ],
    )

    mp4_video_data = NWBGroupSpec(
        neurodata_type_def="MP4H264Video",
        neurodata_type_inc="BaseVideo",
        doc=("A container for storing MP4 video data using the H.264 codec as bytes. "
             "Video can be grayscale or color (RGB)."),
    )

    new_data_types = [base_video_data, mp4_video_data]

    # export the spec to yaml files in the spec folder
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "spec"))
    export_spec(ns_builder, new_data_types, output_dir)


if __name__ == "__main__":
    # usage: python create_extension_spec.py
    main()
