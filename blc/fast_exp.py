import requests, time, os, argparse
from lxml import html
from threading import Thread


parser = argparse.ArgumentParser(description='Auto geting blc exp. Just for fun!')
parser.add_argument('-m', type=str, help='Your MoodleSession cookies!')
parser.add_argument('-c', nargs='*', help='Your target courses links!', required=True)
parser.add_argument('-n', action=argparse.BooleanOptionalAction, help='Hide your name!')
parser.add_argument('-u', type=str, help='Username')
parser.add_argument('-p', type=str, help='Password')
parser.add_argument('-t', action=argparse.BooleanOptionalAction, help='Run in Thread')
args = parser.parse_args()

headers = {
    "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.46 Safari/537.36',
}
 
session = requests.Session()
 
courseLink = args.c
             
 
jar = requests.cookies.RequestsCookieJar()
jar.set('MoodleSession', args.m)

def login(user=args.u, passw=args.p):
  global s
  
  if not (user or passw): return False

  loginLink = "https://elearn.daffodilvarsity.edu.bd/login/index.php"
  s.cookies.clear()
  loginPage = s.get(loginLink, headers=headers).text
  tree = html.fromstring(loginPage)
  logintoken = tree.xpath("//form[@id='login']/input[@name='logintoken']")[0].value
  loginTry = s.post(loginLink, data={
      "username": user,
      "password": passw,
      "logintoken": logintoken}, headers=headers)
  
  return True if loginTry.ok else False

def clear_output():
    command = 'clear'
    if os.name in ('nt', 'dos'):
        command = 'cls'
    os.system(command)

def sleep(s):
  print("")
  for i in range(s,0,-1):
    print('-', end='')
    time.sleep(1)
  print("")
 
def job(l):
  eT = 0
  old = 0

  clickLink = []
  
  try:
    allpageLink = s.get(l, headers=headers).text
    tree = html.fromstring(allpageLink)
    if not tree.xpath("//span[@class='username pr-1']"):
      raise Exception("404")
  except:
    if login():
      allpageLink = s.get(l, headers=headers).text
  
  clickLink.append(l)
  clickLink += tree.xpath("//div[@class='activityinstance']/a[@class='aalink']/@href")
  for loop in range(1000):
    for id,link in enumerate(clickLink):
      trying = s.get(link, headers=headers)
      trylogin = trying.text
      if loop == 0 and id == 0:
        time.sleep(5)
        clear_output()
      if not trying.status_code == 200:
        if eT < 3:
          print(f"Retrying... {eT}")
          eT += 1
          continue
        else:
          clear_output()
          raise Exception(f'Status code: {trying.status_code}\n count: {loop}\nLink: {link}')
      if id == 0:
        tree = html.fromstring(trylogin)
        if not args.n:
            name = tree.xpath('//span[@class="username pr-1"]/text()')
        else:
            name = "Hidden"
        # Ex-show Use
        nowEx = int(tree.xpath('//div[@class="xp-total"]/div/div[@class="pts"]/text()')[0].replace(',', ''))
        print(f"{name} xp:{nowEx-old if loop != 0 else 0}+ T:{nowEx}xp Loop:{loop} \n[0]", end='')
        if loop != 0 and (nowEx-old) == 0:
          sleep(5)
        
        old = nowEx

 
        # Normal Use
        # print(f"{name} Loop:{loop} \n[0]", end='')
      else:
        print(f"[{id}]", end='')
    sleep(30)
s = requests.Session()
s.cookies = jar

if args.t:
  threadList = []
  for t in courseLink:
    threadList.append(Thread(target=job, args=(t,)))
  for _ in threadList:
    _.start()
  for _ in threadList:
    _.join()
else:
  for course in courseLink:
    job(course)


# job(courseLink[0])
