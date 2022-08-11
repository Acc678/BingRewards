import os
import time
import random
import traceback
#os.system("pip install apprise")
import apprise
#os.system("pip install RandomWords")
from random_words import RandomWords

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from dotenv import load_dotenv

# Load ENV
load_dotenv()

if not os.environ["LOGIN"]:
    raise Exception("LOGIN not set. Please enter your login information in .env variable 'LOGIN' in the following format: 'EMAIL:PASSWORD,EMAIL2:PASSWORD2,EMAIL3:PASSWORD3'")
else:
    # LOGIN EXAMPLE:
    # "EMAIL:PASSWORD,EMAIL:PASSWORD"
    ACCOUNTS = os.environ["LOGIN"].replace(" ", "").split(",")

if (len(ACCOUNTS) > 5):
    raise Exception(f"You can only have 5 accounts per IP address. Using more increases your chances of being banned by Microsoft Rewards. You have {len(ACCOUNTS)} accounts within your LOGIN env variable. Please adjust it to have 5 or less accounts and restart the program.")

if not os.environ["URL"]:
    raise Exception("URL not set. Please enter a login URL in .env variable 'URL' obtained from the sign in button of https://bing.com/")

TERMS = ["define ", "explain ", "example of ", "how to pronounce ", "what is ", "what is the ", "what is the definition of ",
         "what is the example of ", "what is the pronunciation of ", "what is the synonym of ",
        "what is the antonym of ", "what is the hypernym of ", "what is the meronym of ","photos of "]

# Optional Variables
APPRISE_ALERTS = os.environ.get("APPRISE_ALERTS", "")
if APPRISE_ALERTS:
    APPRISE_ALERTS = APPRISE_ALERTS.split(",")

HANDLE_DRIVER = os.environ.get("HANDLE_DRIVER", "False")

if (HANDLE_DRIVER == "True"):
    HANDLE_DRIVER = True
else:
    HANDLE_DRIVER = False

# Methods
def apprise_init():
    if APPRISE_ALERTS:
        alerts = apprise.Apprise()
        # Add all services from .env
        for service in APPRISE_ALERTS:
            alerts.add(service)
        return alerts

def login(EMAIL, PASSWORD, driver):
    driver.maximize_window()
    driver.find_element(By.XPATH, value='//*[@id="i0116"]').send_keys(EMAIL)
    driver.find_element(By.XPATH, value='//*[@id="i0116"]').send_keys(Keys.ENTER)
    time.sleep(2)
    driver.find_element(By.XPATH, value='//*[@id="i0118"]').send_keys(PASSWORD)
    driver.find_element(By.XPATH, value='//*[@id="i0118"]').send_keys(Keys.ENTER)
    time.sleep(3)
    driver.find_element(By.XPATH, value='//*[@id="idSIButton9"]').click()

def completeSet(driver):
    time.sleep(15)
    try:
        driver.find_element(By.XPATH, value='/html/body/div[2]/div[2]/span/a').click()
        time.sleep(8)
        driver.refresh()
        print('\tExplore completed!')
    except:
        driver.refresh()
        pass
    return

def completePoll(driver):
    try:
        driver.refresh()
        try:
            time.sleep(5)
            driver.find_element(By.XPATH, value='/html/body/div[2]/div[2]/span/a').click()
        except:
            driver.refresh()
            pass
        time.sleep(5)
        driver.find_element(By.XPATH, value='//*[@id="btoption0"]/div[2]/div[2]').click()
        time.sleep(8)
        print('\tPoll completed!')
    except:
        pass
    time.sleep(3)
    return

