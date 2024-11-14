import io
import h5py
import base64
import numpy as np
from PIL import Image


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


class h5_reader():
    pass