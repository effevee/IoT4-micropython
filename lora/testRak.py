from lora import rak811

rak1 = rak811(1, 115200, debug=True)

res = rak1.start()
print(res)

if res == "OK":
    res = rak1.getVersion()
    print(res)

rak1.stop()