def completeQuiz(driver):
    time.sleep(10)
    try:
        driver.find_element(By.XPATH, value='/html/body/div[2]/div[2]/span/a').click()
        time.sleep(4)
    except:
        pass
    driver.refresh()
    try:
        numberOfQuestions = (driver.find_element(By.XPATH, value='//*[@id="QuestionPane0"]/div[2]').text.strip().split("of ")[1])[:-1]
        # numberOfQuestions = numberOfQuestions[:-1]
        for i in range(int(numberOfQuestions)):
            driver.find_element(By.CLASS_NAME, value='wk_OptionClickClass').click()
            time.sleep(8)
            driver.find_element(By.CLASS_NAME, value='wk_buttons').find_elements(By.XPATH, value='*')[0].send_keys(Keys.ENTER)
            time.sleep(5)
        print('\tQuiz completed!')
        return
    except Exception as e:
        pass
    
    if (driver.find_elements(By.XPATH, value='//*[@id="rqStartQuiz"]') or driver.find_elements(By.CLASS_NAME, value='btOptions') or driver.find_elements(By.XPATH, value='//*[@id="currentQuestionContainer"]/div/div[1]/span/span')):
        try:
            driver.find_element(By.XPATH, value='//*[@id="rqStartQuiz"]').click()
        except:
            pass
        try:
            time.sleep(3)
            if (driver.find_elements(By.XPATH, value='//*[@id="rqHeaderCredits"]')):
                section = len(driver.find_element(By.XPATH, value='//*[@id="rqHeaderCredits"]').find_elements(By.XPATH, value='*'))
                for i in range(section):
                    choices = driver.find_element(By.XPATH, value='//*[@id="currentQuestionContainer"]/div/div[1]/span/span').text
                    choices = int(choices[-1]) - int(choices[0])
                    try:
                        for i in range(choices * 2):
                            time.sleep(5)
                            option = driver.find_element(By.XPATH, value=f'//*[@id="rqAnswerOption{i}"]')
                            if (option.get_attribute('iscorrectoption') == 'True'):
                                option.click()
                    except Exception:
                        continue
                print('\tQuiz completed!')
                return

            elif (driver.find_elements(By.XPATH, value='//*[@id="currentQuestionContainer"]/div/div/div[2]/div[4]')):
                numberOfQuestions = driver.find_element(By.XPATH, value='//*[@id="currentQuestionContainer"]/div/div/div[2]/div[4]').text.strip().split("of ")[1]
                for i in range(int(numberOfQuestions)):
                    driver.find_element(By.CLASS_NAME, value='btOptionCard').click()
                    time.sleep(13)
                print('\tQuiz completed!')
                return
        except Exception as e:
            print(e)
            pass

def completeMore(driver):
    ran = False
    driver.get('https://rewards.microsoft.com/')
    try:
        count = len(driver.find_elements(By.CLASS_NAME, 'ds-card-sec')) - 6
        #for i in range(15):
        for i in range(count):
            i+=1
            try:
                element = driver.find_element(By.XPATH, value=f'/html/body/div[1]/div[2]/main/div/ui-view/mee-rewards-dashboard/main/div/mee-rewards-more-activities-card/mee-card-group/div/mee-card[{i}]')
            except Exception as e:
                pass
            try:
                extra = element.find_element(By.XPATH, value=f'/html/body/div[1]/div[2]/main/div/ui-view/mee-rewards-dashboard/main/div/mee-rewards-more-activities-card/mee-card-group/div/mee-card[{i}]/div/card-content/mee-rewards-more-activities-card-item/div/a/mee-rewards-points/div/div/span[1]')
                class_name = extra.get_attribute('class')

                if (class_name == "mee-icon mee-icon-AddMedium" or class_name == "mee-icon mee-icon-HourGlass"):
                    assign = driver.find_element(By.XPATH, value=f'//*[@id="more-activities"]/div/mee-card[{i}]/div/card-content/mee-rewards-more-activities-card-item/div/a')
                    p = driver.current_window_handle
                    assign.click()

                    chwd = driver.window_handles
                    if (chwd[1]):
                        driver._switch_to.window(chwd[1])
                        try:
                            try:
                                completeQuiz(driver)
                                driver.close()
                                driver._switch_to.window(p)
                                driver.refresh()
                                ran = True
                                continue
                            except:
                                pass
                            try:
                                completeSet(driver)
                                driver.close()
                                driver._switch_to.window(p)
                                driver.refresh()
                                ran = True
                                continue
                            except:
                                pass
                            try:
                                completePoll(driver)
                                driver.close()
                                driver._switch_to.window(p)
                                driver.refresh()
                                ran = True
                                continue
                            except:
                                driver.close()
                                driver._switch_to.window(p)
                                driver.refresh()
                                ran = True
                                pass
                        except:
                            print(traceback.format_exc())
                            pass
                        finally:
                            time.sleep(5)
                            driver.refresh()
                            time.sleep(5)
                    else:
                        driver.get('https://rewards.microsoft.com/')
            except:
                continue
    except Exception as e:
        print(traceback.format_exc())
        pass
    return ran

