from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
import pandas as pd
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from APP.models import Main_person, Project, Shareholder_information, Tianyancha_User


# 登录
def login(phone, password, companyname):
    # 输入账号密码以及公司名称
    phone = phone
    password = password
    companyname = companyname
    url = 'https://www.tianyancha.com/login?from=http%3A%2F%2Fwww.tianyancha.com%2Fusercenter%2FmodifyInfo'

    # 打开页面
    driver = webdriver.Chrome()
    driver.get(url)
    driver.maximize_window()
    # 点击账号密码跳转到输入账号密码页面
    time.sleep(1)
    driver.execute_script("loginObj.toggleQrcodeAndPwd();")
    # 跳转到输入账号密码登录页面
    time.sleep(1)
    driver.execute_script("loginObj.changeCurrent(1);")
    # 输入账号
    time.sleep(1)
    inputuid = driver.find_element(By.XPATH, '//*[@id="mobile"]')
    inputuid.send_keys(phone)

    # 输入密码
    time.sleep(1)
    inputpassword = driver.find_element(By.XPATH, '//*[@id="password"]')
    inputpassword.send_keys(password)

    # 同意书
    time.sleep(1)
    driver.find_element(By.XPATH, '//*[@id="agreement-checkbox-account"]').click()

    # 点击登录
    time.sleep(1)
    driver.execute_script("loginObj.loginByPhone(event);")  # 由于获取不到登录按钮，于是直接执行登录按钮对应的js代码

    # 等待滑块验证完成
    time.sleep(10)
    # 等待页面加载完成
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="header-company-search"]')))
    # 开始爬取信息
    input = driver.find_element(By.ID, 'header-company-search')
    input.clear()
    input.send_keys(companyname)
    time.sleep(1)
    driver.find_element(By.XPATH, '//*[@class="input-group-btn btn -sm btn-primary component"]').click()
    time.sleep(1)
    driver.find_element(By.XPATH,
                        '//div[@class="index_list-wrap___axcs"]/div[1]//a[@class="index_alink__zcia5 link-click"]').click()
    driver.switch_to.window(driver.window_handles[-1])
    spider(driver, companyname)


# 检测分页
def check_pagination(div):
    pagination = div.find_element_by_class_name('pagination')
    if pagination:
        return True
    else:
        return False


# 资质资格
def Building_qualifications(driver, div, companyname):
    text = div.text
    text = re.sub(r'\n', ' ', text)
    pattern = r'\s*(\d{4}-\d{2}-\d{2})\s*(\d{4}-\d{2}-\d{2})\s*(\S+)\s*(\S+)\s*(\S+)\s*(\S+)\s*(\S+)\s*(\S+)\s*(\S+)'
    matches = re.findall(pattern, text[0])
    print(matches)
    columns = ['发证日期', '证书有效期', '资质类别', '资质证书号', '资质名称', '发证机关']
    df = pd.DataFrame(matches, columns=columns)


# 注册人员
def Registered_personnel(driver, div, companyname):
    text = div.text
    text = re.sub(r'序号', ' ', text)
    pattern = r'\s*\d\s*\S+\s*(\S+)\s*(\S+)\s*(\S+)\s*(\S+)'
    matches = re.findall(pattern, text)
    columns = matches[0]
    df = pd.DataFrame(matches[1:], columns=columns)


# 工程项目
def Engineering_project(driver, div, companyname):
    project_div = div
    # 第一页
    project = project_div.text
    project = re.sub(r'\n', ' ', project)
    project = re.sub(r'全部项目 序号', '', project)
    project = re.sub(r'\s*\d+(\s+\d+)*$', '', project)
    project = re.sub(r'详情', '', project)
    project_all = project
    # if check_pagination(project_div):
    #     page_div = project_div.find_element_by_class_name('pagination')
    #     total_page = len(page_div.find_elements(By.CLASS_NAME, 'num')) - 1
    #     for i in range(2, total_page + 1):
    #         # 点击第二页
    #         if i == 2:
    #             page_div.find_element(By.XPATH, './div[2]').click()
    #         # 点击第三页及之后页面
    #         else:
    #             page_div.find_element(By.XPATH, './div[2]/div[' + str(i + 1) + ']').click()
    #         # 获取当前页面的工程项目信息
    #         wait = WebDriverWait(driver, 10)
    #         wait.until(EC.presence_of_element_located(project_div))
    #         project = project_div.text
    #         # 整理数据
    #         project = re.sub(r'\n', ' ', project)
    #         project = re.sub(r'工程项目 28 全部项目 序号 项目编号 项目名称 项目属地 项目类别 建设单位 操作 ', '',
    #                          project)
    #         project = re.sub(r'\s*\d+(\s+\d+)*$', '', project)
    #         project = re.sub(r'详情', '', project)
    #         # 将每页的工程项目信息合并
    #         project_all = project_all + project
    # else:
    #     project_all = project
    # 将工程项目信息保存到数据库
    pattern = r'\s*\d+\s*(\S+)\s*(\S+)\s*(\S+)\s*(\S+)\s*(\S+)'
    matches = re.findall(pattern, project_all)
    columns = matches[0]
    df = pd.DataFrame(matches[1:], columns=columns)
    for i in range(len(df)):
        project = Project()
        project.project_number = df['项目编号'][i]
        project.project_name = df['项目名称'][i]
        project.project_location = df['项目属地'][i]
        project.project_type = df['项目类别'][i]
        project.construction_unit = df['建设单位'][i]
        project.company_name = companyname
        project.save()


