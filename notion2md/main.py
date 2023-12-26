import bs4
from bs4 import BeautifulSoup
import pypandoc
import os
import zipfile
import argparse
import shutil


class NotionMdParser:
    def __init__(self, clean_after, target):
        self.actions = {
            "strong": {
                "em": (self.clear_children, "first_child"),
                "strong": (self.clear_children, "tag"),
            },
            "em": {
                "strong": (self.clear_children, "first_child"),
                "em": (self.clear_children, "tag"),
            },
        }
        self.clean_after = clean_after
        self.target = target
        self.html_files = []
        self.tags_to_delete = []
        self.misc_files_to_move = []
        self.input_folder_fp = "notion_html"
        self.out_folder_fp = "output"

    def create_folder(self, folder_fp):
        if not os.path.isdir(folder_fp):
            try:
                os.mkdir(folder_fp)
            except FileExistsError as e:
                print(f"error creating a folder caused by : {e}")

    def clear_children(self, tag):
        children = list(tag.children)
        if len(children) == 0:
            return
        for child in children:
            if child.name == "strong" or child.name == "em":
                self.tags_to_delete.append(child)

    def unzip(self, zip_fp, folder_fp):
        with zipfile.ZipFile(os.path.join(folder_fp, zip_fp), "r") as zip_ref:
            zip_ref.extractall(folder_fp)

        os.remove(os.path.join(folder_fp, zip_fp))

    def get_files(self, cond, folder_fp, files):
        return list(
            map(
                lambda file: os.path.join(folder_fp, file),
                list(filter(cond, files)),
            )
        )

    def gather_files(self, folder_fp):
        """
        Function gatheres all the files to convert and preserves the project structure in the output directory
        """
        files = os.listdir(folder_fp)
        self.html_files.extend(
            self.get_files(lambda x: x.endswith(".html"), folder_fp, files)
        )
        self.misc_files_to_move.extend(
            self.get_files(
                lambda x: (x.split(".")[-1] not in ["md", "html", "zip"]),
                folder_fp,
                files,
            )
        )

        for file in files:
            file_p = os.path.join(folder_fp, file)
            if file.endswith(".zip"):
                self.unzip(file, folder_fp)
                self.gather_files(folder_fp)
            elif os.path.isdir(file_p) and not file.endswith(".zip"):
                folder_fp = file_p
                self.create_folder(
                    os.path.join(
                        self.out_folder_fp, "/".join((folder_fp.split("/"))[1:])
                    )
                )
                self.gather_files(folder_fp)

    def move_misc_files(self):
        for f in self.misc_files_to_move:
            if not os.path.isdir(f):
                source_p = f
                target_p = f.replace(self.input_folder_fp, self.out_folder_fp)
                shutil.move(source_p, target_p)

    def run(self):
        self.create_folder(self.out_folder_fp)
        self.gather_files(self.input_folder_fp)
        self.move_misc_files()
        for html_fp in self.html_files:
            soup = self.parse(html_fp)
            self.cleanup_tags()
            mod_html = self.write_modified_soup(soup, html_fp)
            self.tags_to_delete = []
            self.dump_md(mod_html)

    def fix_links(self, soup):
        # find all hrefs ending with '.html'
        if self.target == "html":
            for a in soup.find_all("a", href=True):
                if a["href"].endswith(".html"):
                    a["href"] = a["href"].replace(".html", ".md")

        return soup

    def write_modified_soup(self, soup, html_fp):
        self.create_folder(self.out_folder_fp)
        mod_html_fp = html_fp.replace(self.input_folder_fp, self.out_folder_fp)
        with open(mod_html_fp, "w") as f:
            f.write(str(soup))
        return mod_html_fp

    def cleanup_tags(self):
        for tag in self.tags_to_delete:
            tag.decompose()

    def is_navstring(self, tag):
        return type(list(tag.children)[0]) == bs4.element.NavigableString

    def parse(self, html_fp):
        soup = BeautifulSoup(open(html_fp), "html.parser")
        soup = self.fix_links(soup)
        for tag in soup.find_all(["strong", "em"]):
            if tag.parent.name not in ["strong", "em"]:
                text = tag.text
                text = text.replace("\n", "")
                text = text.split(" ")
                text = " ".join(text)
                first_child = list(tag.children)[0]

                if self.is_navstring(tag):
                    continue

                action, target = self.actions.get(tag.name, {}).get(
                    first_child.name, (None, None)
                )

                if action and target:
                    tag = locals()[target]
                    action(tag)
                    if not self.is_navstring(tag):
                        tag.append(text)

        return soup

    def dump_md(self, html_fp):
        self.create_folder(self.out_folder_fp)
        out_file_name = html_fp.replace(".html", ".md")
        pypandoc.convert_file(
            html_fp,
            "md",
            outputfile=out_file_name,
            extra_args=[
                "-t",
                "gfm-raw_html",
            ],
        )
        if self.target == "md":
            os.remove(html_fp)
        else:
            os.remove(out_file_name)

    def clean_helper(self, folder_fp):
        if not os.path.isdir(folder_fp):
            return
        for file in os.listdir(folder_fp):
            os.remove(os.path.join(folder_fp, file))

    def clean(self):
        if self.clean_after == "true":
            self.clean_helper(self.input_folder_fp)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="NotionConverter",
        description="Program to clean up the bad conversion of notion to html and md",
        epilog="Contact me on discord @appulsauce for any issues or problems or raise a gh issue",
    )
    parser.add_argument(
        "-ca",
        "--clean-after",
        choices=[
            "true",
            "false",
        ],
        help="Remove the files from notion after fixing the conversion",
        default="false",
    )
    parser.add_argument(
        "-to",
        "--target",
        choices=["md", "html", "both"],
        help="Fix the conversion either to html or markdown or both",
        default="both",
    )

    args = parser.parse_args()
    notion_parser = NotionMdParser(args.clean_after, args.target)
    notion_parser.run()