def dailySet(driver):
        ranSets = False
        try:
            if (driver.find_element(By.XPATH, value='//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[1]/div/card-content/mee-rewards-daily-set-item-content/div/a/mee-rewards-points/div/div/span[1]').get_attribute("class") == "mee-icon mee-icon-AddMedium"):
                p = driver.current_window_handle
                driver.find_element(By.XPATH, value='//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[1]/div/card-content/mee-rewards-daily-set-item-content/div/a').click()
                chwd = driver.window_handles
                driver._switch_to.window(chwd[1])
                completeSet(driver)
                driver.close()
                driver._switch_to.window(p)
                driver.refresh()
                ranSets = True
        except Exception as e:
            driver.get('https://rewards.microsoft.com/')
            print(e)
            pass

        try:
            if (driver.find_element(By.XPATH, value='//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[3]/div/card-content/mee-rewards-daily-set-item-content/div/a/mee-rewards-points/div/div/span[1]').get_attribute("class") == "mee-icon mee-icon-AddMedium"):
                p = driver.current_window_handle
                driver.find_element(By.XPATH, value='//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[3]/div/card-content/mee-rewards-daily-set-item-content/div/a').click()
                chwd = driver.window_handles
                driver._switch_to.window(chwd[1])
                completePoll(driver)
                driver.close()
                driver._switch_to.window(p)
                driver.refresh()
                ranSets = True
        except Exception as e:
            driver.get('https://rewards.microsoft.com/')
            print(e)
            pass
        try:
            if (driver.find_element(By.XPATH, value='//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[2]/div/card-content/mee-rewards-daily-set-item-content/div/a/mee-rewards-points/div/div/span[1]').get_attribute("class") == "mee-icon mee-icon-AddMedium" or driver.find_element(By.XPATH, value='//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[2]/div/card-content/mee-rewards-daily-set-item-content/div/a/mee-rewards-points/div/div/span[1]').get_attribute("class") =="mee-icon mee-icon-HourGlass"):
                p = driver.current_window_handle
                driver.find_element(By.XPATH, value='//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card[2]/div/card-content/mee-rewards-daily-set-item-content/div/a').click()
                chwd = driver.window_handles
                driver._switch_to.window(chwd[1])
                completeQuiz(driver)
                driver.close()
                driver._switch_to.window(p)
                driver.refresh()
                ranSets = True
        except Exception as e:
            driver.get('https://rewards.microsoft.com/')
            print(e)
            pass

        return ranSets

def getDriver(isMobile = False):
    if not HANDLE_DRIVER:
        chrome_options = Options()
    else:
        chrome_options = webdriver.ChromeOptions()

    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    if (isMobile):   
        mobile_emulation = {"deviceName": "Nexus 5"}
        chrome_options.add_experimental_option(
            "mobileEmulation", mobile_emulation)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    if not HANDLE_DRIVER:
        driver = webdriver.Chrome(options=chrome_options)
    else:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager(cache_valid_range=30).install()),
            options=chrome_options)

    return driver

def getPoints(EMAIL, PASSWORD, driver):
    points = -1
    driver.implicitly_wait(4)
    try:
        driver.get('https://rewards.microsoft.com/Signin?idru=%2F')
        login(EMAIL, PASSWORD, driver)
    except Exception as e:
        driver.get('https://rewards.microsoft.com/')
        print(e)
        pass
    finally:
        time.sleep(10)
    # Error arrises on return statement, therefore it is necessary to have reductant code
    try:
        points = driver.find_element(By.XPATH, '//*[@id="rewardsBanner"]/div/div/div[3]/div[1]/mee-rewards-user-status-item/mee-rewards-user-status-balance/div/div/div/div/div/p[1]/mee-rewards-counter-animation/span').text
        points = points.replace(',', '')
        return int(points)
    except:
        points = driver.find_element(By.XPATH, '//*[@id="rewardsBanner"]/div/div/div[2]/div[2]/span').text
        points = points.replace(',', '')
        pass
        return int(points)

