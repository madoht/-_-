import requests#requests 라이브러리를 호출합니다.
import csv#csv 라이브러리를 호출합니다.
from bs4 import BeautifulSoup#bs4 라이브러리에서 BeautifulSoup를 호출합니다.


# CSV파일 저장 부분
def save_file(jobs):
    file = open("jobs.csv", mode= "w")#jobs라는 이름을 가진 CSV 파일을 생성하여 쓰기 모드로 오픈합니다.
    writer = csv.writer(file)#jobs를 씁니다.
    writer.writerow(["직업명", "회사", "장소", "지원 링크"])#CSV 파일에 한줄을 추가합니다.
    for job in jobs:#그 직업이 직업 리스트에 포함되어있는 경우
        writer.writerow(list(job.values()))#직업의 값을 리스트화하여 CSV파일에 입력합니다.
    confirm_file = input("jobs.csv 파일이 생성되었습니다. 파일을 확인하시겠습니까?[y/n]")# CSV파일을 열어볼 것인지에 대한 입력값
    if confirm_file == "y":#입력값이 y일 경우
        open_file = open('jobs.csv', 'r', encoding='utf-8')#utf-8로 인코딩되어있는 jobs.csv파일을 오픈합니다.
        readline = csv.reader(open_file)#jobs.csv파일을 문자열 타입인 reader 객체로 반환합니다.
        for line in readline:#line 변수가 readline 안에 있는 경우
            print(line)#line을 출력합니다.(job.csv파일을 한줄씩 출력하는 것)
        open_file.close()#출력이 끝날시 CSV파일을 닫습니다.
    
    elif confirm_file == "n":#입력값이 n일 경우
        return#저장합니다.
    
    else:#y 나 n이 아닌 다른 값을 입력했을 경우
        print("잘못된 입력입니다. jobs.csv 파일로 저장되었습니다.")


# 사람인 크롤링 부분
def get_linked_last_page(url):#마지막 페이지를 찾아오는 함수
    result = requests.get(url)#url을 불러와서 result 객체에 할당합니다.
    soups = BeautifulSoup(result.text, "html.parser")#result를 text로 받아서 url의 html를 텍스트로 soups 객체에 할당합니다.
    pages = soups.find("div", {"class" : "pagination"}).find_all("span")# soups 내부의 html에서 div 태그를 가진 객체중 클래스명이 pagination인 객체 아래에서 span 태그를 가진 객체를 모두 찾아냅니다. 
    last_page = pages[-1].get_text(strip=True)#pages에서 찾아낸 객체 중 가장 큰 객체의 태그와 클래스명을 제외하고 문자로 last_page에 할당합니다.
    return int(last_page)#last_page를 int형으로 반환합니다.


def extracting_jobs(html):#직업을 찾아내는 함수
    job_title = html.find("h2", {"class" : "job_tit"}).find("a")["title"]#html 안에서 h2 태그를 가진 클래스 명 job_tit 아래에서 a 태그 내부의 title의 내용을 찾습니다.
    company = html.find("div", {"class": "area_corp"}).find("span")#html 안에서 div 태그를 가진 클래스 명 area_corp 아래에서 span 태그를 찾습니다.
    location = html.find("div", {"class" : "job_condition"}).find("a")#html 안에서 div 태그를 가진 클래스 명 job_condition 아래에서 a 태그를 찾습니다.
    company = company.get_text(strip=True)#company 객체 내부에서 찾아놓은 span 태그의 태그를 제외하고 문자로 company에 재할당합니다. 
    location = location.get_text(strip=True)#location 객체 내부에서 찾아놓은 a 태그의 태그를 제외하고 문자로 location에 재할당합니다.
    job_id = html['value']#html에서 value가 가진 값을 찾아서 job_id에 할당합니다.
    return ({
        '직업명' : job_title,
        '회사' : company,
        '장소' : location,
        '지원 링크' : f"http://www.saramin.co.kr/zf_user/jobs/relay/view?isMypage=no&rec_idx={job_id}"
    })


def extracting_jobsParse(last_page, url):#페이지를 하나씩 넘기는 함수
    jobs = []#jobs란 이름의 빈 리스트를 생성합니다.
    for page in range(last_page):#last_page만큼 for문을 돌립니다.
        print(f"사람인에서 불러오는 중입니다. 페이지:{page + 1}")#크롤링하는 페이지를 순차적으로 출력합니다.
        result = requests.get(f"{url}&pg={page + 1}")#해당 페이지의 html을 불러옵니다.
        soups = BeautifulSoup(result.text, "html.parser")#불러온 html을 텍스트화하여 soups 변수에 저장합니다.
        job_results = soups.find_all("div", {"class": "item_recruit"})#저장한 html 텍스트에서 div태그 중 클래스 명이 item_recruit을 모두 찾습니다. 
        for result in job_results:#불러온 페이지의 html이 job_results안에 있을 때, for문을 돌립니다.
            job = extracting_jobs(result)#직업을 찾아내는 함수를 호출합니다.
            jobs.append(job)#jobs 리스트에 job를 포함시킵니다.
    return jobs#jobs 값을 반환합니다.


