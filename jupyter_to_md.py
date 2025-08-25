import os
from multiprocessing import Pool, cpu_count
import nbformat
from nbconvert import MarkdownExporter
from nbconvert.preprocessors import Preprocessor
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
import shutil
import re

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

class HTMLTableToMarkdown(Preprocessor):
    """
    Convert HTML tables in notebook outputs to clean Markdown tables.
    """

    def _clean_df(self, df: pd.DataFrame) -> pd.DataFrame:
        # Flatten MultiIndex columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [
                " ".join([str(c) for c in col if "Unnamed" not in str(c)]).strip()
                if any("Unnamed" not in str(c) for c in col)
                else f"" 
                for i, col in enumerate(df.columns)
            ]
        else:
            # Replace unnamed columns
            df.columns = [
                col if "Unnamed" not in str(col) else f"" 
                for i, col in enumerate(df.columns)
            ]
        return df

    def preprocess_cell(self, cell, resources, index):
        if cell.cell_type == 'code':
            new_outputs = []
            for output in cell.get('outputs', []):
                if output.output_type in ('display_data', 'execute_result'):
                    if 'text/html' in output.data:
                        html = output.data['text/html']
                        soup = BeautifulSoup(html, 'html.parser')
                        tables = soup.find_all('table')
                        if tables:
                            md_tables = []
                            for table in tables:
                                df = pd.read_html(StringIO(str(table)))[0]
                                df = self._clean_df(df)
                                md_tables.append(df.to_markdown(index=False))
                            # Replace HTML with Markdown
                            output.data['text/markdown'] = "\n\n".join(md_tables)
                            del output.data['text/html']
                new_outputs.append(output)
            cell['outputs'] = new_outputs
        return cell, resources

def convert_notebook(ipynb_path):
    try:
        nb = nbformat.read(ipynb_path, as_version=4)

        # Get notebook name without extension
        notebook_name = os.path.splitext(os.path.basename(ipynb_path))[0]
        output_dir = os.path.dirname(ipynb_path)
        
        # Create folder with notebook name (no _files suffix)
        notebook_folder = os.path.join(output_dir, notebook_name)
        os.makedirs(notebook_folder, exist_ok=True)
        
        # Create media subfolder
        media_folder = os.path.join(notebook_folder, "media")
        os.makedirs(media_folder, exist_ok=True)

        exporter = MarkdownExporter()
        exporter.register_preprocessor(HTMLTableToMarkdown, enabled=True)

        # Disable embedding images as base64
        exporter.embed_images = False
        
        # Configure the exporter to extract images
        resources = {
            "output_files_dir": "media",  # This will be the subfolder for images
            "unique_key": notebook_name,
            "output_directory": notebook_folder  # Output to the notebook folder
        }

        body, resources = exporter.from_notebook_node(nb, resources=resources)
        
        # Save extracted images
        for filename, data in resources.get('outputs', {}).items():
            filepath = os.path.join(notebook_folder, filename)
            with open(filepath, 'wb') as f:
                f.write(data)

        # Write markdown to the notebook folder
        md_filename = f"{notebook_name}.md"
        md_path = os.path.join(notebook_folder, md_filename)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(body)

        # Update references in the markdown file to use relative paths
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Fix image references to use relative paths from the markdown file
        # The images are in the "media" subfolder, so we need to update paths
        content = re.sub(r'!\[(.*?)\]\(([^)]+)\)', 
                         lambda m: f'![{m.group(1)}](media/{os.path.basename(m.group(2))})', 
                         content)
        
        # Replace more than 2 contiguous newlines with exactly 2 newlines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Write the updated content back
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Remove the original markdown file if it exists in the parent directory
        original_md_path = os.path.splitext(ipynb_path)[0] + ".md"
        if os.path.exists(original_md_path):
            os.remove(original_md_path)

        print(f"Converted: {ipynb_path} -> {md_path}")

    except Exception as e:
        print(f"Failed to convert {ipynb_path}: {e}")
        import traceback
        traceback.print_exc()

def find_notebooks(root_dir):
    notebooks = []
    for dirpath, _, filenames in os.walk(root_dir):
        for f in filenames:
            if f.endswith(".ipynb"):
                # Skip checkpoints files
                if ".ipynb_checkpoints" not in dirpath:
                    notebooks.append(os.path.join(dirpath, f))
    return notebooks

def main():
    notebooks = find_notebooks(ROOT_DIR)
    print(f"Found {len(notebooks)} notebooks.")

    # Process notebooks sequentially for better error handling
    # If you want parallel processing, change this back to use Pool
    for notebook in notebooks:
        convert_notebook(notebook)
    
    # If you prefer parallel processing, uncomment the following lines:
    # with Pool(cpu_count()) as pool:
    #     pool.map(convert_notebook, notebooks)

if __name__ == "__main__":
    main()