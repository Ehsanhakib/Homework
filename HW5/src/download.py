"""Part 1: download the raw file once. Never overwrite it."""
import ssl
import sys
from pathlib import Path
from urllib.request import urlopen
import pandas as pd

# Copy the link to AmesHousing.txt from the JSE article page (De Cock, 2011).
# Record the same URL and today's date in README.md.
DATA_URL = "https://jse.amstat.org/v19n3/decock/AmesHousing.txt"
EXPECTED_SHAPE = (2930, 82)


def main(dest: str) -> None:
    path = Path(dest)
    if path.exists():
        print(f"{path} exists; raw data is never overwritten.")
        return
    if not DATA_URL:
        sys.exit("Set DATA_URL in src/download.py first.")
    path.parent.mkdir(parents=True, exist_ok=True)

    ctx = ssl._create_unverified_context()
    with urlopen(DATA_URL, context=ctx) as response:
        path.write_bytes(response.read())

    df = pd.read_csv(path, sep="\t", keep_default_na=False)
    if df.shape != EXPECTED_SHAPE:
        sys.exit(f"Expected shape {EXPECTED_SHAPE}, got {df.shape}")
    print(f"Downloaded {path} ({df.shape[0]:,} rows, {df.shape[1]} columns)")


if __name__ == "__main__":
    main(sys.argv[1])
