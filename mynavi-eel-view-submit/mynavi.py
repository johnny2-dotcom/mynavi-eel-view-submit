# import os
from selenium import webdriver
from selenium.webdriver import Chrome, ChromeOptions
import time 
import pandas as pd
from datetime import  datetime
# from selenium.webdriver.chrome.webdriver import WebDriver
# from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
import eel

LOG_FILE_PATH = 'log/log_{datetime}.log'
EXP_CSV_PATH = 'exp_list_{search_keyword}_{datetime}.csv'
log_file_path = LOG_FILE_PATH.format(datetime=datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))

### Chromeを起動する関数
def set_driver(driver_path,headless_flg):
    options = ChromeOptions()

    if headless_flg == True:
        options.add_argument('--headless')
    
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')  # シークレットモードの設定を付与

    return Chrome(ChromeDriverManager().install(),options=options)

### ログファイルおよびコンソール出力
def log(txt):
    now = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    logStr = '[log: {}] {}'

    with open(log_file_path,'a',encoding='utf-8_sig') as f:
        f.write(logStr.format(now,txt)+'\n')
    print(logStr.format(now,txt))
    eel.view_log(logStr.format(now,txt))

# tableのthからtargetの文字列を探し一致する行のtdを返す
def find_table_target_word(th_elms,td_elms,target:str):
    for th_elm,td_elm in zip(th_elms,td_elms):
        if th_elm.text == target:
            return td_elm.text

### main処理
# @eel.expose
def main(search_keyword):
    if search_keyword == '':
        print('検索ワードを入力してください。')
        eel.view_log('検索ワードを入力してください。')
    else:
        log('処理開始')
        # search_keyword = input('検索キーワードを入力してください：')
        log('検索キーワード：{}'.format(search_keyword))
        # driverを起動 Webサイトを開く
        driver = set_driver('chromedriver.exe',False)
        driver.get('https://tenshoku.mynavi.jp/')
        time.sleep(3)
        try:
            # ポップアップを閉じる（seleniumだけではクローズできない）
            driver.execute_script('document.querySelector(".karte-close").click()')
            time.sleep(5)
            driver.execute_script('document.querySelector(".karte-close").click()')
            time.sleep(3)
        except:
            pass

        # 検索窓に入力 検索ボタンクリック
        driver.find_element_by_class_name('topSearch__text').send_keys(search_keyword)
        driver.find_element_by_class_name('topSearch__button').click()

        exp_name_list = []
        exp_copy_list = []
        exp_status_list = []
        exp_first_year_fee_list = []
        count = 0
        success = 0
        fail = 0
        while True:
            name_list = driver.find_elements_by_css_selector(".cassetteRecruit__heading .cassetteRecruit__name")
            copy_list = driver.find_elements_by_css_selector(".cassetteRecruit__heading .cassetteRecruit__copy")
            status_list = driver.find_elements_by_css_selector(".cassetteRecruit__heading .labelEmploymentStatus")
            table_list = driver.find_elements_by_css_selector(".cassetteRecruit .tableCondition") # テーブル全体を取得

            for name,copy,status,table in zip(name_list,copy_list, status_list,table_list):
                try:
                    exp_name_list.append(name.text)
                    exp_copy_list.append(copy.text)
                    exp_status_list.append(status.text)

                    first_year_fee = find_table_target_word(table.find_elements_by_tag_name("th"), table.find_elements_by_tag_name("td"), "初年度年収")
                    exp_first_year_fee_list.append(first_year_fee)

                    log(f'{count}件目成功 : {name.text}')
                    success += 1
                except Exception as e:
                    log(f'{count}件目失敗 : {name.text}')
                    log(e)
                    fail += 1
                finally:
                    # finallyは成功の時もエラーの時も関係なく必ず実行する処理。ここでは必ずcountに１をプラスして総合回数を記録する処理。
                    count += 1
            
            # 「次へ」の"iconFont--arrowLeft"は各ページに１個しかないが、あえて、find_elementsの複数形で取って、next_pageに代入する。len(next_page)は実質上１であるが、１以上の時とそれ以外の時（存在しない時）で条件分岐してページ遷移を判断している。tryで単数形のfind_elementで取ってきて、存在しない時をexceptにしても、処理は可能であるが、あくまでもエラーが発生したわけではないので、tryにするよりも、ifで処理すべきであるので、条件分岐出来るようにあえて複数形で取ってきている。
            next_page = driver.find_elements_by_class_name("iconFont--arrowLeft")
            if len(next_page) >= 1:
                next_page_link = next_page[0].get_attribute("href")
                driver.get(next_page_link)
            else:
                log("最終ページです。終了します。")
                break

        now = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        df = pd.DataFrame({"企業名":exp_name_list,
                        "キャッチコピー":exp_copy_list,
                        "ステータス":exp_status_list,
                        "初年度年収":exp_first_year_fee_list})
        df.to_csv(EXP_CSV_PATH.format(search_keyword=search_keyword,datetime=now), encoding="utf-8-sig")
        log(f'処理完了　総件数: {count}件 / 成功件数: {success}件 / 失敗件数: {fail}件')

# if __name__ == '__main__':
#     main()
# eel.init('html')
# eel.start('index.html')

