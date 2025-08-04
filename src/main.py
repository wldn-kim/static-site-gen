import os, shutil, sys
from functions import extract_title, markdown_to_html_node

def copy_static_files(src: str, dst: str):
    if os.path.exists(dst):
        shutil.rmtree(dst)
        print(f"Deleted existing directory: {dst}")

    os.mkdir(dst)
    print(f"Created directory: {dst}")

    def recursive_copy(src_path: str, dst_path: str):
        for item in os.listdir(src_path):
            src_item = os.path.join(src_path, item)
            dst_item = os.path.join(dst_path, item)

            if os.path.isfile(src_item):
                shutil.copy(src_item, dst_item)
                print(f"Copied file: {src_item} -> {dst_item}")
            elif os.path.isdir(src_item):
                os.mkdir(dst_item)
                print(f"Created directory: {dst_item}")
                recursive_copy(src_item, dst_item)

    recursive_copy(src, dst)

def generate_page(md_path: str, template_path: str, output_path: str, basepath: str):
    with open(md_path, "r") as f:
        markdown_content = f.read()

    html_node = markdown_to_html_node(markdown_content)
    html_content = html_node.to_html()
    title = extract_title(markdown_content)

    with open(template_path, "r") as f:
        template = f.read()

    page = template.replace("{{ Title }}", title)
    page = page.replace("{{ Content }}", html_content)
    page = page.replace('href="/', f'href="{basepath}')
    page = page.replace('src="/', f'src="{basepath}')

    with open(output_path, "w") as f:
        f.write(page)

def generate_pages_recursive(dir_path_content: str, template_path: str, dest_dir_path: str, basepath: str):
    for root, _, files in os.walk(dir_path_content):
        for file in files:
            if file.endswith(".md"):
                content_md_path = os.path.join(root, file)

                relative_path = os.path.relpath(content_md_path, dir_path_content)
                relative_html_path = os.path.splitext(relative_path)[0] + ".html"
                output_html_path = os.path.join(dest_dir_path, relative_html_path)

                output_dir = os.path.dirname(output_html_path)
                os.makedirs(output_dir, exist_ok=True)

                print(f"Generating page: {content_md_path} -> {output_html_path}")
                generate_page(content_md_path, template_path, output_html_path, basepath)

def main():
    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"
    if not basepath.endswith("/"):
        basepath += "/"

    output_dir = "docs"
    copy_static_files("static", output_dir)
    generate_pages_recursive("content", "template.html", output_dir, basepath)

if __name__ == "__main__":
    main()