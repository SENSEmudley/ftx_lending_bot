import pandas as pd
import json
import csv
import time
from datetime import datetime
import ccxt
import random
from dateutil import parser

# INPUT PARAMETER ========================================================================================== #
apiKey              = ""   
secret              = ""
subacc              = ""
pair                = "XRP/USD"
token_name          = "XRP"
# LENDING ================================================================================================== #
lending_mode        = "manual"    # "auto" or "manual"
time_check_lending  = ["11:30","21:30","21:09","21:40"]
lending_spot        = {'status':True,'percent_lending':70}
lending_cash        = {'status':False,'percent_lending':70}
lending_csv         = "lending_history.csv"
time_sleep          = 60        # min
# ========================================================================================================== #
exchange            = ccxt.ftx({'apiKey':apiKey, 'secret':secret, 'enableRateLimit':True})
exchange.headers    = {'FTX-SUBACCOUNT':subacc,}
# ========================================================================================================== #
def check_lending_csv():
    try:
        df_lending    = pd.read_csv(lending_csv)
    except:
        df_lending    = pd.DataFrame(columns=["coin","time","size","rate","proceeds","feeUsd"])
        df_lending.to_csv(lending_csv,index=False)
    return df_lending

def get_wallet_details():
    wallet = exchange.privateGetWalletBalances()['result']
    return wallet

def get_asset_qty():
    net_size_asset = 0
    for i in range(len(wallet)) :
        if wallet[i]["coin"] == token_name :
            net_size_asset = wallet[i]['total']
    if net_size_asset == 0:
        print("no asset in port, please check your portfolio")
    return float(net_size_asset)

def get_cash():
    for i in range(len(wallet)) :
        if wallet[i]["coin"] == "USD" :
            cash    = wallet[i]['usdValue']
    return float(cash)

def lending():
    now_hour    = int(datetime.now().strftime("%H"))
    now_min     = int(datetime.now().strftime("%M"))
    
    # LENDING
    if lending_mode == "auto":
        for i in range(len(time_check_lending)) :
            time_split = time_check_lending[i].split(":")
        if (now_hour == int(time_split[0]) and now_min == int(time_split[1])):
            if lending_spot['status'] == True :
                lending_qty = (lending_spot['percent_lending']*asset_qty)/100
                lending_res = exchange.private_post_spot_margin_offers(params={"coin":token_name,"size":lending_qty,"rate":1e-6})
                print('lending_spot_response :',lending_res)
                print('lending_spot_success')
            elif lending_spot['status'] == False :
                lending_qty = 0
                lending_res = exchange.private_post_spot_margin_offers(params={"coin":token_name,"size":lending_qty,"rate":1e-6})
                print('lending_spot_response :',lending_res)
                print('cancel_lending_spot')

            if lending_cash['status'] == True :
                lending_qty = (cash*lending_cash['percent_lending'])/100
                lending_res = exchange.private_post_spot_margin_offers(params={"coin":'USD',"size":lending_qty,"rate":1e-6})
                print('lending_cash_response :',lending_res)
                print('lending_cash_success')
            elif lending_cash['status'] == False :
                lending_qty = 0
                lending_res = exchange.private_post_spot_margin_offers(params={"coin":'USD',"size":lending_qty,"rate":1e-6})
                print('lending_cash_response :',lending_res)
                print('cancel_lending_cash')

    elif lending_mode == "manual":
            if lending_spot['status'] == True :
                lending_qty = (lending_spot['percent_lending']*asset_qty)/100
                lending_res = exchange.private_post_spot_margin_offers(params={"coin":token_name,"size":lending_qty,"rate":1e-6})
                print('lending_spot_response :',lending_res)
                print('lending_spot_success')
            elif lending_spot['status'] == False :
                lending_qty = 0
                lending_res = exchange.private_post_spot_margin_offers(params={"coin":token_name,"size":lending_qty,"rate":1e-6})
                print('lending_spot_response :',lending_res)
                print('cancel_lending_spot')

            if lending_cash['status'] == True :
                lending_qty = (cash*lending_cash['percent_lending'])/100
                lending_res = exchange.private_post_spot_margin_offers(params={"coin":'USD',"size":lending_qty,"rate":1e-6})
                print('lending_cash_response :',lending_res)
                print('lending_cash_success')
            elif lending_cash['status'] == False :
                lending_qty = 0
                lending_res = exchange.private_post_spot_margin_offers(params={"coin":'USD',"size":lending_qty,"rate":1e-6})
                print('lending_cash_response :',lending_res)
                print('cancel_lending_cash')

    # PENDING
    # lending_offers  = pd.DataFrame(exchange.private_get_spot_margin_offers()['result'])
    # print(lending_offers)
    # print("=============================================================")

    # HISTORY
    lending_history     = pd.DataFrame(exchange.private_get_spot_margin_lending_history()['result'])
    df_lending_his      = pd.read_csv(lending_csv)
    list_lending_his    = df_lending_his['time'].values.tolist()
    for i in range (len(lending_history)):
        if lending_history['time'].iloc[i] not in list_lending_his :
            with open(lending_csv, "a+", newline='') as fp:
                wr = csv.writer(fp, dialect='excel')
                wr.writerow(lending_history.iloc[i])
    # print(lending_history)
    # print("=============================================================")

def print_lending_summarize():
    df_lending_db   = pd.read_csv(lending_csv)
    lending_info    = pd.DataFrame(exchange.private_get_spot_margin_lending_info()['result'])
    lending_info    = pd.concat([lending_info[lending_info['coin'] == token_name],lending_info[lending_info['coin'] == 'USD']])
    interest_spot   = df_lending_db[df_lending_db['coin'] == token_name]['proceeds'].sum()
    interest_cash   = df_lending_db[df_lending_db['coin'] == 'USD']['proceeds'].sum()

    print("asset_in_port :",round(asset_qty,4),token_name)
    print("cash_in_port  :",round(cash,4),"USD")
    print('interest_spot :',round(interest_spot,4),token_name)
    print('interest_cash :',round(interest_cash,4),'USD')
    print('lending_info  :')
    print(lending_info)

while True :
    wallet      = get_wallet_details()
    df_lending  = check_lending_csv()
    cash        = get_cash()
    asset_qty   = get_asset_qty()

    lending()
    print_lending_summarize()

    time.sleep(60*time_sleep)