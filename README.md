# Obsidian Vault to Hugo Content

Lightweight, extensible, zero-dependency CLI written in Python to help us publish [Obsidian](https://obsidian.md) notes with [Hugo](https://gohugo.io). 

## Description

My Obsidian vault and my Hugo site are two completely different systems with wildly different directory structures. I do all of my writing in Obsidian and simply use Hugo as a place to publish that writing. As such, I wanted a tool that updated my Hugo content that is driven entirely by changes made in my Obsidian vault.

This tool directly copies specified directories into Hugo `content` folder, maintaining the directory structure in the process. It flattens the rest of the vault and dumps into a `content/writing` directory all while maintaining leaf bundles.

### Features

- Clears Hugo content directory
- Copies Obsidian vault contents into Hugo content directory
- Maintains folder structure for directories you specify
- Flattens and dumps all other notes to `content/writing`
- Maintains all notes as Hugo leaf bundles
- Deletes all file types except for `md` files and images that are within a leaf bundle
- Replaces Obsidian wiki links (`[[wikilink]]`) with Hugo shortcode links
  (`[wikilink]({{< ref "wikilink" >}})`)
- Replaces Obsidian image wiki links (`![[some_image.jpg]]`) with Hugo shortcode links (`{{< image some_image.jpg \>}}`)
- Replaces obsidian marks (`==important==`) with HTML marks (`<mark>important</mark>`)
- Removes imported Kindle highlights under any `## Highlights` header
- Want to do more? You can write and register custom [filters](#filters) to dynamically
  include/exclude content from processing and [processors](#processors) to do whatever
  you want with the file contents.

### Processing Examples

| Obsidian | Hugo
| -------- | -------- 
| `[[/some/wiki/link]]` | `[/some/wiki/link]({{< ref "/some/wiki/link" >}})`
| `[[/some/wiki/link\|Some text]]` | `[Some text]({{< ref "/some/wiki/link" >}})`
| `[[/some/wiki/link/_index]]` | `[/some/wiki/link/]({{< ref "/some/wiki/link/" >}})`
| `[[/some/wiki/link#Some Heading\|Some Heading Link]]` | `[Some Heading Link]({{< ref "/some/wiki/link#some-heading" >}})`
| `==foo bar===` | `<mark>foo bar</mark>`
| `![[some_image.jpg]]` | `![](some_image.jpg)`
| `![[some_image.jpg\|692]]` | `{{< image some_image.jpg Resize "692x" \>}}`


> **Note**
> For now, there is *no way to escape* obsidian wiki links. Every link
> will be replaced with a hugo link. The only way to get around this is changing
> the wiki link to don't match the exact sytax, for example by adding an
> [invisible space](https://en.wikipedia.org/wiki/Zero-width_space) (Obsidian will highlight the invisible character as a red dot).
> ![](https://raw.githubusercontent.com/devidw/obsidian-to-hugo/master/img/do-not-do-that.png)
> However, this still is really really *not* best
> practice, so if anyone wants to implement real escaping, [please do
> so](https://github.com/devidw/obsidian-to-hugo/pulls).

### Obsidian Requirements

Obsidian structure must follow [Hugo leaf bundle](https://gohugo.io/content-management/page-bundles/#leaf-bundles) structure. If a note contains images, put the note and all images in the same folder **with the note being named index.md** to maintain leaf bundles and associated images.

## Installation

For now, clone the project and install locally.

```console
git clone https://github.com/Westley-Winks/obsidian-to-hugo.git

cd obsidian-to-hugo

make install_locally
```

## Usage

```console
usage: __main__.py [-h] [--version] [--hugo-content-dir HUGO_CONTENT_DIR]
                   [--obsidian-vault-dir OBSIDIAN_VAULT_DIR]

options:
  -h, --help            show this help message and exit
  --version, -v         Show the version and exit.
  --hugo-content-dir HUGO_CONTENT_DIR
                        Directory of your Hugo content directory, the obsidian notes
                        should be processed into.
  --obsidian-vault-dir OBSIDIAN_VAULT_DIR
                        Directory of the Obsidian vault, the notes should be processed
                        from.
```

### Python API

This file goes in your Hugo site in `scripts`.

```python
from obsidian_to_hugo import ObsidianToHugo

obsidian_to_hugo = ObsidianToHugo(
    obsidian_vault_dir="path/to/obsidian/vault",
    hugo_content_dir="path/to/hugo/content",
)

obsidian_to_hugo.run()
```

#### Filters

You can pass an optional `filters` argument to the `ObsidianToHugo`
constructor. This argument should be a list of functions.

The function will be invoked for each file from the obsidian vault that is
copied into the hugo content directory.

Inside the function, you have access to the file path and the file contents.

When the function returns `False`, the file will be skipped and not copied
into the hugo content directory.

```python
from obsidian_to_hugo import ObsidianToHugo

def filter_file(file_contents: str, file_path: str) -> bool:
    # do something with the file path and contents
    if your_condition:
        return True # copy file
    else:
        return False # skip file

obsidian_to_hugo = ObsidianToHugo(
    obsidian_vault_dir="path/to/obsidian/vault",
    hugo_content_dir="path/to/hugo/content",
    filters=[filter_file],
)

obsidian_to_hugo.run()
```

#### Processors

You can pass an optional `processors` argument to the `ObsidianToHugo`
constructor. This argument should be a list of functions.

The function will be invoked for each file from the obsidian vault that is
copied into the hugo content directory. It will be passed the file contents
as string, and should return the processed version of the file contents.

Custom processors are invoked after the default processing of the file contents.

```python
from obsidian_to_hugo import ObsidianToHugo

def process_file(file_contents: str) -> str:
    # do something with the file contents
    return file_contents

obsidian_to_hugo = ObsidianToHugo(
    obsidian_vault_dir="path/to/obsidian/vault",
    hugo_content_dir="path/to/hugo/content",
    processors=[process_file],
)

obsidian_to_hugo.run()
```

#### Direct copies

For the directories that you want to copy the exact structure of and put into `content` as is, add the `direct_copies` argument to the `ObsidianToHugo` constructor. This should be a list of paths to the directories in your obsidian vault.

This will put the same structure into a directory of the same name in `content` in your Hugo site.

```python
from obsidian_to_hugo import ObsidianToHugo

obsidian_to_hugo = ObsidianToHugo(
    obsidian_vault_dir="path/to/obsidian/vault",
    hugo_content_dir="path/to/hugo/content",
    direct_copies = ["path/to/direct/copy/folder"]
)

obsidian_to_hugo.run()
```

#### Exclusions

For the sensitive directories that you don't want `obsidian-to-hugo` to look at, add the `copy_exclusions` argument to the `ObsidianToHugo` constructor. This should be a list of directory names. `obsidian-to-hugo` will skip these entirely during the copy step.

```python
from obsidian_to_hugo import ObsidianToHugo

obsidian_to_hugo = ObsidianToHugo(
    obsidian_vault_dir="path/to/obsidian/vault",
    hugo_content_dir="path/to/hugo/content",
    copy_exclusions = ["folders", "to", "skip"]
)

obsidian_to_hugo.run()
```

## Contributing

This project is geared to my own specific use case and I kind of built it just for me. However, if you have some ideas to make it more robust and generally useful please submit a pull request.

## Authors and Acknowledgment

This is a direct fork from [David Wolf's obsidian-to-hugo project](https://github.com/devidw/obsidian-to-hugo). Huge thank you to them for doing most of the work. Check out their [really cool website](https://david.wolf.gdn/) while you are at it.
