from os import makedirs

import requests
from bs4 import BeautifulSoup as BS
from fpdf import FPDF
from PIL import Image
import os

from status.status import Status, get_status_length

from flask_socketio import SocketIO

__author__ = "nighmared & m4xy07" # credits to nighmared for the original script
__version__ = 1.36 


DEBUG = False  # makes it more verbose
PDF_H = 300  # Height of resulting PDF
PDF_W = 200  # Width of resulting PDF
# For most comics i have seen an aspect ratio of 2:3 seems to be a good call

PROGRESS_BAR_LEN = 50  # lenght of the progress bar that is displayed
STATUS_LEN = (
    get_status_length() + 1
)  # How much space must be accounted for the status in the progress bar
NUM_STEPS = len(Status)  # Number of steps the program goes through
STEP_SIZE = (
    PROGRESS_BAR_LEN // NUM_STEPS
)  # equal length parts for the status bar


def main(url: str, name: str, socketio: SocketIO, callback=None):
    """
    main method that processes the provided url.
    """
    handle_entry(url=url, name=name, socketio=socketio, callback=callback)


def make_progress_bar(current: int, max_len: int, step: int) -> str:
    """
    Takes three ints as input, current and max are the values
    that get used to compute the current progress by standard
    percentage computation. The resulting progress bar is then
    scaled according to the constant PROGRESS_BAR_LEN and
    divided into NUM_STEPS. Here the last argument 'step' comes
    into play, as it is used to determine the overall progress
    of the script in relation to the number of steps defined
    in the Status Enum.
    """
    perc = step * STEP_SIZE + (STEP_SIZE * current) // max_len
    return f"[{('|'*perc).ljust(PROGRESS_BAR_LEN)}]"


def make_status_string(
    current_status: Status,
    step_num: int,
    title: str,
    current_progress: int,
    max_progress: int,
) -> str:

    res = (
        title.ljust(40)
        + current_status.value.center(STATUS_LEN)
        + make_progress_bar(current_progress, max_progress, step_num)
    )
    return res


def handle_entry(url: str, name: str, socketio: SocketIO, callback=None) -> str:
    """
    First all images for the current comic are downloaded, then the script
    takes a best-effort approach to removing all readallcomics.com banners[1] and finally
    the pages are put together in a uniform format and exported as a pdf.

    [1] This is really not mainly to get rid of the credit to the site but to ensure that
        all pages of the comic have a uniform aspect ratio.
    """
    url = url.strip()
    name = name.strip()
    clean_name = name.replace(" ", "_") 
    makedirs(f"imgs/{clean_name}", exist_ok=True)
    base = requests.get(url)
    base.close()
    soup = BS(base.content, "html.parser")
    # pages = soup.find_all("img", {"width": "1000px"})
    pages = soup.select("center center div img")
    num_pages = len(pages) - 1
    page_num = 0
    stored_page_paths = []
    for page in pages:
        socketio.emit('progress', {'progress': page_num / num_pages, 'status': Status.DOWNLOADING.value, 'name': name})
        print(
            make_status_string(
                Status.DOWNLOADING, 0, name, page_num, num_pages
            ),
            end="\r",
        )
        with requests.Session():
            response = requests.get(page["src"])
        fname = f"imgs/{clean_name}/{page_num}.jpg"
        with open(fname, "wb") as page_file:
            page_file.write(response.content)
        stored_page_paths.append(fname)
        page_num += 1
    to_rotate_imgs = []
    images: list[tuple[Image.Image, int]] = []
    for i, path in enumerate(stored_page_paths):
        socketio.emit('progress', {'progress': i / num_pages, 'status': Status.CROPPING.value, 'name': name})
        fname = path
        images.append((img := Image.open(fname), i))
        if img.width > img.height:
            to_rotate_imgs.append(i)
    assert (
        len(images) >= 2
    )  # if (almost) no images are returned something has to be wrong
    height_a = images[1][0].height
    width_a = images[1][0].width
    i = 0
    while (
        i < len(images)
        and ((wdiff := abs(images[i][0].width - width_a)) < 30 or wdiff > 100)
        and ((hdiff := abs(images[i][0].height - height_a)) < 50 or hdiff > 200)
    ):
        i += 1

    if i < len(images):
        if images[i] and width_a == images[i][0].width:  # so the height changed
            height_b = images[i][0].height
            actual_height = min(height_a, height_b)
            banner_height = max(height_a, height_b)
            assert actual_height != banner_height  # please
            crop_count = 0
            for image, indx in images:
                print(
                    make_status_string(Status.CROPPING, 1, name, indx, num_pages),
                    end="\r",
                )
                if image.height == banner_height:
                    crop_count += 1
                    image = image.crop((0, 0, image.width, actual_height))
                    fname = stored_page_paths[indx]
                    image.save(fname)
                image.close()
            if DEBUG:
                print(f"\nCropped {crop_count} images!".ljust(72))
        elif height_a == images[i][0].height:  # so the width changed
            
            width_b = images[i][0].width
            banner_height = 50
            banner_width = min(width_a, width_b)
            crop_count = 0
            for image, indx in images:
                if indx in to_rotate_imgs:
                    continue
                print(
                    make_status_string(Status.CROPPING, 1, name, indx, num_pages),
                    end="\r",
                )
                if image.width == banner_width:
                    crop_count += 1
                    image = image.crop(
                        (0, 0, image.width, image.height - banner_height)
                    )
                    fname = stored_page_paths[indx]
                    image.save(fname)
                image.close()
            if DEBUG:
                print(f"\nCropped {crop_count} images!")
    else:
        for image, _ in images:
            image.close()
        if DEBUG:
            print("Nothing to crop...")

    pdf = FPDF("P", "mm", (PDF_W, PDF_H))
    page_num = 0
    # so far the pages that were landscape oriented
    # had an aspect ratio of 4:3. Doesn't fit the usual page
    # hence the offset to at least keep it centered
    landscape_offset_x = (PDF_H - PDF_W * (4 / 3)) / 2

    for i, stored_path in enumerate(stored_page_paths):
        image = stored_path
        socketio.emit('progress', {'progress': i / num_pages, 'status': Status.ADDING_PAGES.value, 'name': name})
        print(
            make_status_string(Status.ADDING_PAGES, 2, name, i, num_pages),
            end="\r",
        )
        if i in to_rotate_imgs:
            pdf.add_page(orientation="L")
            pdf.image(name=image, x=landscape_offset_x, y=0, h=PDF_W)
        else:
            pdf.add_page()
            pdf.image(name=image, x=0, y=0, h=PDF_H)
        page_num += 1
    print(make_status_string(Status.EXPORTING, 3, name, 0, 1), end="\r")
    socketio.emit('progress', {'progress': 1, 'status': Status.EXPORTING.value, 'name': name})

    print(make_status_string(Status.COMPLETE, 4, name, 1, 1))
    socketio.emit('progress', {'progress': 1, 'status': Status.COMPLETE.value, 'name': name})
    print(f"handle_entry called with url={url}, name={name}")
    pdf_path = f"pdfs/{name}.pdf"
    pdf.output(pdf_path)
    # Log the PDF path
    print(f"handle_entry returning pdf_path={pdf_path}") #for dubugging

    if callback is not None:
        callback(pdf_path)

    return pdf_path


if __name__ == "__main__":
    main()
