'''
Resourse.py none print
20155136 심창현
'''

import RPi.GPIO as GPIO
from coapthon.resources.resource import Resource
import threading
import time

SeatCount = 0 # 자리 있음 카운트
LeftSeatCount = 0 # 자리비움 카운트
flags = 0 # bool flags

# GPIO
PIR = 26
TRIG = 21
ECHO = 18
LED = 19

class ObservableResource(Resource):
    def __init__(self, name="Obs", coap_server=None):
        super(ObservableResource, self).__init__(name, coap_server, visible=True, observable=True, allow_children=False)
        self.payload = 'null'
        self.period = 10 # 10초마다 업데이트
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIR, GPIO.IN) # PIR
        GPIO.setup(TRIG, GPIO.OUT) # TRIGGER
        GPIO.setup(ECHO, GPIO.IN) # ECHO
        GPIO.setup(LED, GPIO.OUT) # LED
        self.update(True)

    def render_GET(self, request):
        return self

    def render_POST(self, request):
        self.payload = request.payload
        return self
    
    def render_DELETE(self, request):
        return True

    def update(self, first=False):
        global SeatCount
        global LeftSeatCount
        global flags
        
        if not self._coap_server.stopped.isSet():
            timer = threading.Timer(self.period, self.update) # 설정한 period(10)초마다 업데이트
            timer.setDaemon(True)
            timer.start()

            if not first and self._coap_server is not None:
                
                # 초음파 시작시간과 종료시간 변수
                start = 0
                stop = 0
                
                # 초음파 트리거 핀을 OFF 상태로 유지
                GPIO.output(TRIG, False)
                time.sleep(0.5)
                
                # 초음파 펄스를 한번 내보낸다
                GPIO.output(TRIG, True)
                time.sleep(0.00001)
                GPIO.output(TRIG, False)
                
                # 에코 핀이 ON 되는 시점을 시작시간으로 설정
                while GPIO.input(ECHO) == 0: 
                    start = time.time()
                # 에코 핀이 OFF 되는 시점을 반사파 수신 시간으로 설정
                while GPIO.input(ECHO) == 1:
                    stop = time.time()
                
                # 초음파는 반사파이기 때문에 실제 거리를 계산하려면 2로 나눠야한다
                # 음속이기 때문에 340m/s으로 계산한다
                TimeTxRx = stop - start # 거리
                Distance = (TimeTxRx * 34000.0) / 2
                
                # 프로토타입 박스 크기는 20cm이다. 사람이 앉아있는 경우에는 10cm으로 가정한다.
                '''
                flags == false이고, PIR 인식이 안되고 초음파센서로 측정한 거리가 18cm 이상이면
                    payload에 자리 없음을 저장
                    그 후에 클라이언트로 알림을 보내준 후
                    옵저브 카운트를 증가시킨다.
                '''                
                if flags == False and not GPIO.input(26) and Distance >= 18:
                    self.payload = '자리 없음'
                    self._coap_server.notify(self) # notify
                    self.observe_count += 1
                    SeatCount = 0
                    
                    
                '''
                PIR 인식되고 8cm ~ 12cm 이내이면
                    자리 있음이라는 SeatCount 변수를 1 증가시킨다
                    그리고 자리 없음 조건문을 통과시키기 위해 flags를 1으로 바꾼다
                    payload에 자리 있음을 저장한 후
                    클라이언트 알림 및 옵저브 카운트를 증가시킨다.
                
                    만약 SeatCount가 6이상(1분)이 되고 초음파센서로 측정한 사람과의 거리가 35cm 이상 멀어지면
                        졸음 방지를 위해 원래 자세가 될 때까지 LED를 켜고 끄는것을 반복한다.
                만약 PIR센서가 인식이 안되면 flags는 0으로 하고 payload는 자리 없음을 저장한다
                '''
                if GPIO.input(26) and (Distance >= 8 and Distance <= 12): # PIR = 1이고 8~12cm 이내이면 notify
                    SeatCount += 1 # 자리있음 카운트
                    flags = 1
                    self.payload = '자리 있음'
                    self._coap_server.notify(self) # notify
                    self.observe_count += 1

                    if SeatCount >= 6 and Distance >= 14 : # 앉은지 1분이 지나고, 거리가 14cm이상 멀어지면 LED ON, OFF
                        GPIO.output(LED, True)
                        time.sleep(1)
                        GPIO.output(LED, False)

                elif not GPIO.input(26):
                    # 값 초기화
                    flags = 0
                    self.payload = '자리 없음'
                    
                    
                '''
                만약 사람이 한번이라도 자리에 앉았고, 초음파센서간의 거리가 18cm 이상이 되면
                    자리 비움이라는 LeftSeatCount 변수를 1 증가시킨다
                    payload에 자리 비움을 저장한 후
                    클라이언트에 알림 및 옵저브 카운트를 증가시킨다
                    만약 LeftSeatCount가 360(1시간) 이상이면
                        자리 없음으로 간주하고 클라이언트에 알림을 보내고 옵저브 카운트를 증가시킨다
                        그리고 SeatCount(자리있음), LeftSeatCount(자리비움), flags(PIR 자리없음 판단변수)를 0 으로 초기화 시킨다
                '''
                if flags == True and SeatCount > 0 and Distance >= 18: # 18cm 이상이면
                    LeftSeatCount += 1 # 자리비움 카운트
                    self.payload = '자리 비움'
                    self._coap_server.notify(self)
                    self.observe_count += 1
                    
                    if LeftSeatCount >= 360: # 1시간 이상 자리 비움이면
                        self._coap_server.notify(self) # notify
                        self.observe_count += 1
                        # 값 초기화
                        SeatCount = 0
                        LeftSeatCount = 0
                        flags = 0
