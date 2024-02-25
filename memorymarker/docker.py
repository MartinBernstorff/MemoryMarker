from pathlib import Path

import typer

from memorymarker.main import main

app = typer.Typer(no_args_is_help=True)


@app.command()
def docker(
    output_dir: Path = typer.Argument(  # noqa: B008
        Path("/output"),
        help="Directory to save the questions to",
        file_okay=False,
        dir_okay=True,
        writable=True,
    ),
    max_n: int = 100,
    only_new: bool = True,
    select: bool = False,
) -> None:
    main(output_dir=output_dir, max_n=max_n, only_new=only_new, select=select)


if __name__ == "__main__":
    app()
