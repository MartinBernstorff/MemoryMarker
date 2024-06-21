# ✏️ MemoryMarker

<!-- start short-description -->

Highlighting does not aid memory. Questions do. But they take time. MemoryMarker turns your highlights into questions, so you can maintain traction at speed.

Specifically, it takes highlights from [Omnivore](https://www.omnivore.app/) and writes them as question/answer pairs to markdown files.

<!-- end short-description -->

---

> <HIGHLIGHT>If we wanted to delete a node with two children, say, `6`, we replace the node with its **in-order successor.**</HIGHLIGHT>

> <HIGHLIGHT>If the given tree is a balanced binary tree, the height will be in log nlog\\ n, for reasons that are very similar to what we discussed in merge sort. However, it is a possibility that in the worst case, the tree provided is either left-skewed or right-skewed. In that case, the height of the tree will be in O(n) and the total work done for all the operations described above is O(n).</HIGHLIGHT>

---

> Q. When deleting a node with two children from a [[Min-heap]], what should replace the node?

> A. The in-order successor; i.e. the node with the smallest value which is greater than the deleted node. For a binary tree, that is the smallest value in the deleted node's right subtree.

---

To supercharge this and remember the answers, you can ingest these questions into [Anki](https://apps.ankiweb.net/) using [Memium](https://github.com/MartinBernstorff/Memium).

## Setup

1. Install [Docker](https://docs.docker.com/get-docker/) or [Orbstack](https://orbstack.dev/)

2. Copy the `.env.sample` file to `.env` and update the api keys

3. Copy the `compose.sample.yml` file to `compose.yml` and update the output directory

4. Run the container:

```bash
docker compose up
```

## Contributing

1. We use [`rye`](https://rye.astral.sh/) for environment management. Once it is installed, set up your virtual environment using `rye sync`.

2. Make your changes.

3. Update the `.env` file with your API keys so you can run tests, or run them on CI only.

4. When ready to lint, test, see the `makefile` for commands. 

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
