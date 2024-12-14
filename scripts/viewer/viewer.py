import streamlit as st
from streamlit_openseadragon import StreamlitOpenSeadragon
import h5py
import numpy as np


# Function to retrieve tile from H5 file
def retrieve_tile_h5(h5_path, level, row, col):
    with h5py.File(h5_path, "r") as h5_file:
        level_group = h5_file[f"level_{level}"]
        tile_dataset = level_group[f"row_{row}"][f"col_{col}"]
        tile = np.array(tile_dataset)
    return tile


# List of slide H5 paths
slide_h5_paths = [
    "/media/hdd3/neo/results_dir/BMA-diff_2024-12-12 12:52:31/slide.h5",
    "/media/hdd3/neo/results_dir/BMA-diff_2024-12-12 12:59:45/slide.txt",
    "/media/hdd3/neo/results_dir/BMA-diff_2024-12-12 13:55:39/slide.h5",
]

st.title("H5 Slide Viewer with OpenSeadragon")

# Dropdown menu to select a slide
selected_slide = st.selectbox("Select a slide:", slide_h5_paths, index=0)

if selected_slide:
    st.write(f"Displaying: {selected_slide}")

    # Function to serve tiles dynamically for OpenSeadragon
    def tile_callback(level, x, y):
        try:
            tile = retrieve_tile_h5(selected_slide, level, y, x)
            return tile
        except KeyError:
            return None

    # Display the OpenSeadragon viewer
    StreamlitOpenSeadragon(
        tile_callback=tile_callback,
        max_zoom=5,  # Example: adjust based on your H5 tile levels
        tile_size=256,  # Ensure this matches your H5 file's tile size
    )
