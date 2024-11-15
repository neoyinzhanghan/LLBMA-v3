import os
import ray
import pandas as pd
from LLBMA.brain.BMAHighMagRegionChecker import (
    BMAHighMagRegionCheckerBatched,
)
from LLBMA.resources.BMAassumptions import (
    num_region_clf_managers,
    high_mag_region_clf_ckpt_path,
    min_num_focus_regions,
    high_mag_region_clf_threshold,
    max_num_focus_regions,
)
from LLBMA.brain.FocusRegionDataloader import (
    get_high_mag_focus_region_dataloader,
)
from tqdm import tqdm
from ray.exceptions import RayTaskError


def sort_focus_regions_based_on_low_mag_score(focus_regions):
    """Sort the focus regions based on the confidence score at low magnification."""
    return sorted(
        focus_regions, key=lambda x: x.adequate_confidence_score, reverse=True
    )


class BMAHighMagRegionCheckTracker:
    """A class that keeps track of focus regions that made it past the low magnification checks.
    This class keeps track of the high magnification quality control of these regions.

    === Class Attributes ===
    - focus_regions: a list of focus regions that made it past the low magnification checks
    - info_df: a pandas DataFrame that stores the information of the focus regions
    - wsi_path: the path to the WSI

    """

    def __init__(self, focus_regions, wsi_path) -> None:

        self.wsi_path = wsi_path
        tasks = {}
        new_focus_regions = []

        sorted_focus_regions = sort_focus_regions_based_on_low_mag_score(focus_regions)

        # dataloader = get_high_mag_focus_region_dataloader(
        #     sorted_focus_regions, wsi_path
        # )

        # high_mag_checkers = [
        #     BMAHighMagRegionCheckerBatched.remote(
        #         model_ckpt_path=high_mag_region_clf_ckpt_path,
        #     )
        #     for _ in range(num_region_clf_managers)
        # ]

        # tasks = {}
        # new_focus_regions = []
        # total_found = 0

        # with tqdm(
        #     total=len(focus_regions),
        #     desc="Getting high magnification focus regions diagnostics...",
        # ) as pbar_N:
        #     with tqdm(
        #         total=max_num_focus_regions,
        #         desc="Getting high magnification focus regions diagnostics...",
        #     ) as pbar_R:

        #         # Iterate through the dataloader
        #         data_iter = iter(dataloader)

        #         try:
        #             while True:
        #                 # Stop sending batches if the total found regions exceed max_num_focus_regions
        #                 if total_found >= max_num_focus_regions:
        #                     break

        #                 # Send a batch to each worker if possible
        #                 for high_mag_checker in high_mag_checkers:
        #                     try:
        #                         batch = next(data_iter)  # Get the next batch
        #                     except StopIteration:
        #                         break  # Dataloader is exhausted

        #                     # Assign batch to the worker
        #                     tasks[high_mag_checker] = (
        #                         high_mag_checker.async_check_high_mag_score.remote(
        #                             batch
        #                         )
        #                     )

        #                 # Process completed tasks
        #                 while tasks:
        #                     done, _ = ray.wait(list(tasks.values()), timeout=0.1)
        #                     for done_task_id in done:
        #                         try:
        #                             # Retrieve results from Ray task
        #                             focus_regions, num_found = ray.get(done_task_id)
        #                             new_focus_regions.extend(focus_regions)
        #                             total_found += num_found

        #                             # Update progress bars
        #                             pbar_R.update(num_found)
        #                             pbar_N.update(len(focus_regions))

        #                             # Stop further processing if max_num_focus_regions is reached
        #                             if total_found >= max_num_focus_regions:
        #                                 tasks.clear()  # Cancel remaining tasks
        #                                 break
        #                         except RayTaskError as e:
        #                             print(e)
        #                         finally:
        #                             # Remove completed task from the dictionary
        #                             del tasks[done_task_id]

        #                     if total_found >= max_num_focus_regions:
        #                         break

        #         except Exception as e:
        #             print(f"Error occurred: {e}")

        # ray.shutdown()

        # self.focus_regions = new_focus_regions

        dataloader = get_high_mag_focus_region_dataloader(
            sorted_focus_regions, wsi_path
        )

        high_mag_checkers = [
            BMAHighMagRegionCheckerBatched.remote(
                model_ckpt_path=high_mag_region_clf_ckpt_path,
            )
            for _ in range(num_region_clf_managers)
        ]

        tasks = {}
        new_focus_regions = []

        with tqdm(
            total=len(focus_regions),
            desc="Getting high magnification focus regions diagnostics...",
        ) as pbar:

            # Iterate through the dataloader
            data_iter = iter(dataloader)

            try:
                while True:
                    # Send a batch to each worker if possible
                    for high_mag_checker in high_mag_checkers:
                        try:
                            batch = next(data_iter)  # Get the next batch
                        except StopIteration:
                            break  # Dataloader is exhausted

                        # Assign batch to the worker
                        task_id = high_mag_checker.async_check_high_mag_score.remote(
                            batch
                        )
                        tasks[task_id] = high_mag_checker  # Use ObjectRef as the key

                    # Process completed tasks
                    while tasks:
                        done, _ = ray.wait(list(tasks.keys()), timeout=0.1)
                        for done_task_id in done:
                            try:
                                # Retrieve results from Ray task
                                focus_regions, _ = ray.get(done_task_id)
                                new_focus_regions.extend(focus_regions)

                                # Update progress bar
                                pbar.update(len(focus_regions))
                            except RayTaskError as e:
                                print(e)
                            finally:
                                # Remove completed task from the dictionary
                                del tasks[done_task_id]  # Use ObjectRef as the key

            except Exception as e:
                print(f"Error occurred: {e}")

        ray.shutdown()

        self.focus_regions = new_focus_regions

        print(
            f"Number of focus regions after high magnification check: {len(self.focus_regions)}"
        )

        # populate the info_df with the information of the focus regions
        info_dct = {
            "idx": [],
            "VoL_high_mag": [],
            "adequate_confidence_score_high_mag": [],
            "selected_high_mag": [],
        }

        for focus_region in self.focus_regions:
            info_dct["idx"].append(focus_region.idx)
            info_dct["VoL_high_mag"].append(focus_region.VoL_high_mag)
            info_dct["adequate_confidence_score_high_mag"].append(
                focus_region.adequate_confidence_score_high_mag
            )
            info_dct["selected_high_mag"].append(
                focus_region.adequate_confidence_score_high_mag
                > high_mag_region_clf_threshold
            )

        # create a pandas DataFrame to store the information of the focus regions
        # it should have the following columns:
        # --idx: the index of the focus region
        # --VoL_high_mag: the volume of the focus region at high magnification
        # --adequate_confidence_score_high_mag: the confidence score of the focus region at high magnification

        self.info_df = pd.DataFrame(info_dct)

        print(
            f"Number of selected focus regions after high magnification check: {len(self.info_df[self.info_df['selected_high_mag']])}"
        )

    def get_good_focus_regions(self):
        """The criterion for a good focus region is that it has an adequate confidence score at high magnification:
        - VoL_high_mag > 7
        - adequate_confidence_score_high_mag > high_mag_region_clf_threshold
        """

        good_focus_regions = []

        for focus_region in self.focus_regions:
            if (
                focus_region.VoL_high_mag > 8
                and focus_region.adequate_confidence_score_high_mag
                > high_mag_region_clf_threshold
            ):
                good_focus_regions.append(focus_region)

        # if len(good_focus_regions) < min_num_focus_regions:
        #     raise HighMagCheckFailedError(
        #         f"Only {len(good_focus_regions)} good focus regions remain after the high magnification check, and the minimum number of focus regions required is {min_num_focus_regions}."
        #     )

        return good_focus_regions

    def save_results(self, save_dir):

        # save the df in the save_dir/focus_regions/high_mag_focus_regions_info.csv
        self.info_df.to_csv(f"{save_dir}/focus_regions/high_mag_focus_regions_info.csv")

    def hoard_results(self, save_dir):
        # os.makedirs(f"{save_dir}/focus_regions/high_mag_rejected", exist_ok=True)

        # good_focus_regions = self.get_good_focus_regions()
        # bad_focus_regions = [
        #     focus_region
        #     for focus_region in self.focus_regions
        #     if focus_region not in good_focus_regions
        # ]

        # for focus_region in tqdm(
        #     bad_focus_regions, desc="Saving rejected focus regions..."
        # ):
        #     focus_region.image.save(
        #         f"{save_dir}/focus_regions/high_mag_rejected/{focus_region.idx}.jpg"
        #     )
        pass  # TODO TODO TODO DEPRECATED we no longer hoard high mag rejected regions after the implementation of dynamic region filtering


class HighMagCheckFailedError(Exception):
    """This error is raised when not enough good focus regions remain after the high magnification check."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
