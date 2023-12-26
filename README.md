<img src="assets/icon.png" alt="isolated" width="400"/>

# Correct Notion to md/html Converter

This project is a tool for converting Notion pages to Markdown files. Since Notion for some reason adds an excessive number of `strong` and `em` tags this tool just removes them and then converts the html doc to markdown and preserves the fixed html copy.

## Project Structure

- `notion_html/`: Directory for the Notion HTML files to be fixed.
- `output_md/`: Directory for fixed markdown files.
- `output_html/`: Directory for fixed html files.

## Setup

1. Clone the repository.
2. Install [Poetry](https://python-poetry.org/docs/#installation) if you haven't already.
3. Install the project dependencies with Poetry:

```sh
poetry install
```

## Usage
1. Place the html files you want to fix into the `notion_html/` folder, you can also just put in the zip when you export.

2. Run the following command

```sh
poetry run python notion2md/main.py
```
