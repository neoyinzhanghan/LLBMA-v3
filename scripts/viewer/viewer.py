import h5py
import numpy as np
from flask import Flask, send_file, request, render_template_string
from LLBMA.tiling.dzsave_h5 import retrieve_tile_h5

app = Flask(__name__)

# Function to get dimensions from H5 file
def get_dimensions(h5_path):
    with h5py.File(h5_path, "r") as f:
        height = int(f["level_0_height"][()])
        width = int(f["level_0_width"][()])
    return width, height

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

@app.route("/", methods=["GET"])
def index():
    # List of slide H5 paths
    slide_h5_paths = [
        "/media/hdd3/neo/results_dir/BMA-diff_2024-12-12 12:52:31/slide.h5",
        "/media/hdd3/neo/results_dir/BMA-diff_2024-12-12 12:59:45/slide.h5",
        "/media/hdd3/neo/results_dir/BMA-diff_2024-12-12 13:55:39/slide.h5",
    ]

    slide_options = "".join([f'<option value="{slide}">{slide}</option>' for slide in slide_h5_paths])

    template = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>H5 Slide Viewer</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/openseadragon/2.4.2/openseadragon.min.js"></script>
    </head>
    <body>
        <h1>H5 Slide Viewer with OpenSeadragon</h1>
        <label for="slide">Select a slide:</label>
        <select id="slide" onchange="initializeViewer()">
            {slide_options}
        </select>
        <div id="openseadragon1" style="width: 100%; height: 500px;"></div>
        <script>
            var viewer;

            function initializeViewer() {{
                var slide = document.getElementById("slide").value;
                fetch(`/get_dimensions?slide=${{encodeURIComponent(slide)}}`)
                    .then(response => response.json())
                    .then(dimensions => {{
                        const width = dimensions.width;
                        const height = dimensions.height;

                        if (viewer) {{
                            viewer.destroy();
                        }}

                        viewer = OpenSeadragon({{
                            id: "openseadragon1",
                            prefixUrl: "https://cdnjs.cloudflare.com/ajax/libs/openseadragon/2.4.2/images/",
                            tileSources: {{
                                width: width,
                                height: height,
                                tileSize: 512,
                                maxLevel: 18,
                                getTileUrl: function(level, x, y) {{
                                    return `/tile_api?slide=${{encodeURIComponent(slide)}}&level=${{level}}&x=${{x}}&y=${{y}}`;
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
                    }});
            }}

            document.addEventListener('DOMContentLoaded', initializeViewer);
        </script>
    </body>
    </html>
    '''
    return render_template_string(template)

@app.route("/get_dimensions", methods=["GET"])
def get_dimensions_api():
    slide = request.args.get("slide")
    width, height = get_dimensions(slide)
    return {"width": width, "height": height}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
