from lora import rak811

rak1 = rak811(1, 115200, debug=True)

res = rak1.start()
print(res)

if res == "OK":
    print(rak1.getVersion())
    print(rak1.getStatus())

rak1.stop()