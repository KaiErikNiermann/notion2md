import bs4
from bs4 import BeautifulSoup
import pypandoc
import os

class NotionMdParser:
    def __init__(self):
        self.actions = {
            'strong': {
                'em': (self.clear_children, 'first_child'),
                'strong': (self.clear_children, 'tag')
            },
            'em': {
                'strong': (self.clear_children, 'first_child'),
                'em': (self.clear_children, 'tag')
            }
        }
        self.html_files = []
        self.input_folder_fp = 'notion_html'
        self.out_md_folder_fp = 'output_md'
        self.out_html_folder_fp = 'output_html'   
        self.tags_to_delete = []
    
    def create_folder(self, folder_fp):
        if not os.path.isdir(folder_fp):
            try: 
                os.mkdir(folder_fp)
            except OSError as error: 
                print(f"Error creating folder: {error}")
                return
    
    def clear_children(self, tag):
        children = list(tag.children)
        if len(children) == 0:
            return
        for child in children:
            if child.name == 'strong' or child.name == 'em':
                print(f"Deleting {child.name} tag")
                self.tags_to_delete.append(child)
        
    def gather_files(self):
        self.create_folder(self.input_folder_fp)
        for file in os.listdir(self.input_folder_fp):
            if file.endswith(".html"):
                self.html_files.append(os.path.join(self.input_folder_fp, file))
    
    def run(self):
        self.gather_files()
        for html_fp in self.html_files:
            soup = self.parse(html_fp)
            self.cleanup_tags()
            mod_html = self.write_modified_soup(soup, html_fp)
            self.tags_to_delete = []
            self.dump_md(mod_html)
            
    def write_modified_soup(self, soup, html_fp):
        self.create_folder(self.out_md_folder_fp)
        mod_html_fp = html_fp.replace(self.input_folder_fp, self.out_md_folder_fp)
        with open(mod_html_fp, 'w') as f:
            f.write(str(soup))
        return mod_html_fp
    
    def cleanup_tags(self):
        for tag in self.tags_to_delete:
            tag.decompose()
    
    def parse(self, html_fp):
        soup = BeautifulSoup(open(html_fp), "html.parser")
        for tag in soup.find_all(['strong', 'em']):
            if tag.parent.name not in ['strong', 'em']:
                text = tag.text 
                text = text.replace('\n', '')
                text = text.split(' ')
                text = ' '.join(text)
                first_child = list(tag.children)[0]
                
                if len(list(first_child.children)) == 0:
                    continue;
 
                action, target = self.actions.get(tag.name, {}).get(first_child.name, (None, None))

                if action and target:
                    action(locals()[target])
                    if type(list(locals()[target].children)[0]) != bs4.element.NavigableString:
                        locals()[target].append(text)
        return soup
                    
    def dump_md(self, html_fp):
        self.create_folder(self.out_md_folder_fp)
        out_file_name = html_fp.replace('.html', '.md')
        pypandoc.convert_file(html_fp, 'md', outputfile=out_file_name, extra_args=['-t', 'gfm-raw_html'])    
        self.create_folder(self.out_html_folder_fp)
        html_fp.replace(self.input_folder_fp, self.out_html_folder_fp)
        os.remove(html_fp)
        
    def clean_helper(self, folder_fp, end):
        if not os.path.isdir(folder_fp):
            return
        for file in os.listdir(folder_fp): 
            if file.endswith(end):
                os.remove(os.path.join(folder_fp, file))
        
    def clean(self): 
        self.clean_helper(self.input_folder_fp, '.html')
        self.clean_helper(self.out_md_folder_fp, '.md')
        self.clean_helper(self.out_html_folder_fp, '.html')
        
if __name__ == '__main__':
    parser = NotionMdParser()
    parser.run()