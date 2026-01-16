import os
import zipfile
from pathlib import Path
import keyring
from arcgis.gis import GIS
import row.usr.constants as c


BASE_DIR = Path(c.CODE_BASE)
BASE_DIR_FILES = ['constants.py']

agol_code_sample_item_id = '697ebae936b74c0294a28f8a9beaac5b'


output_path = r'C:\ROW\temp\test.zip'

with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:

    # Write base selected base directory files to zip
    for file in BASE_DIR_FILES:
        file_path =  Path(BASE_DIR) / 'row' / file 
        archive_file_path = file_path.relative_to(BASE_DIR)
        zipf.write(file_path, archive_file_path)

    # Write notebook directory and all files below it to the zip file
    subdir_path = os.path.join(BASE_DIR, 'row', 'notebook')
    for root, _, files in os.walk(subdir_path):
        for file in files:
            file_path = Path(root) / file
            archive_file_path = file_path.relative_to(BASE_DIR)
            zipf.write(file_path, archive_file_path)
print ('Zip Complete')

gis = GIS("https://www.arcgis.com", c.AGOL_OWNER_ID, keyring.get_password('AGOL', c.AGOL_OWNER_ID))
agol_code_sample_item =  gis.content.get(agol_code_sample_item_id)
update_result = agol_code_sample_item.update(data=output_path)
if update_result:
    print(f"Successfully updated item '{agol_code_sample_item.title}' with the new zip file.")
else:
    print("Failed to update the item.")
