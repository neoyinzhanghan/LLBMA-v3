from LLBMA.tiling.dzsave_h5 import dzsave_h5

slide_path = "/media/hdd3/neo/error/viewer_test_slide.ndpi"
h5_path_256 = "/media/hdd3/neo/viewer_test_slide_256.h5"
h5_path_512 = "/media/hdd3/neo/viewer_test_slide_512.h5"

print("Saving 256x256 tiles")
dzsave_h5(
    slide_path,
    h5_path_256,
    tile_size=256,
)

print("Saving 512x512 tiles")
dzsave_h5(
    slide_path,
    h5_path_256,
    tile_size=512,
)
