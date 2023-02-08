import requests
from fake_useragent import UserAgent
import re
import os

import sys
import time
from bs4 import BeautifulSoup
from selenium import webdriver
import random
import paramiko

def mkdir_p(sftp, remote_directory):
    """Change to this directory, recursively making new folders if needed.
    Returns True if any folders were created."""
    if remote_directory == '/':
        # absolute path so change directory to root
        sftp.chdir('/')
        return
    if remote_directory == '':
        # top-level relative directory must exist
        return
    try:
        sftp.chdir(remote_directory) # sub-directory exists
    except IOError:
        dirname, basename = os.path.split(remote_directory.rstrip('/'))
        mkdir_p(sftp, dirname) # make parent directories
        sftp.mkdir(basename) # sub-directory missing, so created it
        sftp.chdir(basename)
        return True

def deal_with_page(html):
    file_str = html
    file_split = file_str.split('<div data-asin="')
    ind = 1
    ASIN_arr = []
    for block in file_split:
        block_split = block.split('" data-index="')
        if len(block_split) < 2:
            continue
        if (block_split[0]==''):
            continue

        #price
        price_low = 0
        price_high = 0
        price_split_0 = block_split[1].split('<span class="a-offscreen">$')
        if len(price_split_0) > 2:
            pricel_split = price_split_0[1].split('</span><span aria-hidden="true">')
            priceh_split = price_split_0[2].split('</span><span aria-hidden="true">')
            if len(pricel_split) > 1:
                price_low = float(pricel_split[0].replace(',',''))
            price_high = price_low
            if len(priceh_split) > 1:
                price_high = float(priceh_split[0].replace(',',''))
        elif len(price_split_0) > 1:
            price_split = price_split_0[1].split('</span><span aria-hidden="true">')
            if len(price_split) > 1:
                price_low = float(price_split[0].replace(',',''))
            price_high = price_low

        ##review number
        rate = 0.0
        review_num = 0
        review_num_split = block_split[1].split('class="a-row a-size-small"')
        if len(review_num_split) > 1:
            r_n_splits = review_num_split[1].split('<span aria-label="')
            if len(r_n_splits)>2:
                rate_part = r_n_splits[1]
                rate_split = rate_part.split(' out of')
                if len(rate_split) > 1:
                    rate = float(rate_split[0])

                reviewNum_part = r_n_splits[2]
                reviewNum_split = reviewNum_part.split('"><')
                if len(reviewNum_split) > 1:
                    review_num = int(reviewNum_split[0].replace(',',''))

        ##check ad
        adcheck = block_split[1].split('SponsoredProductsEventTracking')
        ifad = 0
        if len(adcheck) > 1:
            ifad = 1
        ASIN_arr.append([ifad,block_split[0],rate,review_num,price_low,price_high])
        ind += 1
    f.close()
    return ASIN_arr


def parse_cookie(filename):
    f = open(filename)
    f.readline()
    f.readline()
    f.readline()
    f.readline()
    ourstirng = ''

    for line in f:
        line = line[:-1]
        line_split = line.split('  ')
        ourstirng += line_split[-2]+'='+line_split[-1]+';'

    ourstirng = ourstirng[:-1]
    return ourstirng

def ua():
    cookie_file1 = '/Users/yipengm/PycharmProjects/AMZ_LIB/AMZ_COOKIE_POOL/amazon1'
    cookie_file2 = '/Users/yipengm/PycharmProjects/AMZ_LIB/AMZ_COOKIE_POOL/amazon2'
    cookie_file3 = '/Users/yipengm/PycharmProjects/AMZ_LIB/AMZ_COOKIE_POOL/amazon3'

    ua=UserAgent()
    headers1={
        'User-Agent':ua.random,
        'Cookie': parse_cookie(cookie_file1)
    }
    headers2 = {
        'User-Agent': ua.random,
        'Cookie':parse_cookie(cookie_file2)
    }
    headers3 = {
        'User-Agent': ua.random,
        'Cookie':parse_cookie(cookie_file3)
    }

    p = random.random()
    if p < 1/3:
        return headers1,1
    elif p < 2/3:
        return headers2,2
    else:
        return headers3,3



