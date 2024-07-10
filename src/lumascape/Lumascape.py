import colorsys
import math
from functools import cached_property
import numpy as np
import squarify
from PIL import Image, ImageDraw, ImageOps
from utils import Log

log = Log('Lumascape')


class Lumascape:
    def __init__(
        self,
        items: list,
        get_name: callable,
        get_group: callable,
        get_image_path: callable,
        size: tuple[int, int],
    ):
        self.items = items
        self.get_name = get_name
        self.get_group = get_group
        self.get_image_path = get_image_path
        self.size = size

    @cached_property
    def width(self):
        return self.size[0]

    @cached_property
    def height(self):
        return self.size[1]

    @cached_property
    def group_to_items(self):
        group_to_items = {}
        for item in self.items:
            group = self.get_group(item)
            if group not in group_to_items:
                group_to_items[group] = []
            group_to_items[group].append(item)

        group_to_items = dict(
            sorted(
                group_to_items.items(), key=lambda x: len(x[1]), reverse=True
            )
        )
        return group_to_items

    @cached_property
    def values(self):
        return [len(value) for value in self.group_to_items.values()]

    @cached_property
    def normalized_values(self):
        return squarify.normalize_sizes(self.values, self.width, self.height)

    @cached_property
    def rects(self):
        return squarify.squarify(
            self.normalized_values, 0, 0, self.width, self.height
        )

    @staticmethod
    def make_circular(im):
  
        im = im.convert("RGBA")
        width, height = im.size
        diameter = min(width, height)
        
        mask = Image.new('L', (diameter, diameter), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, diameter, diameter), fill=255)
        
        circular_im = Image.new('RGBA', (diameter, diameter), (255, 255, 255, 255))
        
        x = (width - diameter) // 2
        y = (height - diameter) // 2
        
        circular_im.paste(im.crop((x, y, x + diameter, y + diameter)), (0, 0), mask)
        return circular_im

    def draw_im_icon(
        self, im, x, y, ix, iy, icon_width, icon_height, items, my
    ):

        icon_image_path = self.get_image_path(items[ix * my + iy])
        im_icon = Image.open(icon_image_path).convert('RGBA')
   
        
        icon_dim = int(min(icon_width, icon_height) * 0.9)
        x_offset = (icon_width - icon_dim) // 2
        y_offset = (icon_height - icon_dim) // 2

        im_icon = im_icon.resize((icon_dim, icon_dim))

        im_icon_masked = Lumascape.make_circular(im_icon)
 
        im.paste(
            im_icon_masked,
            (
                x + ix * icon_width + x_offset,
                y + iy * icon_height + y_offset,
            ),
            im_icon_masked
        )


    @staticmethod
    def get_color(p):
        hue = int(240 * p)
        r , g, b = colorsys.hsv_to_rgb(hue / 360, 1, 0.75)
        return (int(r * 255), int(g * 255), int(b * 255), 255)



    def draw_im_group(self, group, p_group, im, draw, rect, items):
        color = Lumascape.get_color(p_group)


        
        x, y, width, height = [
            int(x) for x in [rect['x'], rect['y'], rect['dx'], rect['dy']]
        ]

        padding = 10
        x += padding
        y += padding
        width -= padding * 2
        height -= padding * 2
        padding2 = padding // 2

        


        n_group = len(items)
        k = math.sqrt(n_group / (width * height))
        mx = max(1, int(width * k))
        my = int(n_group / mx)
        icon_width, icon_height = width // mx, height // my
        for ix in range(mx):
            for iy in range(my):
                self.draw_im_icon(
                    im,
                    x,
                    y,
                    ix,
                    iy,
                    icon_width,
                    icon_height,
                    items,
                    my,
                )
        draw.rectangle(
            [x-padding2, y-padding2, x + width+padding2, y + height+padding2],
            outline=color,

            width=padding//2,
        )

        draw.text(
            (x + width//2, y + height // 2),
            group,
            fill=color,
            align='center',
        )
        print(group)
   

    def draw_im(self):
        im = Image.new('RGBA', self.size, (255, 255, 255, 255))
        draw = ImageDraw.Draw(im)
        for i_group,[rect, [group, items]] in enumerate(zip(
            self.rects, self.group_to_items.items()
        )):
            p_group = i_group / len(self.group_to_items)
            self.draw_im_group(group, p_group,im, draw, rect, items)
        return im

    def write(self, image_path: str):
        im = self.draw_im()
        im.save(image_path)
        log.info(f'Wrote {image_path}')