def main():
    totalPointsReport = 0
    totalDifference = 0
    differenceReport = 0
    rw = RandomWords()
    delay = 6
    ranRewards = False
    for x in ACCOUNTS:
        driver = getDriver()

        # Grab email
        colonIndex = x.index(":")+1
        EMAIL = x[0:colonIndex-1]
        PASSWORD = x[colonIndex:len(x)]

        # Set default search amount
        Number_Mobile_Search = 20
        Number_PC_Search = 34

        # Retireve points before completing searches
        points = getPoints(EMAIL, PASSWORD, driver)
        print(f'Email:\t{EMAIL}\n\tPoints:\t{points}')
        driver.get('https://rewards.microsoft.com/pointsbreakdown')
        try:
            time.sleep(10)
            PC = driver.find_element(By.XPATH, value='//*[@id="userPointsBreakdown"]/div/div[2]/div/div[1]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]').text.replace(" ", "").split("/")
            
            if (int(PC[0]) < int(PC[1])):
                Number_PC_Search = int((int(PC[1]) - int(PC[0])) / 5)
                print(f'\tPC Searches Left:\t{Number_PC_Search}')
            else:
                Number_PC_Search = 0
                print(f'\tPC Searches Completed:\t{PC[0]}/{PC[1]}')

            if (int(PC[1]) > 50):
                MOBILE = driver.find_element(By.XPATH, value='//*[@id="userPointsBreakdown"]/div/div[2]/div/div[2]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]').text.replace(" ", "").split("/")
                if (int(MOBILE[0]) < int(MOBILE[1])):
                    Number_Mobile_Search = int((int(MOBILE[1]) - int(MOBILE[0])) / 5)
                    print(f'\tMobile Searches Left:\t{Number_Mobile_Search}')
                else:
                    Number_Mobile_Search = 0
                    print(f'\tMobile Searches Completed:\t{MOBILE[0]}/{MOBILE[1]}')
            else:
                Number_Mobile_Search = 0
            
            driver.find_element(By.XPATH, '//*[@id="modal-host"]/div[2]/button').click()
        except Exception as e:
            driver.get('https://rewards.microsoft.com/')
            print(e)
            pass
        finally:
            print()

        ranDailySets = False 
        ranMoreActivities = False

        ranDailySets = dailySet(driver)
        ranMoreActivities = completeMore(driver)

        if (Number_PC_Search > 0 or Number_Mobile_Search > 0 or ranDailySets or ranMoreActivities):
            ranRewards = True
            if APPRISE_ALERTS:
                alerts.notify(title=f'Bing Rewards Automation Starting', 
                            body=f'Email:\t\t{EMAIL} \nPoints:\t\t {points} \nCash Value:\t\t${round(points/1300, 2)}\n\n ')
            if (Number_PC_Search > 0):
                rw = RandomWords()
                driver.get(os.environ['URL'])
                # TO TRY:
                # driver.get('https://login.live.com/')
                driver.maximize_window()
                try:
                    login(EMAIL, PASSWORD, driver)
                except:
                    pass
                try:
                    driver.find_element(By.XPATH, value='//*[@id="mHamburger"]').click()
                    driver.find_element(By.XPATH, value='//*[@id="HBSignIn"]/a[1]').click()
                except Exception:
                    pass
                finally:
                    driver.get('https://www.bing.com/')

                try:
                    driver.find_element(By.ID, 'id_l').click()
                    time.sleep(2)
                    driver.refresh()
                except:
                    pass

                # First test search
                time.sleep(delay)
                first = driver.find_element(By.ID, value="sb_form_q")
                first.send_keys("test")
                first.send_keys(Keys.RETURN)

                # Main search loop
                for x in range(1, Number_PC_Search+1):
                    time.sleep(delay)
                    # Create string to send
                    value = random.choice(TERMS) + rw.random_word()

                    # Clear search bar
                    ping = driver.find_element(By.ID, value="sb_form_q")
                    ping.clear()

                    # Send random keyword
                    ping.send_keys(value)

                    # add delay to prevent ban
                    time.sleep(4)
                    try:
                        go = driver.find_element(By.ID, value="sb_form_go")
                        go.click()

                    except:
                        driver.find_element(By.ID, value="sb_form_go").send_keys(Keys.RETURN)
                        pass

                    # add delay to prevent ban
                    time.sleep(delay)
                    print(f'\t{x} PC search of {Number_PC_Search}. Now {int(x/Number_PC_Search*100)}% done.')
            driver.quit()

            if (Number_Mobile_Search > 0):
                rw = RandomWords()
                driver = getDriver(True)
                        
                driver.implicitly_wait(4)
                driver.get(os.environ['URL'])
                # TO TRY:
                # driver.get('https://login.live.com/')
                driver.maximize_window()

                try:
                    driver.find_element(By.XPATH, value='//*[@id="mHamburger"]').click()
                    driver.find_element(By.XPATH, value='//*[@id="HBSignIn"]/a[1]').click()
                except Exception:
                    pass

                login(EMAIL, PASSWORD, driver)
                print(f"\n\tAccount {EMAIL} logged in successfully! Auto search initiated.\n")
                driver.get('https://www.bing.com/')
                
                # Main search loop
                for x in range(1, Number_Mobile_Search + 1):
                    value = random.choice(TERMS) + rw.random_word()
                    try:
                        # Clear search bar
                        ping = driver.find_element(By.ID, value="sb_form_q")
                        ping.clear()

                        # Send random keyword
                        ping.send_keys(value)
                    except:
                        driver.get('https://www.bing.com/')

                        time.sleep(10)
                        # Clear search bar
                        ping = driver.find_element(By.ID, value="sb_form_q").send_keys(value)
                        pass
                    try:
                        # add delay to prevent ban
                        time.sleep(4)
                        go = driver.find_element(By.ID, value="sb_form_go")
                        go.click()
                    except Exception:
                        ping.send_keys(Keys.ENTER)
                        pass
                    time.sleep(delay)

                    print(f'\t{x} mobile search of {Number_Mobile_Search}. Now {int(x/Number_Mobile_Search*100)}% done.')

                print("\n\tAccount [" + EMAIL + "] has completed mobile searches]\n")

                driver.quit()

            driver = getDriver()
            driver.implicitly_wait(3)
            differenceReport = points
            points = getPoints(EMAIL, PASSWORD, driver)
            differenceReport = points - differenceReport
            print(f'Email:\t{EMAIL}\n\tPoints:\t{points}')
            if APPRISE_ALERTS:
                alerts.notify(title=f'Bing Rewards Automation Completed!', 
                    body=f'Email:\t\t\t{EMAIL} \nPoints:\t\t\t{points} \nEarned Points:\t\t\t{differenceReport} \nCash Value:\t\t${round(points / 1300, 2)}\n\n ')
                
        driver.quit()
        totalPointsReport += points
        totalDifferenceReport += differenceReport
        print(f'\n\n')
    if APPRISE_ALERTS and ranRewards:
        alerts.notify(title=f'Bing Rewards Automation Complete', 
                    body=f'Total Points (across all accounts):\t\t{totalPointsReport}\nCash Value of Total Points:\t\t${round(totalPointsReport/1300, 2)}\n\nTotal Earned (in latest run):\t\t{totalDifference}\nCash Value of Earned (in latest run):\t\t{round(totalDifference/1300, 2)}\n\n')
    #totalPointsReport = 0
    return

if __name__ == "__main__":
    if APPRISE_ALERTS:
        alerts = apprise_init()

    while True:
        try:
            main()
            print('Bing Automation complete. Sleeping for some time before resuming checks.')
            time.sleep(14400)
        except Exception as e:
            print(f"EXCEPTION: {e}\n\nTRACEBACK: {traceback.format_exc()}")

            if APPRISE_ALERTS:
                alerts.notify(title=f'Bing Rewards Failed!',
                        body=f'EXCEPTION: {e} \n\n{traceback.format_exc()} \nAttempting to restart...\n\n ')

            time.sleep(600)
            continue