if __name__ == "__main__":

    ####################
    date = 'PST_2021_12_27_4_23_00'
    mode = 'PS'
    ###################
    machinename = '192.168.3.12'
    user = 'yipengm'
    pw = 'Shabbyed12'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(machinename, username=user,password=pw)
    sftp = ssh.open_sftp()



    filename = 'word_' + mode
    f = open(filename)

    driver = webdriver.Chrome(
        '/Users/yipengm/Downloads/chromedriver')  # 创建一个driver用于打开网页，记得找到brew安装的chromedriver的位置，在创建driver的时候指定这个位置

    search_dict = dict()
    adstuck_flag = 0
    webstuck_flag = 0
    for line in f:
        line_r = line[:-1]
        search_dict[line_r] = 0

    for k, v in search_dict.items():
        print(k)
        kw = k
        kw_sep = kw.split(' ')
        kw_reassemble = ''
        for kwsep in kw_sep:
            kw_reassemble += '+'+kwsep
        kw_reassemble = kw_reassemble[1:]

        timenow = int(time.time())
        i = 0
        path = '/Users/yipengm/PycharmProjects/AMZ_LIB/' + date + '/' + mode + '/' + kw_reassemble + '_collect/'

        block_num = 0
        while i < 7:
            scratch_file_path = path+kw_reassemble+'_page'+str(i+1)
            scratch_latter = kw_reassemble+'_page'+str(i+1)
            #fw = open(scratch_file_path,'w+')
            url = 'https://www.amazon.com/s?k=' + kw_reassemble + '+cup&page='+str(i+1)
            driver.get(url)
            html = driver.page_source

            soup = BeautifulSoup(driver.page_source, "html.parser")
            ###html = requests.get(url, headers=header, timeout=10).content.decode('utf-8')
            #print(html, file=fw)
            print(timenow)
            print('page' + str(i))
            if len(re.findall('please contact api-services-support@amazon.com',html,re.S)) > 0:
                print('blocked')
                block_num+=1
                time.sleep(1)
                sleepTimeBase = random.randint(30, 100)
                sleepTime = sleepTimeBase / 1.0
                time.sleep(sleepTime)
                if block_num > 5:
                    print(header['Cookie'])
                    break

                if block_num > 3:
                    print(header['Cookie'])
                    header,rand_ind = ua()
                continue

            ASIN_arr = deal_with_page(html)

            sleepTimeBase = random.randint(3,10)
            sleepTime = sleepTimeBase/10.0
            time.sleep(sleepTime)

            if len(ASIN_arr) > 1 :
                if len(ASIN_arr[0]) > 1 and len(ASIN_arr[1]) > 1:
                    webstuck_flag = 0

            elif webstuck_flag > 3:
                webstuck_flag = 0
                i+=1
                continue

            else:
                webstuck_flag+=1
                continue


            if ASIN_arr[0][0] == 1 or ASIN_arr[1][0] == 1 or adstuck_flag > 1:
                remote_path = '/media/yipengm/New Volume1/luosi_data/' + date + ' / ' + mode + ' / ' + kw_reassemble + '_collect/'
                mkdir_p(sftp,remote_path)
                ArrPath = remote_path + kw_reassemble + '_page' + str(i + 1) + '_arr'
                fw_arr = sftp.open(ArrPath,'w+')
                for arr in ASIN_arr:
                    print("ASIN:"+str(arr[1])+",IsAd:"+str(arr[0])+",PriceLow:"+str(arr[4])+",PriceHigh:"+str(arr[5])+",score:"+str(arr[2])+",review_num:"+str(arr[3]),file=fw_arr)
                i = i + 1
                adstuck_flag = 0
                fw_arr.close()
            else:
                adstuck_flag+=1
            time.sleep(0.5)

            if block_num > 5:
                print(kw_reassemble)
                break