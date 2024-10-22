import json

# Open the JSON file and load its contents
with open('C:\\Users\\admin\\Downloads\\ics_v1-20230328\\ics_v1\\ics_v1\\json\\ics_master_db_v1_fastenerexpress\\2023-04-26-v1.json') as f:
    data = json.load(f)

# Define the maximum number of objects per part
max_objects_per_part = 5000

# Loop through the objects in the JSON file and split them into parts
part_number = 1
objects_in_part = []
for obj in data:
    objects_in_part.append(obj)
    if len(objects_in_part) == max_objects_per_part:
        # Write the current part to a file
        with open(f'Coast_Pneumatics_{part_number}.json', 'w') as f:
            json.dump(objects_in_part, f)
        # Reset the objects in the part and increment the part number
        objects_in_part = []
        part_number += 1

# Write any remaining objects to a final part file
if objects_in_part:
    with open(f'Coast_Pneumatics_{part_number}.json', 'w') as f:
        json.dump(objects_in_part, f)
