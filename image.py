import sys
import numpy as np
from math import floor
from PIL import Image as PImage

def normalize_dim(in_bounds, in_value, out_size):
    in_size = in_bounds[1] - in_bounds[0] + 1
    out_value = (in_value - in_bounds[0]) / in_size * out_size
    return floor(out_value)

def temperature_to_color(temperature, magnitude):
    color = None

    if temperature > 30000:   # O
        color = np.array([0x9A, 0xAF, 0xFF], dtype=np.float64)
    elif temperature > 10000: # B
        color = np.array([0xCA, 0xD7, 0xFF], dtype=np.float64)
    elif temperature > 7400:  # A
        color = np.array([0xFF, 0xFF, 0xFF], dtype=np.float64)
    elif temperature > 6000:  # F
        color = np.array([0xFF, 0xF9, 0xC5], dtype=np.float64)
    elif temperature > 5000:  # G
        color = np.array([0xFF, 0xF2, 0xA1], dtype=np.float64)
    elif temperature > 3800:  # K
        color = np.array([0xFF, 0xC4, 0x6F], dtype=np.float64)
    elif temperature > 2500:  # M
        color = np.array([0xFF, 0x60, 0x60], dtype=np.float64)
    else:
        color = np.array([0xFF, 0x00, 0x00], dtype=np.float64)

    mul = 100 ** (-magnitude/5)
    color *= mul

    return color

class Image:
    def __init__(self):
        output_size = 10000
        self.input_dims = ((-42213, 40503), (-23405, 65630))
        self.output_dims = (output_size, output_size, 3)
        self.image = np.zeros(self.output_dims, dtype=np.float64)

    def finalize(self):
        self.image /= np.max(self.image, axis=2, keepdims=True)
        self.image *= 255
        self.image = np.asarray(self.image, dtype=np.int8)

        img = PImage.fromarray(self.image, mode="RGB")
        img = img.rotate(90)
        img.save("img.png")

    def process(self, system):
        #generate color
        xdim = normalize_dim(self.input_dims[0], system["coords"]["x"], self.output_dims[0])
        zdim = normalize_dim(self.input_dims[1], system["coords"]["z"], self.output_dims[1])

        for body in system["bodies"]:
            if not 'type' in body:
                continue

            if body["type"] == "Star":
                if not 'surfaceTemperature' in body:
                    continue

                if not 'absoluteMagnitude' in body:
                    continue

                color = temperature_to_color(body["surfaceTemperature"], body["absoluteMagnitude"])
                self.image[xdim,zdim] += color

