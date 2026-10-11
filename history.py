"""Persistent pressure-sample history for the Pico filesystem."""

import os


def _is_missing(error):
    return bool(error.args) and error.args[0] == 2


def load_history(path, max_samples):
    """Load the most recent samples, including a pending compaction file."""
    samples = []
    for candidate in (path, path + ".tmp"):
        try:
            history_file = open(candidate, "r")
        except OSError as error:
            if _is_missing(error):
                continue
            raise

        with history_file:
            for line in history_file:
                line = line.strip()
                if not line:
                    continue
                try:
                    samples.append(float(line))
                except ValueError:
                    print("Ignoring invalid pressure-history entry")
        break

    return samples[-max_samples:]


def append_sample(path, pressure_hpa):
    """Append one pressure sample to the history file."""
    with open(path, "a") as history_file:
        history_file.write("{}\n".format(pressure_hpa))


def save_history(path, samples):
    """Replace the history file safely, retaining samples in a temporary file."""
    temporary_path = path + ".tmp"
    with open(temporary_path, "w") as history_file:
        for sample in samples:
            history_file.write("{}\n".format(sample))

    try:
        os.remove(path)
    except OSError as error:
        if not _is_missing(error):
            raise
    os.rename(temporary_path, path)
