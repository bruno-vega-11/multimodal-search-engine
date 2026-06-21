def split_song_into_chunks(song_text):

    paragraphs = []

    current = []

    for line in song_text.splitlines():

        line = line.strip()

        if line == "":

            if current:

                paragraphs.append(
                    " ".join(current)
                )

                current = []

        else:

            current.append(line)

    if current:

        paragraphs.append(
            " ".join(current)
        )

    return paragraphs