# 主要人员
def Main_personnel(driver, div, companyname):
    main_person = div.text
    main_person = re.sub(r'\n最终受益人', '', main_person)
    pattern = r'\d+\s*\S+\s*(\S+)\s*.*?\s*(\S+)\s*-\s*-'
    main_person_match = re.findall(pattern, main_person)
    columns = ['主要人员', '职位']
    df = pd.DataFrame(main_person_match, columns=columns)
    # 保存到数据库
    for i in range(len(df)):
        person = Main_person()
        person.pname = df['主要人员'][i]
        person.position = df['职位'][i]
        person.company_name = companyname
        person.save()


def Stocker_information(driver, div, companyname):
    stocker = div.text
    pattern = r'(?P<name>\S+)\s*.*?\s*.*?\s*(?P<percent1>\d+.\d+%)\s*(?P<percent2>\d+.\d+%)\s*[\S\s]*?(?P<num>\d+\.\d+万元)\s*(?P<data>\d{4}-\d{2}-\d{2})'
    matches = re.findall(pattern, stocker)
    columns = ['股东（发起人）', '持股比例', '最终受益股份', '认缴出资额', '认缴出资日期']
    df = pd.DataFrame(matches, columns=columns)
    # 保存到数据库
    for i in range(len(df)):
        stock = Shareholder_information()
        stock.shareholder_name = df['股东（发起人）'][i]
        stock.shareholding_ratio = df['持股比例'][i]
        stock.ultimate_beneficial_shares = df['最终受益股份'][i]
        stock.contribution_amount = df['认缴出资额'][i]
        stock.contribution_time = df['认缴出资日期'][i]
        stock.company_name = companyname
        stock.save()


def spider(driver, companyname):
    # 透视图下载
    # wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="page-root"]/div[3]/div[1]/div[3]/div/div[2]/div[2]/div/div[4]/div/div[2]/div/div/div[1]/div[2]/div[3]/span')))
    # driver.find_element(By.XPATH,
    #                     '//*[@id="page-root"]/div[3]/div[1]/div[3]/div/div[2]/div[2]/div/div[4]/div/div[2]/div/div/div[1]/div[2]/div[3]/span').click()

    # 滑动页面到相应位置
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    # 等待页面加载完成
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="page-root"]//div[@data-dim="staff"]')))
    # 查找包含data-dim="staff"的div，获取主要人员信息
    main_person_div = driver.find_elements(By.XPATH, '//*[@id="page-root"]//div[@data-dim="staff"]')[0]
    Main_personnel(driver, main_person_div, companyname)

    # 滑动页面到相应位置
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    # 等待页面加载完成
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="page-root"]//div[@data-dim="holder"]')))
    # 查找包含data-dim="holder"的div，获取股东信息
    stocker_div = driver.find_elements(By.XPATH, '//*[@id="page-root"]//div[@data-dim="holder"]')[0]
    Stocker_information(driver, stocker_div, companyname)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    # 等待页面加载完成
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="page-root"]//div[@data-dim="constructAll"]')))
    construct_div = driver.find_elements(By.XPATH, '//*[@id="page-root"]//div[@data-dim="constructAll"]')[0]
    construct_divs = construct_div.find_elements(By.XPATH, './div[2]/div')
    for construct_div in construct_divs:
        first_word = construct_div.find_element(By.XPATH, './div[1]').text
        # if '资质资格' in first_word:
        #     Building_qualifications(driver, construct_div, companyname)
        # elif '注册人员' in first_word:
        #     Registered_personnel(driver, construct_div, companyname)
        if '工程项目' in first_word:
            Engineering_project(driver, construct_div, companyname)


# 封装函数
def get_data(phone, password, companyname):
    login(phone, password, companyname)
