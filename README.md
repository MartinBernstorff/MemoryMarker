<a href="https://github.com/martinbernstorff/memorymarker"><img src="https://github.com/martinbernstorff/memorymarker/blob/main/docs/_static/icon.png?raw=true" width="100" align="right"/></a>

# memorymarker

<!-- start short-description -->

Highlighting does not aid memory. Questions do. But they take time. MemoryMarker turns your highlights into questions, so you can maintain traction at speed.

Specifically, it takes highlights from [Omnivore](https://www.omnivore.app/) and turns them into markdown questions.

To supercharge this, you can even ingest these questions into [Anki](https://apps.ankiweb.net/) using [Memium](https://github.com/MartinBernstorff/Memium).

<!-- end short-description -->

## Setup

A Docker image for Omnivore is continuously built and pushed to [ghcr.io/martinbernstorff/memorymarker](https://github.com/martinbernstorff/memorymarker/pkgs/container/memorymarker).

1. Install [Docker](https://docs.docker.com/get-docker/) or [Orbstack](https://orbstack.dev/)

2. Update the api keys in the compose file and run the container:

```bash
docker compose up -d
```

You can install `memorymarker` via [pip] from [PyPI]:

```bash
pip install memorymarker
```

[pip]: https://pip.pypa.io/en/stable/installing/
[PyPI]: https://pypi.org/project/memorymarker/

## Usage

TODO: Add minimal usage example

To see more examples, see the [documentation].

# 📖 Documentation

| Documentation          |                                                          |
| ---------------------- | -------------------------------------------------------- |
| 🔧 **[Installation]**  | Installation instructions on how to install this package |
| 📖 **[Documentation]** | A minimal and developing documentation                   |
| 👩‍💻 **[Tutorials]**     | Tutorials for using this package                         |
| 🎛️ **[API Reference]** | API reference for this package                           |
| 📚 **[FAQ]**           | Frequently asked questions                               |

# 💬 Where to ask questions

| Type                            |                        |
| ------------------------------- | ---------------------- |
| 📚 **FAQ**                      | [FAQ]                  |
| 🚨 **Bug Reports**              | [GitHub Issue Tracker] |
| 🎁 **Feature Requests & Ideas** | [GitHub Issue Tracker] |
| 👩‍💻 **Usage Questions**          | [GitHub Discussions]   |
| 🗯 **General Discussion**        | [GitHub Discussions]   |

[Documentation]: https://martinbernstorff.github.io/memorymarker/index.html
[Installation]: https://martinbernstorff.github.io/memorymarker/installation.html
[Tutorials]: https://martinbernstorff.github.io/memorymarker/tutorials.html
[API Reference]: https://martinbernstorff.github.io/memorymarker/references.html
[FAQ]: https://martinbernstorff.github.io/memorymarker/faq.html
[github issue tracker]: https://github.com/martinbernstorff/memorymarker/issues
[github discussions]: https://github.com/martinbernstorff/memorymarker/discussions
