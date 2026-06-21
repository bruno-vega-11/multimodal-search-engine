# src/build_dictionary.py

import json


def build_dictionary(
    index_file,
    dictionary_file
):

    dictionary = {}

    with open(
        index_file,
        "r",
        encoding="utf-8"
    ) as f:

        while True:

            offset = f.tell()

            line = f.readline()

            if not line:
                break

            record = json.loads(
                line
            )

            term = record["term"]

            dictionary[
                term
            ] = offset

    with open(
        dictionary_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            dictionary,
            f
        )

    print()

    print(
        f"Terms indexed: "
        f"{len(dictionary)}"
    )

    print(
        f"Dictionary saved: "
        f"{dictionary_file}"
    )


if __name__ == "__main__":

    build_dictionary(

        index_file=
        "data/index/final_index.idx",

        dictionary_file=
        "data/index/dictionary.json"

    )