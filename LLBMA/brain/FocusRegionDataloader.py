import torch
import openslide
from PIL import Image
from LLBMA.resources.BMAassumptions import (
    snap_shot_size,
    region_clf_batch_size,
    num_croppers,
    num_region_clf_managers,
)
from torchvision import transforms


class HighMagFocusRegionDataset(torch.utils.data.Dataset):
    """A class that represents a dataset of focus regions.
    === Attributes ===
    - focus_regions: a list of focus regions objects

    """

    def __init__(self, focus_regions):
        self.focus_regions = focus_regions

    def __len__(self):
        return len(self.focus_regions)

    def __getitem__(self, idx):
        focus_region = self.focus_regions[idx]

        # use transform.ToTensor() to transform the image to a tensor
        image_tensor = transforms.ToTensor()(focus_region.image)

        return focus_region, image_tensor


def custom_collate_function(batch):
    """A custom collate function that returns the focus regions and the images as a batch."""
    focus_regions = [item[0] for item in batch]
    images_tensors = [item[1] for item in batch]

    images_batch = torch.stack(images_tensors)

    return focus_regions, images_batch


def get_high_mag_focus_region_dataloader(
    focus_regions, batch_size=region_clf_batch_size, num_workers=num_croppers
):
    """Return a dataloader of high magnification focus regions."""
    high_mag_focus_region_dataset = HighMagFocusRegionDataset(focus_regions)

    high_mag_focus_region_dataloader = torch.utils.data.DataLoader(
        high_mag_focus_region_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        collate_fn=custom_collate_function,
    )

    return high_mag_focus_region_dataloader


def get_alternating_high_mag_focus_region_dataloader(
    focus_regions,
    wsi_path,
    num_data_loaders=num_region_clf_managers,
    batch_size=region_clf_batch_size,
    num_workers=num_croppers,
):

    list_of_lists_of_focus_regions = [[] for _ in range(num_data_loaders)]
    for i, focus_region in enumerate(focus_regions):
        list_idx = i % num_data_loaders
        list_of_lists_of_focus_regions[list_idx].append(focus_region)

    dataloaders = []

    for focus_regions in list_of_lists_of_focus_regions:
        dataloader = get_high_mag_focus_region_dataloader(
            focus_regions, wsi_path, batch_size, num_workers
        )
        dataloaders.append(dataloader)

    return dataloaders
