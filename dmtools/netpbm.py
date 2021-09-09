import os
import imageio
import numpy as np
from skimage.transform import rescale
from typing import List
from ._log import _log_msg
import logging


# TODO: Improve this class defintion following conventions described in
# http://netpbm.sourceforge.net.
class Netpbm:
    """An object representing a Netpbm image.

    For more information about Netpbm images, see the
    `Netpbm Home Page <http://netpbm.sourceforge.net/>`_.
    """
    extension_to_magic_number = {"pbm": 1, "pgm": 2, "ppm": 3}
    magic_number_to_extension = {1: "pbm", 2: "pgm", 3: "ppm"}

    def __init__(self, P: int, k: int, M: np.ndarray):
        """Initialize a Netpbm image.

        Args:
            P (int): Magic number of the Netpbm image.
            k (int): Maximum gray/color value
            M (np.ndarray): A NumPy array representing the image pixels.
        """
        self.P = P
        self.h, self.w, *_ = M.shape
        self.k = k
        self.M = M

    def __copy__(self):
        return Netpbm(P=self.P, k=self.k, M=self.M)

    def set_max_color_value(self, k: int):
        """Set the maximum gray/color value of this Netpbm image.

        Args:
            k (int): Maximum gray/color value.
        """
        if k == 1:
            self.M = ((self.M / self.k) > 0.5).astype(int)
            if self.P == 2:
                self.P == 1
        else:
            step = int(self.k / k)
            self.M = np.array(list(map(lambda x: x // step, self.M)), dtype=int)

    def to_netpbm(self, path: str):
        """Write object to a Netpbm file (pbm, pgm, ppm).

        Uses the ASCII (plain) magic numbers.

        Args:
            path (str): String file path.
        """
        with open(path, "w") as f:
            f.write('P%d\n' % self.P)
            f.write("%s %s\n" % (self.w, self.h))
            if self.P != 1:
                f.write("%s\n" % (self.k))
            if self.P == 3:
                M = self.M.reshape(self.h, self.w * 3)
            else:
                M = self.M
            lines = M.clip(0, self.k).astype(int).astype(str).tolist()
            f.write('\n'.join([' '.join(line) for line in lines]))
            f.write('\n')
        logging.info(_log_msg(path, os.stat(path).st_size))

    def to_png(self, path: str):
        """Write object to a png file.

        Args:
            path (str): String file path.
        """
        M = self.M
        if self.P == 1:
            M = np.where(M == 1, 0, 1)
        M = np.array(M * (255 / self.k), dtype=np.uint8)
        imageio.imwrite(path, M)
        logging.info(_log_msg(path, os.stat(path).st_size))


def _parse_ascii_netpbm(f: List[str]) -> Netpbm:
    # adapted from code by Dan Torop
    vals = [v for line in f for v in line.split('#')[0].split()]
    P = int(vals[0][1])
    if P == 1:
        w, h, *vals = [int(v) for v in vals[1:]]
        k = 1
    else:
        w, h, k, *vals = [int(v) for v in vals[1:]]
    if P == 3:
        M = np.array(vals).reshape(h, w, 3)
    else:
        M = np.array(vals).reshape(h, w)
    return Netpbm(P=P, k=k, M=M)


# TODO: make the file reading code more robust
def _parse_binary_netpbm(path: str) -> Netpbm:
    # adapted from https://www.stackvidhya.com/python-read-binary-file/
    with open(path, "rb") as f:
        P = int(f.readline().decode()[1])
        # change to corresponding ASCII magic number
        P = int(P / 2)
        w = int(f.readline().decode()[:-1])
        h = int(f.readline().decode()[:-1])
        if P == 1:
            k = 1
        else:
            k = int(f.readline().decode()[:-1])
        dtype = np.dtype('B')
        M = np.fromfile(f, dtype)
        if P == 3:
            M = M.reshape(h, w, 3)
        else:
            M = M.reshape(h, w)
    return Netpbm(P=P, k=k, M=M)


def read_netpbm(path: str) -> Netpbm:
    """Read Netpbm file (pbm, pgm, ppm) into Netpbm.

    Args:
        path (str): String file path.

    Returns:
        Netpbm: A Netpbm image
    """
    with open(path, "rb") as f:
        magic_number = f.read(2).decode()
    if int(magic_number[1]) <= 3:
        # P1, P2, P3 are the ASCII (plain) formats
        with open(path) as f:
            return _parse_ascii_netpbm(f)
    else:
        # P4, P5, P6 are the binary (raw) formats
        return _parse_binary_netpbm(path)


def enlarge(image: Netpbm, k: int) -> Netpbm:
    """Enlarge the netpbm image by the multiplier k.

    Args:
        image (Netpbm): Netpbm image to enlarge.

    Returns:
       Netpbm: Enlarged Netpbm image.
    """
    # old implementation -- now using skimage for efficiency
    # ======================================================
    # M = image.M
    # n,m = M.shape
    # expanded_rows = np.zeros((n*k,m))
    # for i in range(n*k):
    #     expanded_rows[i] = M[i // k]
    # expanded = np.zeros((n*k, m*k))
    # for j in range(m*k):
    #     expanded[:,j] = expanded_rows[:,j // k]
    # M_prime = expanded.astype(int)
    # ======================================================

    # NEAREST_NEIGHBOR (order=0)
    M = rescale(image.M, k,
                order=0, preserve_range=True, multichannel=(image.P == 3))
    return Netpbm(P=image.P, k=image.k, M=M)


def image_grid(images: List[Netpbm], w: int, h: int, b: int,
               color: int = "white") -> Netpbm:
    """Create a w * h grid of images with a border of width b.

    Args:
        images (List[Netpbm]): images to be put in the grid (same dimensions).
        w (int): number of images in each row of the grid.
        h (int): number of images in each column of the grid.
        b (int): width of the border/margin.
        color (int): color of border {'white', 'black'} (defaults to white).

    Returns:
        Netpbm: grid layout of the images.
    """
    n,m = images[0].M.shape
    k = images[0].k
    c = {'white': k, 'black': 0}[color]
    h_border = c*np.ones((b, w*m + (w+1)*b))
    v_border = c*np.ones((n, b))
    grid_layout = h_border
    p = 0
    for i in range(h):
        row = v_border
        for j in range(w):
            row = np.hstack((row, images[p].M))
            row = np.hstack((row, v_border))
            p += 1
        grid_layout = np.vstack((grid_layout, row))
        grid_layout = np.vstack((grid_layout, h_border))
    return Netpbm(P=images[0].P, k=k, M=grid_layout.astype(int))


def border(image: Netpbm, b: int, color: int = "white") -> Netpbm:
    """Add a border of width b to the image

    Args:
        image (Netpbm): Netpbm image to add a border to
        b (int): width of the border/margin.
        color (int): color of border {'white', 'black'} (defaults to white).

    Returns:
        Netpbm: Image with border added.
    """
    return image_grid([image], w=1, h=1, b=b, color=color)

# TODO: Comment to write in file should be provided as optional argument
# def netpbm_comment(file_name:str):
#     """Comment to be written in the

#     Args:
#         file_name (str): Name of the Netpbm file to be written.
#     """
#     name = file_name.split('/')[-1]
#     lines = ["Title: %s\n" % name,
#              "Compiled on: %s\n" % datetime.datetime.now(), "\n"]
#     readme_path = "/".join(file_name.split('/')[:-1]) + "/README.md"
#     with open(readme_path) as f:
#         readme = f.readlines()
#         indices = [i for i in range(len(readme)) if readme[i] == '\n']
#         lines = lines + readme[:indices[1]]
#     lines = ["# " + line for line in lines]
#     return lines
