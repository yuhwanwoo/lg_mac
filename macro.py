from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import urllib
import time
import pytz
import datetime
import requests
from selenium.common.exceptions import NoSuchElementException
import easyocr
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# 태그가 없으면 에러발생
def check_exists_by_element(by, name):
    elements = driver.find_elements(by, name)
    if len(elements) == 0:
        return False
    return True

def get_tag_name(x):
    return x.tag_name

# 추가로 할일
# 1.    https://sh-safer.tistory.com/10 이 방법 고려
#       아니면 로그인 후 상태는 대기해놓자
# 2.    에러 발생 시 try catch로 묶자 -> 안꺼지게

############ 초기 설정 ############
# 레베카
# loginId = 'wooseung92'
# loginPwd = 'audgns1230*'
# goodsCode = '23008837'
# targetDate = '2023-07-13 16:40:00'
# isAutoMakingCharacter = None
# targetSeat = '스탠딩' # 스탠딩: '스탠딩', VIP석: 'VIP석 '
# targetArea = '001영역'
# targetDay = '25'
# targetShow = '2회 19:30'
# targetCount = 2
# isGradeSeparation = False
##################################

############ 초기 설정 ############
# 레베카
loginId = 'wooseung92'
loginPwd = 'audgns1230*'
goodsCode = '24001548'
targetDate = '2023-07-18 20:00:00'
isAutoMakingCharacter = True
targetSeat = 'SR석' # 스탠딩: '스탠딩', VIP석: 'VIP석 '
targetArea = '001영역'
targetDay = '26'
targetShow = '1회 15:00'
targetCount = 2
isGradeSeparation = True
##################################

############ 초기 설정 ############
# loginId = 'wooseung92'
# loginPwd = 'audgns1230*'
# goodsCode = '23009492'
# targetDate = '2023-07-13 16:40:00'
# isAutoMakingCharacter = None # True, False, None
# targetSeat = '전석' # 스탠딩: '스탠딩', VIP석: 'VIP석 '
# targetArea = '001영역'
# targetDay = '27'
# targetShow = '1회 20:00'
# targetCount = 2
# isGradeSeparation = False
##################################

############ 초기 설정 ############
# 찰리푸스 테스트
# loginId = 'wooseung92'
# loginPwd = 'audgns1230*'
# goodsCode = '23008633'
# targetDate = '2023-07-13 16:40:00'
# isAutoMakingCharacter = True # True, False, None
# targetSeat = '전석' # 스탠딩: '스탠딩', VIP석: 'VIP석 '
# targetArea = '001영역'
# targetDay = '21'
# targetShow = '1회 19:00'
# targetCount = 2
# isGradeSeparation = True
##################################

########## 티켓팅 날짜 설정 ##########
targetDatetime = datetime.datetime.strptime(targetDate, "%Y-%m-%d %H:%M:%S")
koreaTz = pytz.timezone('Asia/Seoul')
targetDatetime.astimezone(koreaTz)

targetLocalizedTime = koreaTz.localize(targetDatetime)

targetUtcTime = targetLocalizedTime.astimezone(pytz.UTC)
targetEpochTime = (targetUtcTime - datetime.datetime(1970, 1, 1, tzinfo=pytz.UTC)).total_seconds()
targetTime = int(targetEpochTime)
#####################################

nowTime = 0
    
