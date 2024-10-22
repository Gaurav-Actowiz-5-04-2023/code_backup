# import json
# # with open (r"D:\Work_motion\motion_json_att.json",'r') as f1:
# with open(r"E:\VAIBHAV's PROJECT\ics_CWD\ics_v1\ics_v1\ics_v1\json\ics_cwd\2023-06-29\full\2023-06-29-v1.json",'r') as f1:
#     mydata=f1.read()
# my_d=json.loads(mydata)
# mylist=[]
# count=0
# for data in my_d:
#     if data["estimated_lead_time"] == '':
#         data["estimated_lead_time"] = None
#         mylist.append(data)
#         count+=1
#         print('estimat updated',count)
#     else:
#         mylist.append(data)
# print(count)
# with open(r"E:\VAIBHAV's PROJECT\ics_CWD\ics_v1\ics_v1\ics_v1\json\ics_cwd\2023-06-29\full\2023-06-29-v1_new555.json",'w') as f2:
#     f2.write(json.dumps(mylist))
#
