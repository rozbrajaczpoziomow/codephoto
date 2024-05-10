import json
from PIL import Image, ImageDraw, ImageChops
from pygments import highlight
from pygments.lexers import guess_lexer, get_all_lexers, find_lexer_class_by_name, find_lexer_class
from pygments.formatters.img import ImageFormatter

class CustomFormatter(ImageFormatter):
    def format(self, tokensource, outfile):
        self._create_drawables(tokensource)
        self._draw_line_numbers()
        im = Image.new(
            'RGB',
            self._get_image_size(self.maxlinelength, self.maxlineno),
            self.background_color
        )
        self._paint_line_number_bg(im)
        draw = ImageDraw.Draw(im)
        # Highlight
        if self.hl_lines:
            x = self.image_pad + self.line_number_width - self.line_number_pad + 1
            recth = self._get_line_height()
            rectw = im.size[0] - x
            for linenumber in self.hl_lines:
                y = self._get_line_y(linenumber - 1)
                draw.rectangle([(x, y), (x + rectw, y + recth)],
                               fill=self.hl_color)
        for pos, value, font, text_fg, text_bg in self.drawables:
            draw.text(pos, value, font=font, fill=text_fg)
        self.image = im


def get_formatter(dark):
    if dark:
        return CustomFormatter(
            style="monokai",
            format="png",
            line_numbers=True,
            font_name='DejaVu Sans Mono',
            font_size=14,
            line_number_bg="#272822",
            line_number_fg="#888888",
            image_pad=8,
        )
    return CustomFormatter(
        style="tango",
        format="png",
        line_numbers=True,
        font_name='DejaVu Sans Mono',
        font_size=14,
        line_number_bg="#e0e0e0",
        line_number_fg="#999999",
        image_pad=8,
    )


def limit_input(content: str, max_lines=47) -> str:
    lines = content.splitlines()
    if len(lines) > max_lines:
        lines = lines[:max_lines]
    else:
        lines = lines + [" "] * (max_lines - len(lines))
    return "\n".join(lines)


matrix_cache: Dict[str, List[int]] = {}


def get_matrix_file(background: str) -> str:
    return background.rsplit(".", maxsplit=1)[0] + ".json"


def get_matrix(bg):
    if bg not in matrix_cache:
        with open(get_matrix_file(bg)) as f:
            matrix_cache[bg] = json.load(f)["coefficients"]
    return matrix_cache[bg]


def transform(img, img_file, background, matrix=None):
    background_img_raw = Image.open(background)
    if matrix is None:
        matrix = get_matrix(background)

    foreground_img_raw = img
    foreground_img_raw = foreground_img_raw.transform(background_img_raw.size, method=Image.PERSPECTIVE, data=matrix,
                                                      resample=Image.BILINEAR, fillcolor=(255, 255, 255))

    ImageChops.multiply(foreground_img_raw, background_img_raw).convert("RGB").save(img_file)


def make_image(content, output, lang, background, dark=False, matrix=None):
    lexer = None
    if lang:
        lexer = find_lexer_class(lang)()
    if not lexer:
        lexer = guess_lexer(content)
    formatter = get_formatter(dark)
    highlight(limit_input(content), lexer, formatter, output)
    transform(formatter.image, output, background, matrix)


def get_languages():
    if not languages:
        languages.extend(sorted([
            x[0] for x in get_all_lexers()
        ]))
    return languages