####################################
# print("티켓팅 시각")
# print(targetTime)
# print("현재 시각")
# print(nowTime)
try:
    driver = webdriver.Chrome()
    # 사이즈조절
    driver.set_window_size(1400, 1000)  # (가로, 세로)
    driver.get('https://ticket.interpark.com/Gate/TPLogin.asp') # 페이지 이동

    driver.switch_to.frame(driver.find_element(By.XPATH, "//div[@class='leftLoginBox']/iframe[@title='login']"))
    userId = driver.find_element(By.ID, 'userId')
    userId.send_keys(loginId) # 로그인 할 계정 id
    userPwd = driver.find_element(By.ID, 'userPwd')
    userPwd.send_keys(loginPwd) # 로그인 할 계정의 패스워드
    userPwd.send_keys(Keys.ENTER)

    driver.get('https://tickets.interpark.com/goods/' + goodsCode)

    driver.implicitly_wait(10)

    # 티켓팅 첫 화면에 팝업 뜨는지 체크
    firstPopupCheck = check_exists_by_element(By.XPATH, "//*[@id='popup-prdGuide']/div/div[3]/button")

    if firstPopupCheck:
        driver.find_element(By.XPATH, "//*[@id='popup-prdGuide']/div/div[3]/button").click()
    #################################

    # 서버 시간 될 때까지 대기
    while nowTime < targetTime: ## <=
        ###### 현재 서버 시간 가져오기 ######
        response = requests.get('http://ticket.interpark.com', headers={'ETag': ''})
        nowDate = response.headers['Date']
        print(nowDate)
        nowDatetime = datetime.datetime.strptime(nowDate, '%a, %d %b %Y %H:%M:%S %Z')
        nowTz = pytz.timezone('GMT')
        nowDatetime.astimezone(nowTz)
        nowLocalizedTime = nowTz.localize(nowDatetime)
        nowUtcTime = nowLocalizedTime.astimezone(pytz.UTC)
        nowEpochTime = (nowUtcTime - datetime.datetime(1970, 1, 1, tzinfo=pytz.UTC)).total_seconds()
        nowTime = int(nowEpochTime)
        print(str(nowTime) + " " + str(targetTime))
        driver.refresh()
        time.sleep(1)

    driver.implicitly_wait(10)

    driver.find_element(By.XPATH, "//li[text()='" + targetDay + "']").click()
    driver.find_element(By.XPATH, "//a[@data-text='" + targetShow + "']").click()

    driver.find_element(By.CLASS_NAME, "sideBtn.is-primary").click()
    while len(driver.window_handles) == 1:
        pass

    driver.switch_to.window(driver.window_handles[1])

    driver.implicitly_wait(10)
    driver.switch_to.frame(driver.find_element(By.XPATH, "//*[@id='ifrmSeat']"))
    # 자동 문자 생성 할 것인지 수기로 할 것인지 설정
    if isAutoMakingCharacter:
        # driver.switch_to.frame(driver.find_element(By.XPATH, "//*[@id='ifrmSeat']"))
        start = time.time()
        hasCapchaImage = check_exists_by_element(By.XPATH, "//*[@id='imgCaptcha']")
        end = time.time()
        print(f"{end - start:.5f} sec")
        # hasCapchaImage = check_exists_by_element(By.XPATH, "//div[@id='divRecaptcha']")
        if hasCapchaImage:
            # 입력해야될 문자 이미지 캡쳐하기.
            capchaPng = driver.find_element(By.XPATH, "//*[@id='imgCaptcha']")

            # easyocr 이미지내 인식할 언어 지정
            reader = easyocr.Reader(['en'])
            # 캡쳐한 이미지에서 문자열 인식하기
            result = reader.readtext(capchaPng.screenshot_as_png, detail=0)

            # 이미지에 점과 직선이 포함되어있어서 문자 인식이 완벽하지 않아서 데이터를 수동으로 보정해주기로 했습니다.
            capchaValue = result[0].replace(' ', '').replace('5', 'S').replace('0', 'O').replace('$', 'S').replace(',', '')\
                .replace(':', '').replace('.', '').replace('+', 'T').replace("'", '').replace('`', '')\
                .replace('1', 'L').replace('e', 'Q').replace('3', 'S').replace('€', 'C').replace('{', '').replace('-', '').replace('@', 'Q')\
                .replace('[', 'L').replace('_', '').replace('~', '').replace('8', 'B')
            print(capchaValue)
            # 입력할 텍스트박스 클릭하기.
            driver.find_element(By.CLASS_NAME,'validationTxt').click()
            # 추출된 문자열 텍스트박스에 입력하기.
            chapchaText = driver.find_element(By.ID, 'txtCaptcha')
            chapchaText.send_keys(capchaValue)
            driver.find_element(By.XPATH, "//*[@id='divRecaptcha']/div[1]/div[4]/a[2]").click()
        else :
            print("test")
    elif (isAutoMakingCharacter == False):
        # 자동예매 방지 문자열입력이 떠있는지 확인
        # driver.switch_to.frame(driver.find_element(By.XPATH, "//div[@id='divBookSeat']/iframe[@id='ifrmSeat']"))

        firstPopupCheck = check_exists_by_element(By.XPATH, "//div[@id='divRecaptcha']")

        # 자동예매 방지 문자열 입력창이 있다면 5초 대기
        if firstPopupCheck:
            time.sleep(5)
    else:
        print("NONE")
    
    possibleSeats = None
    if isGradeSeparation:
        driver.find_element(By.XPATH, By.XPATH, '//*[@id="SeatGradeInfo"]//./tbody//a[text()="001영역"]').click()
        driver.switch_to.frame(driver.find_element(By.XPATH, "//div[@class='seatL']/iframe[@id='ifrmSeatDetail']"))
        possibleSeats = driver.find_elements(By.XPATH, "//span[@class='SeatN']")
    else:
        driver.switch_to.frame(driver.find_element(By.XPATH, "//div[@class='seatL']/iframe[@id='ifrmSeatDetail']"))
        possibleSeats = driver.find_elements(By.XPATH, "//tbody//img[@class='stySeat']")
    # driver.find_element(By.XPATH, "//*[@id='SeatGradeInfo']//./tbody//a[text()='"+ targetArea + "']").click()
    # driver.find_element(By.XPATH, "//strong[text()='"+ targetSeat +"']").click()
    # driver.find_element(By.XPATH, "//strong[text()='스탠딩']").click()
    # driver.find_element(By.XPATH, By.XPATH, "//*[@id='SeatGradeInfo']//./tbody//a[text()='"+ targetArea + "']").click()
    # driver.find_element(By.XPATH, By.XPATH, '//*[@id="SeatGradeInfo"]//./tbody//a[text()="001영역"]').click()

    # hasArea = check_exists_by_element(By.XPATH, "//*[@id='SeatGradeInfo']//./tbody//a[text()='"+ targetArea + "']")
    # print(hasArea)

    # if hasArea:
    #     driver.find_element(By.XPATH, By.XPATH, "//*[@id='SeatGradeInfo']//./tbody//a[text()='"+ targetArea + "']").click()
    # print("1")

    cnt = 0
    for possibleSeat in possibleSeats:
        if cnt == targetCount:
            break
        possibleSeat.click()
        cnt += 1

    # iframe 을 옮겼으니 결제 화면으로 가기 위해서 iframe을 기본 iframe으로 옮겨줘야 함
    driver.switch_to.default_content()

    driver.switch_to.frame(driver.find_element(By.XPATH, "//*[@id='ifrmSeat']"))

    driver.find_element(By.XPATH, "//div[@class='seatR']//img[@id='NextStepImage']").click()
except:
    while(True):
        pass

while(True):
        pass



############## 여기까지 1차 완료 ##############

# 좌석 선택 iframe
# driver.switch_to.frame(driver.find_element(By.XPATH, "//div[@class='seatL']/iframe[@id='ifrmSeatDetail']"))
# 활성화 되어 있는 좌석의 class 속성 stySeat
# driver.switch_to.frame(driver.find_element(By.ID, "ifrmSeat"))
# seat_check = driver.find_elements(By.XPATH, "//*[@id='SeatGradeInfo']//./*") # 됐던거

# seat_check = driver.find_elements(By.XPATH, "//span[@class='SeatN']")
# seat_check = list(map(get_tag_name, seat_check))
# print(seat_check)



# seat_check = driver.find_elements(By.XPATH, "//*[@id='GradeDetail']/div/ul")

# seat_title = seat_check.get_attribute('title')
# b = seat_title.split('-')

###############################################################

# driver.close()