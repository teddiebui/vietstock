import requests
import json
import re
import os
import time
s = requests.Session()
s.headers.update({
    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
"Sec-Ch-Ua-Mobile": "?0",
"Sec-Ch-Ua-Platform": '"Windows"',
"Sec-Fetch-Dest": "document",
"Sec-Fetch-Mode": "navigate",
"Sec-Fetch-Site": "none",
"Sec-Fetch-User": "?1",
"Upgrade-Insecure-Requests": "1",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})
FINANCE_DATA_Q = "finance_index_q.txt"
FINANCE_DATA_YEAR = "finance_index_year.txt"
HOSE_SYMBOL = "hose_symbols.json"

def get_symbols():
    z = []
    with open(HOSE_SYMBOL, "r", encoding="utf-8") as f:
        data = json.loads(f.read())
        symbols = [i['ss'] for i in data['data']]

        for i in symbols:
            print(i)
        print("haha")
        return symbols

def get_html(symbol):
    url = f"https://finance.vietstock.vn/search-stock"
    pl = {
        "query": symbol,
        "page": "1",
        "pageSize": "5",
        "skip": "0"
    }
    res = s.get(url, params=pl)
    json_data = json.loads(res.text)

    return json_data

def get_finance_html(symbol):
    res = s.get(f"https://finance.vietstock.vn/{symbol}/tai-chinh.htm?tab=BCTT")
    
    __RequestVerificationToken = re.findall(r"name=__RequestVerificationToken type=hidden value=(.*?)>", res.text)

    # print(__RequestVerificationToken)
    # print(res.request.url)
    return res.text.replace("\r", ""), __RequestVerificationToken[0]

def get_finance_info_as_json(symbol: str, __RequestVerificationToken: str)-> json:
    index_payload = {
        "StockCode": symbol,
        "UnitedId": "-1",
        "AuditedStatusId": "-1",
        "Unit": "1000000",
        "IsNamDuongLich": "false",
        "PeriodType": "QUY",
        "SortTimeType": "Time_ASC",
        "__RequestVerificationToken": __RequestVerificationToken
    }
    index = s.post("https://finance.vietstock.vn/data/BCTT_GetListReportData", data=index_payload)
    temp_data = json.loads(index.text)


    post_url = "https://finance.vietstock.vn/data/GetReportDataDetailValue_BCTT_ByReportDataIds"
    payload = {
        "StockCode": symbol,
        "Unit": "1000000",
        "listReportDataIds[0][Index]": "0",
        "listReportDataIds[0][ReportDataId]": temp_data['data'][-5]['ReportDataID'],
        "listReportDataIds[0][IsShowData]": "true",
        "listReportDataIds[0][RowNumber]": "71",
        "listReportDataIds[0][YearPeriod]": "2022",
        "listReportDataIds[0][TotalCount]": "75",
        "listReportDataIds[0][SortTimeType]": "Time_ASC",
        "listReportDataIds[1][Index]": "1",
        "listReportDataIds[1][ReportDataId]": temp_data['data'][-4]['ReportDataID'],
        "listReportDataIds[1][IsShowData]": "true",
        "listReportDataIds[1][RowNumber]": "72",
        "listReportDataIds[1][YearPeriod]": "2022",
        "listReportDataIds[1][TotalCount]": "75",
        "listReportDataIds[1][SortTimeType]": "Time_ASC",
        "listReportDataIds[2][Index]": "2",
        "listReportDataIds[2][ReportDataId]": temp_data['data'][-3]['ReportDataID'],
        "listReportDataIds[2][IsShowData]": "true",
        "listReportDataIds[2][RowNumber]": "73", 
        "listReportDataIds[2][YearPeriod]": "2023", 
        "listReportDataIds[2][TotalCount]": "75", 
        "listReportDataIds[2][SortTimeType]": "Time_ASC", 
        "listReportDataIds[3][Index]": "3", 
        "listReportDataIds[3][ReportDataId]": temp_data['data'][-2]['ReportDataID'], 
        "listReportDataIds[3][IsShowData]": "true", 
        "listReportDataIds[3][RowNumber]": "74", 
        "listReportDataIds[3][YearPeriod]": "2023", 
        "listReportDataIds[3][TotalCount]": "75", 
        "listReportDataIds[3][SortTimeType]": "Time_ASC", 
        "listReportDataIds[4][Index]": "4", 
        "listReportDataIds[4][ReportDataId]": temp_data['data'][-1]['ReportDataID'], 
        "listReportDataIds[4][IsShowData]": "true", 
        "listReportDataIds[4][RowNumber]": "75", 
        "listReportDataIds[4][YearPeriod]": "2023", 
        "listReportDataIds[4][TotalCount]": "75", 
        "listReportDataIds[4][SortTimeType]": "Time_ASC", 
        "__RequestVerificationToken": __RequestVerificationToken
    }
    res = s.post(post_url, data=payload)
    print(res, res.request.url)
    
    # print(payload)
    # print(res.text)
    data = json.loads(res.text)
    data['symbol'] = symbol
    return data

