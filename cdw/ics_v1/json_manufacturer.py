import pandas as pd

file_path = r"E:\ProjectICS\Output_file\ics_master_db_v1_cdw\2024-03-08\json\sample_2024-03-08-v1.json"

product_df = pd.read_json(file_path)

def manufacturer_attributes(attributes):
    manufacturer = "CDW"
    for i in attributes:
        if i['name'] == 'Manufacturer':
            manufacturer = i['value']
    return manufacturer

product_df['manufacturer'] = product_df['attributes'].apply(manufacturer_attributes)

def attrinute_manufacturer_remove(attributes):
    Length = len(attributes)
    for i in range(Length):
        if attributes[i]['name'] == 'Manufacturer':
            del attributes[i]
            break
    return attributes

product_df['attributes'] = product_df['attributes'].apply(attrinute_manufacturer_remove)

product_df['sku'] = product_df['sku'].apply(str)

final_file_path = r"E:\ProjectICS\Output_file\ics_master_db_v1_cdw\2024-03-08\json\sample_2024-03-08-v2.json"

product_df.to_json(final_file_path, orient="records")

size = 300000

k = product_df.shape[0]
for i in range(int(k / size) + 1):
    df = product_df[size * i:size * (i + 1)]
    writer = pd.ExcelWriter(
        r"E:\ProjectICS\Output_file\ics_master_db_v1_cdw\2024-03-08\excel\2024-03-08_PART_001.xlsx",
        engine='xlsxwriter',
        engine_kwargs={'options': {'strings_to_urls': False}}
    )
    writer.book.use_zip64()
    df.to_excel(writer)
    writer.close()

