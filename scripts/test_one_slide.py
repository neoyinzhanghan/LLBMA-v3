import os
from LLBMA.front_end.api import analyse_bma

slide_path = (
    "/media/hdd3/neo/error_slides_ndpi/H24-3456;S20;MSK9 - 2024-05-20 12.14.45.ndpi"
)
pretiled_h5_path = (
    "/media/hdd3/neo/error_slides_h5/H24-3456;S20;MSK9 - 2024-05-20 12.14.45.h5"
)
dump_dir = "/media/hdd3/neo/test_error_results_dir"

os.makedirs(dump_dir, exist_ok=True)

if __name__ == "__main__":

    # if the dump directory does not exist, create it
    if not os.path.exists(dump_dir):
        os.makedirs(dump_dir)
    else:
        # remove the dump directory if it already exists and recreate it
        os.system(f"rm -rf {dump_dir}")
        os.makedirs(dump_dir)

    # Run the heme_analyze function
    analyse_bma(
        slide_path=slide_path,
        dump_dir=dump_dir,
        hoarding=True,
        continue_on_error=True,
        do_extract_features=False,
        check_specimen_clf=False,
        pretiled_h5_path=pretiled_h5_path,
    )
