import os
from LLBMA.front_end.api import analyse_bma

slide_path = "/media/hdd3/neo/tmp_slide_dir/H22-7033;S12;MSK3 - 2023-06-06 19.17.45.ndpi"
dump_dir = "/media/hdd3/neo/results_dir"

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
        continue_on_error=False,
        do_extract_features=False,
        check_specimen_clf=True,
    )
