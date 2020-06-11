'''
Coap_server.py
20155136 심창현
'''
from coapthon.server.coap import CoAP
import Resource
import RPi.GPIO as GPIO

class CoAPServer(CoAP):
    def __init__(self, host, port):
        CoAP.__init__(self, (host, port))
        # observe path를 설정 후 Resource.py의 ObservableResource Class를 리소스에 추가시킨다
        self.add_resource('observe/', Resource.ObservableResource(coap_server=self))

def main():
    # 라즈베리파이 IP으로 서버를 지정해준다
    server = CoAPServer("192.168.0.76", 5683)
    
    # 응답을 계속 받는다
    try:
        server.listen(10)
    # Ctrl + C를 누르면 서버를 종료시킨다
    except KeyboardInterrupt:
        print("Server Shutdown")
        server.close()
        print("Exiting...")
        # GPIO를 초기화시킨다
        GPIO.cleanup()

if __name__ == '__main__':
    main()
