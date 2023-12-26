<img src="assets/icon.png" alt="isolated" width="400" style="max-width: 100%"/>

# Notion to md/html converter

This project is a tool for converting Notion pages to Markdown files. A better project than this already exists [here](https://github.com/souvikinator/notion-to-md) and probably in other places so if you want the highest quality conversion thats probably better.

**Note** : This still has some bugs but should work for most basic markdown stuff, but expect certain stuff to be buggy.

Since Notion for some reason emits some slightly messed up html/md this tool just fixes the outputs, and gives you either the corrected html files or the cleaned up markdown, see `--help` for details.

## Project Structure

- `notion_html/`: Directory for the Notion HTML files to be fixed.
- `output_md/`: Directory for the fixed converted files

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
poetry run python notion2md/main.py --help
```


### commands summary
| **command** | **description**                                                                  | **options**   | **default** |
|-------------|----------------------------------------------------------------------------------|---------------|-------------|
| `-ca`       | Remove the files you put in the conversion folder after everything is cleaned up | {true, false} | false       |
| `-to`       | Choose to either just get the corrected html files or get the markdown files     | {md, html}    | md          |

## What is different here ? 

This approach doesn't make use of the Notion API directly, I just parse the html notion emits, fix any oddities and then let pandoc to the actual conversion. Probably not the best approach but it minimizes unecessary code by just fixing what actually needs to be fixed.