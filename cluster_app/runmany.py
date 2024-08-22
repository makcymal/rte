import subprocess
import randomname as rn
from random import choice


if __name__ == "__main__":
    sensors = []
    N = 50

    batches = [
        rn.get_name(adj=("size", "materials"), noun=("infrastructure",))
        for i in range(5)
    ]
    labels = [
        rn.get_name(
            noun=(
                "astronomy",
                "minerals",
                "ghosts",
                "music_instruments",
                "water",
            ),
        )
        for i in range(N)
    ]

    with open("runmany.log", "w") as log:
        for i in range(N):
            batch = choice(batches)
            label = labels[i]
            sp = subprocess.Popen(["python run.py", batch, label], shell=True)
            print(f"{batch}!{label} is running with pid {sp.pid}", file=log)
