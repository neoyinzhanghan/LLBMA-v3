import io
import h5py
import base64
import numpy as np
from PIL import Image
from LLBMA.resources.BMAassumptions import focus_regions_size, max_dzsave_level


def image_to_jpeg_string(image):
    # Create an in-memory bytes buffer
    buffer = io.BytesIO()
    try:
        # Save the image in JPEG format to the buffer
        image.save(buffer, format="JPEG")
        jpeg_string = buffer.getvalue()  # Get the byte data
    finally:
        buffer.close()  # Explicitly close the buffer to free memory

    return jpeg_string


def jpeg_string_to_image(jpeg_string):
    # Create an in-memory bytes buffer from the byte string
    buffer = io.BytesIO(jpeg_string)

    # Open the image from the buffer and keep the buffer open
    image = Image.open(buffer)

    # Load the image data into memory so that it doesn't depend on the buffer anymore
    image.load()

    return image


def encode_image_to_base64(jpeg_string):
    return base64.b64encode(jpeg_string)


def decode_image_from_base64(encoded_string):
    return base64.b64decode(encoded_string)


def retrieve_tile_h5(h5_path, level, row, col):
    with h5py.File(h5_path, "r") as f:
        try:
            jpeg_string = f[str(level)][row, col]
            jpeg_string = decode_image_from_base64(jpeg_string)
            image = jpeg_string_to_image(jpeg_string)

        except Exception as e:
            print(
                f"Error: {e} occurred while retrieving tile at level: {level}, row: {row}, col: {col} from {h5_path}"
            )
            jpeg_string = f[str(level)][row, col]
            print(f"jpeg_string: {jpeg_string}")
            jpeg_string = decode_image_from_base64(jpeg_string)
            print(f"jpeg_string base 64 decoded: {jpeg_string}")
            raise e
        return image


import h5py


class h5_reader:
    """
    A singleton-like class for reading tiles from an H5 file.
    Ensures only one instance exists per unique h5_path.

    === Attributes ===
    - h5_path : the path to the H5 file
    - f : the H5 file object, None if not opened
    """

    _instances = {}

    def __new__(cls, h5_path):
        # Check if an instance with the same h5_path already exists
        if h5_path in cls._instances:
            return cls._instances[h5_path]
        # If not, create a new instance and store it in the dictionary
        instance = super(h5_reader, cls).__new__(cls)
        cls._instances[h5_path] = instance
        return instance

    def __init__(self, h5_path):
        if hasattr(self, "_initialized") and self._initialized:
            return  # Avoid reinitializing the instance
        self.h5_path = h5_path
        self.f = None
        self._initialized = True

    def open(self):
        """Open the H5 file."""
        if self.f is None:
            self.f = h5py.File(self.h5_path, "r")

    def close(self):
        """Close the H5 file if it's open."""
        if self.f is not None:
            self.f.close()
            self.f = None

    def retrieve_tile(self, level, row, col):
        """
        Retrieve a tile at the specified level, row, and column.

        Parameters:
            level (int): The zoom level of the tile.
            row (int): The row index of the tile.
            col (int): The column index of the tile.

        Returns:
            The tile image as an object.
        """
        if self.f is None:
            raise RuntimeError(
                "H5 file is not open. Please call open() before retrieving tiles."
            )

        try:
            jpeg_string = self.f[str(level)][row, col]
            jpeg_string = decode_image_from_base64(jpeg_string)
            image = jpeg_string_to_image(jpeg_string)
        except Exception as e:
            print(
                f"Error: {e} occurred while retrieving tile at level: {level}, row: {row}, col: {col} from {self.h5_path}"
            )
            jpeg_string = self.f[str(level)][row, col]
            print(f"jpeg_string: {jpeg_string}")
            jpeg_string = decode_image_from_base64(jpeg_string)
            print(f"jpeg_string base 64 decoded: {jpeg_string}")
            raise e

        return image

    def read_region(self, open_slide_level, TL_x, TL_y):
        """
        Retrieve a region of tiles at the specified level and top left corner.

        Parameters:
            level (int): The zoom level of the tile.
            TL_x (int): The x coordinate of the top left corner of the region.
            TL_y (int): The y coordinate of the top left corner of the region.

        Returns:
            The region of tiles as a numpy array.
        """
        if self.f is None:
            raise RuntimeError(
                "H5 file is not open. Please call open() before retrieving tiles."
            )

        row, col = TL_x // focus_regions_size, TL_y // focus_regions_size
        level = max_dzsave_level - open_slide_level
        image = self.retrieve_tile(level, row, col)

        return image
