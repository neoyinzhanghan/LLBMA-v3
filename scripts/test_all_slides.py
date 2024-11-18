import os
from tqdm import tqdm
from LLBMA.front_end.api import analyse_bma

slides_dir = "/media/hdd3/neo/error_slides_ndpi"
h5_dir = "/media/hdd3/neo/error_slides_h5"
dump_dir = "/media/hdd3/neo/test_error_results_dir"

slide_paths = [
    os.path.join(slides_dir, file)
    for file in os.listdir(slides_dir)
    if file.endswith(".ndpi")
]

os.makedirs(dump_dir, exist_ok=True)

for slide_path in tqdm(slide_paths, desc="Processing slides"):

    pretiled_h5_path = os.path.join(
        h5_dir, os.path.basename(slide_path).replace(".ndpi", ".h5")
    )

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
