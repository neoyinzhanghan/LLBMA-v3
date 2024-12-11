import h5py
from LLBMA.tiling.dzsave_h5 import retrieve_tile_h5

dzsave_h5_path = "/media/hdd3/neo/test_error_results_dir_tmp/test_slide/slide.h5"

# open the h5 file
with h5py.File(dzsave_h5_path, "r") as f:
    # get the "0" dataset
    dataset = f["3"]

    # print the dimensions of the dataset
    print(dataset.shape)

    # print the the [0,0] element of the dataset
    print(dataset[0, 0])
