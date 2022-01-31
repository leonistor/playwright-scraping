import json
import time
from urllib.request import Request, urlopen


def write_genre(file_name):
    """Write radom genre from binaryjazz.us to given file."""
    req = Request(
        "https://binaryjazz.us/wp-json/genrenator/v1/genre/",
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"
        },
    )
    genre = json.load(urlopen(req))

    with open(file_name, "w") as new_file:
        print(f"Writing '{genre}' to '{file_name}'...")
        new_file.write(genre)
    # -


if __name__ == "__main__":

    print("starting...")
    start = time.time()

    for i in range(5):
        write_genre(f"./output/tutorials/sync_new_file{i}.txt")

    end = time.time()
    print(f"Time to complete sync read/writes: {round(end-start, 2)} seconds")