def find_jobs(work_id):#사람인 최종 함수
    url = f"http://www.saramin.co.kr/zf_user/search/recruit?&searchword={work_id}&recruitPageCount=200"
    last_page = get_linked_last_page(url)#마지막 페이지를 찾아오는 함수를 호출합니다.
    jobs = extracting_jobsParse(last_page, url)#페이지를 하나씩 넘기는 함수를 호출합니다.
    return(jobs)#위의 함수에서 반환받은 값을 반환합니다.


# Indeed 크롤링 부분
def get_last_page(url):#마지막 페이지를 찾아오는 함수
    result = requests.get(url)#url을 불러와서 result 객체에 할당합니다.
    soup = BeautifulSoup(result.text, "html.parser")#result를 text로 받아서 url의 html를 텍스트로 soup 객체에 할당합니다.
    pagination = soup.find("div", {"class": "pagination"})# soups 내부의 html에서 div 태그를 가진 객체중 클래스명이 pagination인 객체를 모두 찾아냅니다.
    links = pagination.find_all('a')#찾아낸 객체 아래에 a 태그를 가진 객체를 모두 찾아냅니다.
    pages = []#pages 라는 이름을 가진 빈 리스트를 생성합니다.
    for link in links[:-1]:#links의 마지막 한개의 요소를 제외한 나머지 요소들에 있을 때, for문을 돌립니다.
        pages.append(int(link.string))#link의 값을 숫자로 받아서 pages 리스트에 추가시킵니다.
    max_pages = pages[-1]#pages 리스트의 마지막 요소를 max_pages에 할당합니다.
    return max_pages#max_pages를 반환합니다.


def extract_job(html):#직업을 찾아내는 함수
    title = html.find("h2", {"class": "title"}).find("a")["title"]#html 안에서 h2 태그를 가진 클래스 명 title 아래에서 a 태그 내부의 title의 내용을 찾습니다.
    company = html.find("span", {"class": "company"})#html 안에서 span 태그를 가진 클래스 명 company를 찾습니다.
    if company:#만약 company이면
        company_anchor = company.find("a")#company 에서 a태그를 가진 객체를 찾아서 company_anchor에 할당합니다.
        if company_anchor is not None:#company에 할당된 값이 있을 때,
            company = str(company_anchor.string)#할당된 값을 string형으로 재 할당합니다.
        else:
            company = str(company.string)#company의 값을 string형으로 재 할당합니다.
        company = company.strip()#company 내부 객체의 태그나, 클래스명을 제외합니다.
    else:
        company = None#company 객체의 값이 없습니다.
    location = html.find("div", {"class": "recJobLoc"})['data-rc-loc']#html에서 div 태그와 클래스 명 recJobLoc를 가진 객체를 찾은 다음 객체 내부의 data-rc-loc값만 location에 할당합니다.
    job_id = html["data-jk"]#html에서 data-jk가 가진 값을 찾아서 job_id에 할당합니다.
    return {'직업명': title,
            '회사': company,
            '장소': location,
            "지원 링크": f"https://kr.indeed.com/viewjob?jk={job_id}"
            }


def extract_jobs(last_page, url):#페이지를 넘기는 함수
    jobs = []#jobs라는 이름을 가진 빈 리스트를 생성합니다.
    LIMIT = 50#LIMIT 변수에 50이라는 값을 할당합니다. LIMIT을 조절함으로써 사이트에서 한번에 보이는 직업 수를 조절할 수 있습니다.
    for page in range(last_page):#last_page만큼 for문을 돌립니다.
        print(f"Indeed에서 불러오는 중입니다. 페이지:{page + 1}")#크롤링하는 페이지를 순차적으로 출력합니다.
        result = requests.get(f"{url}&start = {page * LIMIT}")#페이지를 하나씩 불러옵니다.
        soup = BeautifulSoup(result.text, "html.parser")#불러온 html을 텍스트화하여 soup 변수에 저장합니다.
        results = soup.find_all("div", {"class": "jobsearch-SerpJobCard"})#soup 내에서 div 태그와 클래스 명 jobsearch-SerpJobCard를 가진 객체를 모두 찾습니다.
        for result in results:#result가 results 안에 있으면, for문을 돌립니다.
            job = extract_job(result)#직업을 찾아내는 함수를 호출하여 리턴받은 값을 job에 저장합니다.
            jobs.append(job)#job을 jobs 리스트에 포함시킵니다.
    return jobs#jobs 리스트를 반환합니다.


def get_jobs(work_id):#Indeed 최종 호출 함수
    url = f"https://kr.indeed.com/%EC%B7%A8%EC%97%85?q={work_id}&limit=50"
    last_page = get_last_page(url)#마지막 페이지를 찾아오는 함수를 호출합니다.
    jobs = extract_jobs(last_page, url)#페이지를 넘기는 함수를 호출합니다.
    return jobs#반환받은 jobs를 반환합니다.

# 최종 입출력 & 저장 부분
work_id = str(input("원하는 분야를 말씀하십시오 : "))#string형으로 입력값을 받습니다.
jobs_final = find_jobs(work_id) + get_jobs(work_id)#사람인 과 Indeed에서 각각 크롤링하여 반환받은 결과를 합칩니다. 
save_file(jobs_final)#합친 결과를 CSV파일로 저장하는 함수를 호출합니다.