import requests, json

with open('./transcript.txt', 'r') as f:
    text = f.read()
num = 7
response = requests.post(f"http://localhost:3001/transcript/{num}", data=text, headers={'Content-Type': 'text/plain'})
input("--->")
response = requests.get(f"http://localhost:3001/transcript/{num}/summary?interviewee=Jason")
print(response.text)
input("\n\n---------x---------\n\n")
body = response.json()
output = body["output"]
cost = body["cost"]
final_str = []
for item in output:
    final_str.append(item["text"])
    print("\n-------------------------------")
    print("Text: ", item["text"])
    for reference in item["references"]:
        print(text[reference[0]:reference[1]])