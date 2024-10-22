start = 900000
end = 2100000
num_parts = 100
spider_name = 'download_assest -a vendor_id=ACT-B3-010'


# Calculate the number of items in each part
items_per_part = (end - start + 1) // num_parts

# Initialize a list to store the range parts
range_parts = []

# Generate the range parts
for i in range(num_parts):
    part_start = start + i * items_per_part
    part_end = start + (i + 1) * items_per_part - 1 if i < num_parts - 1 else end
    range_parts.append((part_start, part_end))

# Print the range parts
for i, (part_start, part_end) in enumerate(range_parts):
    print(f'start "Part:{"SKYGEEK"}{i+1}" skygeek crawl {spider_name} -a start={part_start} -a end={part_end}')

