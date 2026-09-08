from pathlib import Path
import logging

import pandas as pd


# Project directories
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
LOG_DIR = BASE_DIR / "logs"


# Create logs directory if it doesn't exist
LOG_DIR.mkdir(exist_ok=True)


# Configure logging
logging.basicConfig(
    filename=LOG_DIR / "extract.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


def extract_data():
    """
    Read all CSV files from the raw data directory.
    """

    if not RAW_DATA_DIR.exists():
        logger.error("Raw data directory not found: %s", RAW_DATA_DIR)
        raise FileNotFoundError(
            f"Raw data directory not found: {RAW_DATA_DIR}"
        )

    csv_files = list(RAW_DATA_DIR.glob("*.csv"))

    if not csv_files:
        logger.error("No CSV files found in %s", RAW_DATA_DIR)
        raise FileNotFoundError(
            f"No CSV files found in {RAW_DATA_DIR}"
        )

    data = {}

    for file in csv_files:
        try:
            df = pd.read_csv(file)
            data[file.stem] = df

            logger.info(
                "Extracted %s | rows=%s | columns=%s",
                file.name,
                len(df),
                len(df.columns)
            )

            print(
                f"Extracted: {file.name} | "
                f"Rows: {len(df)} | "
                f"Columns: {len(df.columns)}"
            )

        except Exception as error:
            logger.error(
                "Failed to read %s | error=%s",
                file.name,
                error
            )

            print(f"Failed to read {file.name}: {error}")

    return data


if __name__ == "__main__":
    extracted_data = extract_data()

    logger.info(
        "Extraction completed | files=%s",
        len(extracted_data)
    )

    print("\nExtraction completed.")
    print(f"Successfully extracted {len(extracted_data)} files.")