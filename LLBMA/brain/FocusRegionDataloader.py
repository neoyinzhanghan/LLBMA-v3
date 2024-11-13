import torch
import openslide
from PIL import Image
from LLBMA.resources.BMAassumptions import snap_shot_size, region_clf_batch_size, num_croppers
from torchvision import transforms

class HighMagFocusRegionDataset(torch.utils.data.Dataset):
    """ A class that represents a dataset of focus regions. 
    === Attributes ===
    - focus_regions: a list of focus regions objects
    - wsi_path: the path to the WSI
    - wsi: the openslide object of the WSI
    """
    def __init__(self, focus_regions, wsi_path):
        self.focus_regions = focus_regions
        self.wsi_path = focus_regions[0].wsi_path
        self.wsi = openslide.OpenSlide(wsi_path)

    def __len__(self):
        return len(self.focus_regions)
    
    def __getitem__(self, idx):
        focus_region = self.focus_regions[idx]

        pad_size = snap_shot_size // 2

        padded_coordinate = (
            focus_region.coordinate[0] - pad_size,
            focus_region.coordinate[1] - pad_size,
            focus_region.coordinate[2] + pad_size,
            focus_region.coordinate[3] + pad_size,
        )
        padded_image = self.wsi.read_region(
            padded_coordinate,
            0,
            (
                focus_region.coordinate[2]
                - focus_region.coordinate[0]
                + pad_size * 2,
                focus_region.coordinate[3]
                - focus_region.coordinate[1]
                + pad_size * 2,
            ),
        )

        original_width = focus_region.coordinate[2] - focus_region.coordinate[0]
        original_height = focus_region.coordinate[3] - focus_region.coordinate[1]

        unpadded_image = padded_image.crop(
            (
                pad_size,
                pad_size,
                pad_size + original_width,
                pad_size + original_height,
            )
        )

        focus_region.get_image(unpadded_image, padded_image)

        # use transform.ToTensor() to transform the image to a tensor
        padded_image_tensor = transforms.ToTensor()(padded_image)

        return focus_region, padded_image_tensor

def custom_collate_function(batch):
    """A custom collate function that returns the focus regions and the padded images as a batch."""
    focus_regions = [item[0] for item in batch]
    padded_images_tensors = [item[1] for item in batch]
    
    # stack the padded images tensors into a batch
    padded_images_batch = torch.stack(padded_images_tensors)

    return focus_regions, padded_images_batch

def get_high_mag_focus_region_dataloader(focus_regions, wsi_path, batch_size=region_clf_batch_size, num_workers=num_croppers):
    """Return a dataloader of high magnification focus regions."""
    high_mag_focus_region_dataset = HighMagFocusRegionDataset(focus_regions, wsi_path)

    high_mag_focus_region_dataloader = torch.utils.data.DataLoader(
        high_mag_focus_region_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        collate_fn=custom_collate_function,
    )

    return high_mag_focus_region_dataloader

