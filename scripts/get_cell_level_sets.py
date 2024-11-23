import os
import random
import pandas as pd
from tqdm import tqdm
from LLBMA.resources.BMAassumptions import *

result_dir = "/media/hdd3/neo/test_error_results_dir_025"
save_dir = "/media/hdd3/neo/CC_level_sets"

# if save_dir already exists, delete it
if os.path.exists(save_dir):
    os.system(f"rm -rf {save_dir}")

os.makedirs(save_dir, exist_ok=True)

for cell_type in cellnames:
    os.makedirs(os.path.join(save_dir, cell_type), exist_ok=True)

increment = 0.05


def level_to_str(level: float):
    level = round(level, 2)
    return str(level).replace(".", "_")


def get_levels():
    levels = []
    level = 0.0
    while level < 1.0:
        levels.append(level)
        level += increment

    levels_str = [level_to_str(level) for level in levels]
    return levels, levels_str


# get the levels and levels_str
levels, levels_str = get_levels()


def find_levels(score: float):
    for i in range(len(levels)):
        if i == 0:
            continue
        elif score < levels[i]:
            return levels[i - 1]

    print(f"Score {score} is greater than 1.0")
    print(f"Score {score} is faulty")
    import sys

    sys.exit(1)


for cell_type in cellnames:
    for level_str in levels_str:
        os.makedirs(os.path.join(save_dir, cell_type, level_str), exist_ok=True)

# get all the paths in the result directory
subdirs = [
    os.path.join(result_dir, subdir)
    for subdir in os.listdir(result_dir)
    if os.path.isdir(os.path.join(result_dir, subdir))
]

# only keep the ones that do not start with ERROR
subdirs = [
    subdir for subdir in subdirs if not os.path.basename(subdir).startswith("ERROR")
]

num_per_subdir = 100

pseudo_idx = 0

for subdir in tqdm(subdirs, desc="Processing Result Dirs"):
    # check if the cells folder exists
    cells_dir = os.path.join(subdir, "cells")

    # check how many jpgs are in the cells folder
    jpgs = [
        os.path.join(cells_dir, file)
        for file in os.listdir(cells_dir)
        if file.endswith(".jpg")
    ]

    if len(jpgs) < num_per_subdir:
        print(f"Skipping {subdir} because it has less than {num_per_subdir} jpgs")
        continue

    # randomly select num_per_subdir jpgs
    jpgs = random.sample(jpgs, num_per_subdir)

    cell_df_path = os.path.join(subdir, "cells", "cell_info.csv")

    cell_df = pd.read_csv(cell_df_path)

    for jpg in jpgs:
        jpg_name = os.path.basename(jpg)
        cell_df_row = cell_df[cell_df["name"] == jpg_name]

        for cell_type in cellnames:
            cell_type_prob = cell_df_row[cell_type].values[0]

            level = find_levels(cell_type_prob)
            level_str = level_to_str(level)

            new_name = f"{pseudo_idx}.jpg"
            new_path = os.path.join(save_dir, cell_type, level_str, new_name)

            # create a symlink to the jpg in the appropriate level directory
            os.symlink(jpg, new_path)
            pseudo_idx += 1
