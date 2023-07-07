"""
Utilities to process obsidian notes and convert them to hugo ready content files.
"""

import os
from shutil import rmtree, copytree, ignore_patterns, copyfile
from .wiki_links_processor import replace_wiki_links
from .md_mark_processor import replace_md_marks
from.highlights_processor import remove_highlights
from pathlib import Path


class ObsidianToHugo:
    """
    Process the obsidian vault and convert it to hugo ready content.
    """

    def __init__(
        self,
        obsidian_vault_dir: str,
        hugo_content_dir: str,
        processors: list = None,
        filters: list = None,
        copy_exclusions: list = None,
        direct_copies: list = None,
    ) -> None:
        self.obsidian_vault_dir = obsidian_vault_dir
        self.hugo_content_dir = hugo_content_dir
        self.processors = [replace_wiki_links, replace_md_marks, remove_highlights]
        self.filters = []
        self.copy_exclusions = []
        self.direct_copies = []
        if processors:
            self.processors.extend(processors)
        if filters:
            self.filters.extend(filters)
        if copy_exclusions:
            self.copy_exclusions.extend(copy_exclusions)
        if direct_copies:
            self.direct_copies.extend(direct_copies)

    def run(self) -> None:
        """
        Delete the hugo content directory and copy the obsidian vault to the
        hugo content directory, then process the content so that the wiki links
        are replaced with the hugo links.
        """
        self.clear_hugo_content_dir()
        self.copy_obsidian_vault_to_hugo_content_dir()
        self.dump_to_writing()
        self.process_content()

    def clear_hugo_content_dir(self) -> None:
        """
        Delete directories within the hugo content directory
        """
        for dir in self.direct_copies:
            rmtree(self.hugo_content_dir / dir.name)

        rmtree(self.hugo_content_dir / "writing")

    def copy_obsidian_vault_to_hugo_content_dir(self) -> None:
        """
        Copy directories from the obsidian vault to the hugo content directory, as is
        """

        for dir in self.direct_copies:
            copytree(self.obsidian_vault_dir / dir, self.hugo_content_dir / dir.name)

    def dump_to_writing(self) -> None:
        """
        Flatten the whole obsidian directory and copy it into the hugo content/writing directory using page bundles as necessary
        """
        os.mkdir(self.hugo_content_dir / "writing")

        exclude = set(self.copy_exclusions)

        all_files = []
        for root, dirs, files in os.walk(self.obsidian_vault_dir):
            dirs[:] = [d for d in dirs if d not in exclude]

            if dirs:
                for file_name in files:
                    all_files.append(os.path.join(root, file_name))
            elif "_index.md" in files: # branch bundle with no leaves
                all_files.append(os.path.join(root, file_name))
            elif "index.md" in files: # leaf bundle
                all_files.append(root)
            else: # leaf bundle without markdown
                continue

        for file_name in all_files:
            file_name = Path(file_name)
            try:
                copyfile(file_name, self.hugo_content_dir / "writing" / file_name.name)
            except IsADirectoryError:
                copytree(file_name, self.hugo_content_dir / "writing" / file_name.name)
            except:
                raise

    def process_content(self) -> None:
        """
        Looping through all files in the hugo content directory and replace the
        wiki links of each matching file.
        """

        for root, dirs, files in os.walk(self.hugo_content_dir):
            if dirs: # not a leaf bundle
                for file in files:
                    if file.endswith(".md"): # CASE: normal notes
                        with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                            content = f.read()
                        # If the file matches any of the filters, delete it.
                        keep_file = True
                        for filter in self.filters:
                            if not filter(content, file):
                                os.remove(os.path.join(root, file))
                                keep_file = False
                                break
                        if not keep_file:
                            continue
                        for processor in self.processors:
                            content = processor(content)
                        with open(os.path.join(root, file), "w", encoding="utf-8") as f:
                            f.write(content)
                    else: # delete other file types not in a leaf bundle
                        os.remove(os.path.join(root, file))
            elif "_index.md" in files: # branch bundle with no leaves
                for file in files:
                    if file.endswith(".md"):
                        with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                            content = f.read()
                        # If the file matches any of the filters, delete it.
                        keep_file = True
                        for filter in self.filters:
                            if not filter(content, file):
                                os.remove(os.path.join(root, file))
                                keep_file = False
                                break
                        if not keep_file:
                            continue
                        for processor in self.processors:
                            content = processor(content)
                        with open(os.path.join(root, file), "w", encoding="utf-8") as f:
                            f.write(content)
            else: # leaf bundle
                for file in files:
                    if file.endswith(".md"): # index file
                        with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                            content = f.read()
                        # If the file matches any of the filters, delete it.
                        keep_file = True
                        for filter in self.filters:
                            if not filter(content, file):
                                rmtree(root) # delete whole leaf bundle
                                keep_file = False
                                break
                        if not keep_file:
                            break
                        for processor in self.processors:
                            content = processor(content)
                        with open(os.path.join(root, file), "w", encoding="utf-8") as f:
                            f.write(content)
