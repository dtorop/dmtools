import os
import pytest
import numpy as np
from dmtools.transform import rescale
from dmtools.colorspace import gray_to_RGB
from dmtools.io import read_png

RESOURCES_PATH = os.path.join(os.path.dirname(__file__), 'resources')

# These tests are derived from ImageMagick example images which can be found in
# https://legacy.imagemagick.org/Usage/filter/
#
# Links test imagery used for each filter
#
# Point filter: https://legacy.imagemagick.org/Usage/filter/#point
# Box filter: https://legacy.imagemagick.org/Usage/filter/#box
# Triangle filter: https://legacy.imagemagick.org/Usage/filter/#triangle
# Gaussian filter: https://legacy.imagemagick.org/Usage/filter/#gaussian


@pytest.mark.parametrize("image,filter,k,new_name",[
    ('checks_10', 'point', 0.9, 'point_0.9'),
    ('checks_10', 'point', 0.8, 'point_0.8'),
    ('checks_10', 'point', 0.7, 'point_0.7'),
    ('checks_10', 'point', 0.6, 'point_0.6'),
    ('checks_10', 'point', 0.5, 'point_0.5'),
    ('checks_10', 'box', 0.9, 'box_0.9'),
    # ('checks_10', 'box', 0.8, 'box_0.8'), strangely differs from ImageMagick
    ('checks_10', 'box', 0.7, 'box_0.7'),
    ('checks_10', 'box', 0.6, 'box_0.6'),
    ('checks_10', 'box', 0.5, 'box_0.5'),
    ('checks_5', 'box', 1.2, 'box_1.2'),
    ('checks_5', 'point', 1.2, 'box_1.2'),
    ('checks_5', 'box', 1.4, 'box_1.4'),
    ('checks_5', 'point', 1.4, 'box_1.4'),
    ('checks_5', 'box', 1.6, 'box_1.6'),
    ('checks_5', 'point', 1.6, 'box_1.6'),
    ('checks_5', 'box', 1.8, 'box_1.8'),
    ('checks_5', 'point', 1.8, 'box_1.8'),
    ('checks_5', 'box', 2.0, 'box_2.0'),
    ('checks_5', 'point', 2.0, 'box_2.0'),
    ('checks_10', 'triangle', 0.9, 'triangle_0.9'),
    ('checks_10', 'triangle', 0.8, 'triangle_0.8'),
    ('checks_10', 'triangle', 0.7, 'triangle_0.7'),
    ('checks_10', 'triangle', 0.6, 'triangle_0.6'),
    ('checks_10', 'triangle', 0.5, 'triangle_0.5'),
    ('checks_5', 'triangle', 1.2, 'triangle_1.2'),
    ('checks_5', 'triangle', 1.4, 'triangle_1.4'),
    ('checks_5', 'triangle', 1.6, 'triangle_1.6'),
    ('checks_5', 'triangle', 1.8, 'triangle_1.8'),
    ('checks_5', 'triangle', 2.0, 'triangle_2.0')])
def test_rescale(image, filter, k, new_name):
    # single channel
    src = read_png(os.path.join(RESOURCES_PATH, image, 'src.png'))
    new = read_png(os.path.join(RESOURCES_PATH, image, new_name + '.png'))
    assert np.allclose(new, rescale(image=src, k=k, filter=filter), atol=2)

    # three channel
    src = gray_to_RGB(src)
    new = gray_to_RGB(new)
    assert np.allclose(new, rescale(image=src, k=k, filter=filter), atol=2)


@pytest.mark.parametrize("image,k,blur,new_name",[
    ('pixel_5', 300, 0.5, 'blur_0.5'),
    ('pixel_5', 300, 1.0, 'blur_1.0'),
    ('pixel_5', 300, 1.5, 'blur_1.5')])
def test_gaussian_blur(image, k, blur, new_name):
    src = read_png(os.path.join(RESOURCES_PATH, image, 'src.png'))
    new = read_png(os.path.join(RESOURCES_PATH, image, new_name + '.png'))
    assert np.allclose(new, rescale(src, k=k, filter='gaussian', blur=blur),
                       atol=2)