def get_and_save_data():
    symbols = get_symbols()

    if not os.path.exists(FINANCE_DATA_Q):
        for symbol in symbols:
            finance_index, __RequestVerificationToken = get_finance_html(symbol)
            finance_data = get_finance_info_as_json(symbol, __RequestVerificationToken)
            
            with open(FINANCE_DATA_Q, "a", encoding="utf-8") as f:
                f.write(json.dumps(finance_data))
                f.write("\n")
    
    else:
        with open(FINANCE_DATA_Q, "r", encoding="utf-8") as f:
            return [json.loads(i[:-1]) for i in f.readlines()]

def get_title():
    # CssStyle: "NormalB"
    # ReportNormId: 2216
    # ReportNormName: "Doanh thu thuần về bán hàng và cung cấp dịch vụ"
    # ReportTypeCode: "KQ"
    # ReportTypeName: "Kết quả kinh doanh"
    # Unit: ""
    
    if os.path.exists("report_title.json"):
        with open("report_title.json", "r", encoding="utf-8") as f:
            return json.loads(f.read())

def main():
    title = get_title()
    data = get_and_save_data()
    indexed_data = []
    for ticket in data:
        # with open("test.json", "w") as f:
        #     f.write(json.dumps(ticket))
        symbol = ticket['symbol']
        # if not symbol == "HDC":
        #     continue
        eps_data = []
        pe_data = []
        for i in ticket['data']:
            for k, v in i.items():
                if k == "ReportNormId" and v == 53:
                    # print(i)
                    for j in range(1,6):
                        # print(f"Value{j}")
                        value = i[f"Value{j}"]
                        if value == None:
                            eps_data.append(0)   
                            continue
                        eps_data.append(value)     
                        
                elif k == "ReportNormId" and v == 55:
                    for j in range(1,6):
                        # print(f"Value{j}")
                        value = i[f"Value{j}"]
                        if value == None:
                            pe_data.append(999)
                            continue
                        pe_data.append(value)  
        indexed_data.append({
            "symbol" : symbol,
            "eps_index": eps_data,
            "pe_index": pe_data
            })
    
    
    indexed_data.sort(key=lambda e: e['eps_index'][-1], reverse=True)
    
    for i in indexed_data[:]:
        if i['eps_index'][-1] > 0:  
            print(f"{i['symbol']} - {str(i['eps_index']):>55} - {str(i['pe_index']):>55}")

