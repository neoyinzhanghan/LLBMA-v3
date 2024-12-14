import os
import io
import h5py
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

    tile = retrieve_tile_h5(slide, level, row, col)  # Retrieve the JPEG image file
    img_io = io.BytesIO()
    tile.save(img_io, format="JPEG")
    img_io.seek(0)
    return send_file(img_io, mimetype="image/jpeg")

@app.route("/", methods=["GET"])
def index():

    root_dir = "/media/hdd3/neo/results_dir"

    subdirs = [
        os.path.join(root_dir, name)
        for name in os.listdir(root_dir)
        if os.path.isdir(os.path.join(root_dir, name))
    ]

    slide_h5_paths = []
    for subdir in subdirs:
        for root, dirs, files in os.walk(subdir):
            if "slide.h5" in files:
                slide_h5_paths.append(os.path.join(root, "slide.h5"))

    slide_options = "".join(
        [f'<option value="{slide}">🌸 {slide}</option>' for slide in slide_h5_paths]
    )

    template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🌺 H5 Slide Viewer 🌺</title>
        <link href="https://fonts.googleapis.com/css2?family=Pacifico&family=Roboto:wght@400;700&display=swap" rel="stylesheet">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/openseadragon/2.4.2/openseadragon.min.js"></script>
        <style>
            body {{
                font-family: 'Roboto', sans-serif;
                margin: 0;
                padding: 0;
                background-color: #1b1b1b;
                color: white;
                transition: background-color 0.3s, color 0.3s;
            }}

            .header {{
                text-align: center;
                padding: 20px;
                background: linear-gradient(to right, #ff7eb3, #ff758c);
                color: white;
                font-family: 'Pacifico', cursive;
                font-size: 24px;
                border-bottom: 2px solid #fff;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            }}

            .theme-toggle {{
                position: fixed;
                top: 10px;
                right: 10px;
                background: #ff69b4;
                border: none;
                border-radius: 20px;
                color: white;
                padding: 10px 20px;
                cursor: pointer;
                font-size: 16px;
                transition: background-color 0.3s;
            }}

            .theme-toggle:hover {{
                background: #ff4582;
            }}

            .search-container {{
                text-align: center;
                margin: 30px auto;
                display: flex;
                justify-content: center;
                align-items: center;
                flex-direction: column;
            }}

            .search-bar {{
                padding: 10px;
                font-size: 16px;
                border-radius: 5px;
                border: 2px solid #ff69b4;
                background: #292929;
                color: white;
                width: 90%;
                max-width: 500px;
                margin-bottom: 20px;
            }}

            select {{
                margin: 20px auto;
                display: block;
                padding: 10px;
                font-size: 16px;
                border-radius: 5px;
                border: 2px solid #ff69b4;
                background: #292929;
                color: white;
                width: 90%;
                max-width: 500px;
                text-align: center;
            }}

            select option {{
                background-color: #1b1b1b;
                color: white;
                padding: 5px;
                border: none;
                transition: all 0.3s;
            }}

            #openseadragon1 {{
                width: 100%;
                height: 500px;
                border: 5px solid #ff69b4;
                border-radius: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="header">🌷✨ Welcome to the H5 Slide Viewer ✨🌷</div>
        <button class="theme-toggle" onclick="toggleTheme()">🌞 Switch to Dark Theme</button>
        <div class="search-container">
            <input type="text" id="searchBar" class="search-bar" placeholder="🌼 Search for a slide..." oninput="filterSlides()">
            <select id="slide" onchange="initializeViewer()">
                {slide_options}
            </select>
        </div>
        <div id="openseadragon1"></div>
        <script>
            let viewer;
            let isDarkTheme = true;

            function toggleTheme() {{
                isDarkTheme = !isDarkTheme;
                document.body.style.backgroundColor = isDarkTheme ? "#1b1b1b" : "#ffffff";
                document.body.style.color = isDarkTheme ? "white" : "black";
                document.querySelector('.theme-toggle').textContent = isDarkTheme ? '🌙 Switch to Light Theme' : '🌞 Switch to Dark Theme';
            }}

            function filterSlides() {{
                const searchInput = document.getElementById('searchBar').value.toLowerCase();
                const slideSelect = document.getElementById('slide');
                const options = slideSelect.options;

                for (let i = 0; i < options.length; i++) {{
                    const slideName = options[i].textContent.toLowerCase();
                    options[i].style.display = slideName.includes(searchInput) ? 'block' : 'none';
                }}
            }}

            function initializeViewer() {{
                const slide = document.getElementById("slide").value;
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
                    }});
            }}

            document.addEventListener('DOMContentLoaded', initializeViewer);
        </script>
    </body>
    </html>
    """
    return render_template_string(template)

@app.route("/get_dimensions", methods=["GET"])
def get_dimensions_api():
    slide = request.args.get("slide")
    width, height = get_dimensions(slide)
    return {"width": width, "height": height}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
