import requests
import os
import json
import re

class ChungKhoanApp:
    HOSE_SYMBOLS = "hose_symbols.json"
    SYMBOL_DATA = "symbol_data.txt"
    def __init__(self):
        self.s = requests.Session()
        self.s.headers.update({
            
           "Device-Id": "756752CB-6DB4-41C5-819D-F55269D33576",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": '?0',
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.hose_symbols = self.get_hose_symbols()
        
        pass

    def get_hose_symbols(self) -> list:
        if os.path.exists(ChungKhoanApp.HOSE_SYMBOLS):
            with open(ChungKhoanApp.HOSE_SYMBOLS, "r", encoding="utf-8") as f:
                data = json.loads(f.read())
                hose_symbols = [i['s'] for i in data['data']]
                print("len(hose_symbols)", len(hose_symbols))
                return hose_symbols
    
    def get_eps_year(self):

        if os.path.exists(ChungKhoanApp.SYMBOL_DATA):
            with open(ChungKhoanApp.SYMBOL_DATA, "w", encoding="utf-8") as f:
                symbol_data = [json.loads(i[:-1]) for i in f.readlines()]
                return symbol_data

    
        
        symbol_data = []
        for symbol in self.hose_symbols:
            index = self.s.get(f"https://finance.vietstock.vn/{symbol}/tai-chinh.htm?tab=BCTT")
            __RequestVerificationToken = re.findall('__RequestVerificationToken type=hidden value=(.*?)>', index.text, re.S|re.I)[0]
            payload_pre = {
                "StockCode": symbol,
"UnitedId": "-1",
"AuditedStatusId": "-1",
"Unit": "1000000000",
"IsNamDuongLich": "false",
"PeriodType": "NAM",
"SortTimeType": "Time_ASC",
"__RequestVerificationToken": __RequestVerificationToken
            }
            aa = self.s.post("https://finance.vietstock.vn/data/BCTT_GetListReportData", data=payload_pre)
            aa = json.loads(aa.text)['data']
            print(aa[-5]['ReportDataID'])
            print(aa[-4]['ReportDataID'])
            print(aa[-3]['ReportDataID'])
            print(aa[-2]['ReportDataID'])
            print(aa[-1]['ReportDataID'])
            payload = {
                "StockCode": symbol,
"Unit": "1000000000",
"listReportDataIds[0][Index]": "0",
"listReportDataIds[0][ReportDataId]": aa[-5]['ReportDataID'],
"listReportDataIds[0][IsShowData]": "true",
"listReportDataIds[0][RowNumber]": "8",
"listReportDataIds[0][YearPeriod]": "2018",
"listReportDataIds[0][TotalCount]": "12",
"listReportDataIds[0][SortTimeType]": "Time_ASC",
"listReportDataIds[1][Index]": "1",
"listReportDataIds[1][ReportDataId]": aa[-4]['ReportDataID'],
"listReportDataIds[1][IsShowData]": "true",
"listReportDataIds[1][RowNumber]": "9",
"listReportDataIds[1][YearPeriod]": "2019",
"listReportDataIds[1][TotalCount]": "12",
"listReportDataIds[1][SortTimeType]": "Time_ASC",
"listReportDataIds[2][Index]": "2",
"listReportDataIds[2][ReportDataId]": aa[-3]['ReportDataID'],
"listReportDataIds[2][IsShowData]": "true",
"listReportDataIds[2][RowNumber]": "10",
"listReportDataIds[2][YearPeriod]": "2020",
"listReportDataIds[2][TotalCount]": "12",
"listReportDataIds[2][SortTimeType]": "Time_ASC",
"listReportDataIds[3][Index]": "3",
"listReportDataIds[3][ReportDataId]": aa[-2]['ReportDataID'],
"listReportDataIds[3][IsShowData]": "true",
"listReportDataIds[3][RowNumber]": "11",
"listReportDataIds[3][YearPeriod]": "2021",
"listReportDataIds[3][TotalCount]": "12",
"listReportDataIds[3][SortTimeType]": "Time_ASC",
"listReportDataIds[4][Index]": "4",
"listReportDataIds[4][ReportDataId]": aa[-1]['ReportDataID'],
"listReportDataIds[4][IsShowData]": "true",
"listReportDataIds[4][RowNumber]": "12",
"listReportDataIds[4][YearPeriod]": "2022",
"listReportDataIds[4][TotalCount]": "12",
"listReportDataIds[4][SortTimeType]": "Time_ASC",
"__RequestVerificationToken":  __RequestVerificationToken
            }

            res = self.s.post("https://finance.vietstock.vn/data/BCTT_GetListReportData", data=payload)
            data = json.loads(res.text)
            eps_list = []
            pe_list = []

            print(symbol, data)
            print("===========")
            for i in data:
                if i['ReportNormId'] == "53": #EPS
                    for j in range(1, 6):
                        eps_list.append(i[f"Value{j}"])

                if i['ReportNormId'] == "55": #P/E
                    for j in range(1, 6):
                        pe_list.append(i[f"Value{j}"])

            my_data = {"symbol": symbol, "eps_list": eps_list, "pe_list": pe_list}
            print(my_data)
            symbol_data.append(my_data)

            with open(ChungKhoanApp.SYMBOL_DATA, "a", encoding="utf-8") as f:
                f.write(my_data)
                f.write("\n")
        return symbol_data


    def get_pe_year(self):
        pass

if __name__ == "__main__":
    app = ChungKhoanApp()
    symbol_data = app.get_eps_year()
    for i in symbol_data:
        print(i)