import os
import time
from LLBMA.front_end.api import analyse_bma

slide_path = "/media/hdd2/neo/tmp_slides_dir/test_slide.ndpi"
pretiled_h5_path = None
dump_dir = "/media/hdd3/neo/test_error_results_dir_for_error"

os.makedirs(dump_dir, exist_ok=True)

if __name__ == "__main__":

    # if the dump directory does not exist, create it
    if not os.path.exists(dump_dir):
        os.makedirs(dump_dir)
    else:
        # remove the dump directory if it already exists and recreate it
        os.system(f"rm -rf {dump_dir}")
        os.makedirs(dump_dir)

    start_time = time.time()

    # Run the heme_analyze function
    analyse_bma(
        slide_path=slide_path,
        dump_dir=dump_dir,
        hoarding=True,
        extra_hoarding=False,
        continue_on_error=True,
        do_extract_features=False,
        check_specimen_clf=False,
        pretiled_h5_path=pretiled_h5_path,
    )

    print(f"Time taken: {time.time() - start_time:.2f} seconds to process {slide_path}")
