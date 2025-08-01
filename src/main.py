import os
import shutil
from functions import generate_page

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

def main():
    copy_static_files("static", "public")
    generate_page("content/index.md", "template.html", "public/index.html")

if __name__ == "__main__":
    main()