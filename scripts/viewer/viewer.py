import streamlit as st
import h5py
import numpy as np
from flask import Flask, send_file, request
from LLBMA.tiling.dzsave_h5 import retrieve_tile_h5

app = Flask(__name__)


@app.route("/tile_api", methods=["GET"])
def tile_api():
    slide = request.args.get("slide")
    level = int(request.args.get("level"))
    row = int(request.args.get("x"))  # Note: x corresponds to row
    col = int(request.args.get("y"))  # Note: y corresponds to col

    tile = retrieve_tile_h5(slide, level, row, col)
    # Return the tile as an image
    tile_img_path = "/tmp/tile_img.png"  # Temporary path
    from PIL import Image

    img = Image.fromarray(tile)
    img.save(tile_img_path)
    return send_file(tile_img_path, mimetype="image/png")


# List of slide H5 paths
slide_h5_paths = [
    "/media/hdd3/neo/results_dir/BMA-diff_2024-12-12 12:52:31/slide.h5",
    "/media/hdd3/neo/results_dir/BMA-diff_2024-12-12 12:59:45/slide.h5",
    "/media/hdd3/neo/results_dir/BMA-diff_2024-12-12 13:55:39/slide.h5",
]

st.title("H5 Slide Viewer with OpenSeadragon")

# Dropdown menu to select a slide
selected_slide = st.selectbox("Select a slide:", slide_h5_paths, index=0)

if selected_slide:
    st.write(f"Displaying: {selected_slide}")

    # Get width and height from the H5 file
    with h5py.File(selected_slide, "r") as f:
        height = int(f["level_0_height"][()])
        width = int(f["level_0_width"][()])

    # Embed OpenSeadragon viewer
    viewer_html = f"""
    <div id="openseadragon1" style="width: 100%; height: 500px;"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/openseadragon/2.4.2/openseadragon.min.js"></script>
    <script>
        var viewer;
        function initializeViewer() {{
            if (viewer) {{
                viewer.destroy();
            }}

            viewer = OpenSeadragon({{
                id: "openseadragon1",
                prefixUrl: "https://cdnjs.cloudflare.com/ajax/libs/openseadragon/2.4.2/images/",
                tileSources: {{
                    width: {width},
                    height: {height},
                    tileSize: 512,
                    maxLevel: 18,
                    getTileUrl: function(level, x, y) {{
                        return `/tile_api?slide=${{encodeURIComponent(selected_slide)}}&level=${{level}}&x=${{x}}&y=${{y}}`;
                    }}
                }},
                showNavigator: true
            }});

            var zoomDisplay = document.createElement('div');
            zoomDisplay.id = 'zoomDisplay';
            zoomDisplay.style.position = 'absolute';
            zoomDisplay.style.bottom = '10px';
            zoomDisplay.style.right = '10px';
            zoomDisplay.style.background = 'rgba(0, 0, 0, 0.5)';
            zoomDisplay.style.color = 'white';
            zoomDisplay.style.padding = '5px';
            zoomDisplay.style.borderRadius = '5px';
            zoomDisplay.style.fontFamily = 'Arial, sans-serif';
            zoomDisplay.style.fontSize = '14px';
            zoomDisplay.style.zIndex = '9999';

            viewer.container.appendChild(zoomDisplay);

            function updateZoomDisplay() {{
                var zoom = viewer.viewport.getZoom(true);
                zoomDisplay.textContent = 'Zoom: ' + zoom.toFixed(2) + 'x';
            }}

            viewer.addHandler('zoom', updateZoomDisplay);
            updateZoomDisplay();
        }}

        document.addEventListener('DOMContentLoaded', initializeViewer);
    </script>
    """
    st.components.v1.html(viewer_html, height=550)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
