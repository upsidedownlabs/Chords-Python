
import os
from typing import Optional
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "scripts"))
import scrape_module

root_dir = '.'

def scrape_lib_folder(lib_dir:str, search_path: Optional[str] = None, output_dir: Optional[str] = None):
    for directory, subdirectories, files in os.walk(lib_dir):
        path = directory.split(os.sep)
        rel_output = os.path.relpath(directory, lib_dir)
        rel_output_dir = os.path.join(output_dir or root_dir, rel_output)
        for file in files:
            if file.endswith(".pyd"):
                out_dir = os.path.abspath(rel_output_dir)
                os.makedirs(out_dir, exist_ok = True)

                first_part_pyd = file.split('.')[0]
                module_name = '.'.join(rel_output_dir.split(os.sep)) + '.' + first_part_pyd if lib_dir != search_path else first_part_pyd

                collect_module(module_name, file, search_path , rel_output_dir)

            

def collect_module(module_name: str, file_pyd:str, search_path = None, output_dir: str = ""):
    first_part_pyd = file_pyd.split('.')[0]
    pyi_filename: str = output_dir + '\\' + first_part_pyd + '.pyi'

    if(not pyi_filename.endswith('tests.pyi')):
        try:
            state = scrape_module.ScrapeState(module_name, search_path)

            with open(pyi_filename, mode='w', encoding="utf-8") as file_object:
                state.collect_top_level_members()
                state.members[:] = [m for m in state.members if m.name not in scrape_module.keyword.kwlist]
                state.collect_second_level_members()
                state.dump(file_object)
        except Exception as e:
            print(f"scrap failed for {module_name} with {e}")

def main():
    lib_dir = sys.argv[1] if len(sys.argv) > 1 else u"."
    search_path = sys.argv[2] if len(sys.argv) > 2 else None
    output_dir = sys.argv[3] if len(sys.argv) > 3 else None
  
    abs_lib_dir = os.path.abspath(lib_dir)

    if search_path is None:
        search_path = os.path.dirname(abs_lib_dir)

    if os.path.exists(abs_lib_dir):
        scrape_lib_folder(abs_lib_dir, search_path, output_dir)
    else:
        print("directory doesn't exists " + abs_lib_dir)

if __name__ == "__main__":
    main()