def get_finance_year_info_as_json():
    print("downloading..")
    symbols = get_symbols()

    whole_data = []
    for symbol in symbols:
        print(symbol)
        my_data = {}
        try:
            finance_index, __RequestVerificationToken = get_finance_html(symbol)
            index_payload = {
                "StockCode": symbol,
                "UnitedId": "-1",
                "AuditedStatusId": "-1",
                "Unit": "1000000",
                "IsNamDuongLich": "false",
                "PeriodType": "NAM",
                "SortTimeType": "Time_ASC",
                "__RequestVerificationToken": __RequestVerificationToken
            }
            index = s.post("https://finance.vietstock.vn/data/BCTT_GetListReportData", data=index_payload)
            temp_data = json.loads(index.text)

            post_url = "https://finance.vietstock.vn/data/GetReportDataDetailValue_BCTT_ByReportDataIds"
            payload = {
                "StockCode": symbol,
                "Unit": "1000000",
                "listReportDataIds[0][Index]": "0",
                "listReportDataIds[0][ReportDataId]": temp_data['data'][-5]['ReportDataID'],
                "listReportDataIds[0][IsShowData]": "true",
                "listReportDataIds[0][RowNumber]": "16",
                "listReportDataIds[0][YearPeriod]": "2018",
                "listReportDataIds[0][TotalCount]": "20",
                "listReportDataIds[0][SortTimeType]": "Time_ASC",
                "listReportDataIds[1][Index]": "1",
                "listReportDataIds[1][ReportDataId]": temp_data['data'][-4]['ReportDataID'],
                "listReportDataIds[1][IsShowData]": "true",
                "listReportDataIds[1][RowNumber]": "17",
                "listReportDataIds[1][YearPeriod]": "2019",
                "listReportDataIds[1][TotalCount]": "20",
                "listReportDataIds[1][SortTimeType]": "Time_ASC",
                "listReportDataIds[2][Index]": "2",
                "listReportDataIds[2][ReportDataId]": temp_data['data'][-3]['ReportDataID'],
                "listReportDataIds[2][IsShowData]": "true",
                "listReportDataIds[2][RowNumber]": "18", 
                "listReportDataIds[2][YearPeriod]": "2020", 
                "listReportDataIds[2][TotalCount]": "20", 
                "listReportDataIds[2][SortTimeType]": "Time_ASC", 
                "listReportDataIds[3][Index]": "3", 
                "listReportDataIds[3][ReportDataId]": temp_data['data'][-2]['ReportDataID'], 
                "listReportDataIds[3][IsShowData]": "true", 
                "listReportDataIds[3][RowNumber]": "19", 
                "listReportDataIds[3][YearPeriod]": "2021", 
                "listReportDataIds[3][TotalCount]": "20", 
                "listReportDataIds[3][SortTimeType]": "Time_ASC", 
                "listReportDataIds[4][Index]": "4", 
                "listReportDataIds[4][ReportDataId]": temp_data['data'][-1]['ReportDataID'], 
                "listReportDataIds[4][IsShowData]": "true", 
                "listReportDataIds[4][RowNumber]": "20", 
                "listReportDataIds[4][YearPeriod]": "2022", 
                "listReportDataIds[4][TotalCount]": "20", 
                "listReportDataIds[4][SortTimeType]": "Time_ASC", 
                "__RequestVerificationToken": __RequestVerificationToken
            }

            res = s.post(post_url, data=payload)
            
            my_data = json.loads(res.text)
            my_data["symbol"] = symbol
            whole_data.append(my_data)
        except:
            pass
        with open(FINANCE_DATA_YEAR, "a") as f:
            f.write(json.dumps(my_data))
            f.write("\n")
        

    return whole_data

def main2():
    if os.path.exists(FINANCE_DATA_YEAR):
        with open(FINANCE_DATA_YEAR, "r", encoding="utf-8") as f:
            my_data = [json.loads(i[:-1]) for i in f.readlines()]

    else:
        my_data = get_finance_year_info_as_json()
    
    for i in my_data:
        eps_list = []
        pe_list = []
        for m in i['data']:
            if m['ReportNormId']==53:
                eps_list = [m[f"Value{j}"] for j in range(1, 6)]
            if m["ReportNormId"]==55:
                pe_list = [m[f"Value{j}"] for j in range(1, 6)]
                
            then_data = {
                "symbol" : i['symbol'],
                "eps_index": eps_list,
                "pe_index": pe_list
                }
        print(then_data)



if __name__ == "__main__":  
    main2()
    


        
