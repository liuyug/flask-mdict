#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# dumpbin /exports TdxHqApi20991230.dll
# Microsoft (R) COFF/PE Dumper Version 14.00.23918.0
# Copyright (C) Microsoft Corporation.  All rights reserved.
#
#
# Dump of file TdxHqApi20991230.dll
# 
# File Type: DLL
# 
#   Section contains the following exports for TdxHqApi.dll
# 
#     00000000 characteristics
#     5642D37F time date stamp Wed Nov 11 13:34:55 2015
#         0.00 version
#            1 ordinal base
#           16 number of functions
#           16 number of names
# 
#     ordinal hint RVA      name
# 
#           1    0 00015FA0 TdxHq_Connect
#           2    1 00016120 TdxHq_Disconnect
#           3    2 000171A0 TdxHq_GetCompanyInfoCategory
#           4    3 00017320 TdxHq_GetCompanyInfoContent
#           5    4 00017630 TdxHq_GetFinanceInfo
#           6    5 00016780 TdxHq_GetHistoryMinuteTimeData
#           7    6 00016C20 TdxHq_GetHistoryTransactionData
#           8    7 00016900 TdxHq_GetIndexBars
#           9    8 00016470 TdxHq_GetMinuteTimeData
#          10    9 000165F0 TdxHq_GetSecurityBars
#          11    A 000161C0 TdxHq_GetSecurityCount
#          12    B 000162E0 TdxHq_GetSecurityList
#          13    C 00016DB0 TdxHq_GetSecurityQuotes
#          14    D 00016A90 TdxHq_GetTransactionData
#          15    E 000174B0 TdxHq_GetXDXRInfo
#          16    F 00016F30 TdxHq_VB_GetSecurityQuotes
# 
#   Summary
# 
#         E000 .data
#        55000 .rdata
#        1E000 .reloc
#         4000 .rsrc
#       15D000 .text
# 
# API使用流程为: 应用程序先调用TdxHq_Connect连接通达信行情服务器,然后才可以调用其他接口获取行情数据,应用程序应自行处理网络断线问题, 接口是线程安全的
# 如果断线，调用任意api函数后，api会返回已经断线的错误信息，应用程序应根据此错误信息重新连接服务器。

import os.path

from ctypes import WinError, WinDLL, WINFUNCTYPE, create_string_buffer, \
    POINTER, byref, c_bool, c_char, c_char_p, c_int, c_byte, c_short


# load DLL into memory
tdxhqapi_dll = WinDLL(os.path.join(os.path.dirname(__file__), 'TdxHqApi20991230.dll'))


# /// <summary>
# ///  连接通达信行情服务器
# /// </summary>
# /// <param name="IP">服务器IP,可在券商通达信软件登录界面“通讯设置”按钮内查得</param>
# /// <param name="Port">服务器端口</param>
# /// <param name="Result">此API执行返回后，Result内保存了返回的查询数据, 形式为表格数据，行数据之间通过\n字符分割，列数据之间通过\t分隔。一般要分配1024*1024字节的空间。出错时为空字符串。</param>
# /// <param name="ErrInfo">此API执行返回后，如果出错，保存了错误信息说明。一般要分配256字节的空间。没出错时为空字符串。</param>
# /// <returns>成功返货true, 失败返回false</returns>
# typedef bool (__stdcall*  TdxHq_ConnectDelegate)(char* IP, int Port, char* Result, char* ErrInfo);
# bool  TdxHq_Connect(char* IP, int Port, char* Result, char* ErrInfo);//连接券商行情服务器
prototype = WINFUNCTYPE(c_bool, c_char_p, c_int, c_char_p, c_char_p)
paramflags = (1, "IP", None), (1, "Port", 0), (1, "Result", None), (1, "ErrInfo", None)
TdxHq_Connect = prototype(("TdxHq_Connect", tdxhqapi_dll), paramflags)


# /// <summary>
# /// 断开同服务器的连接
# /// </summary>
# typedef void(__stdcall* TdxHq_DisconnectDelegate)();
# void  TdxHq_Disconnect();//断开服务器
prototype = WINFUNCTYPE(None)
TdxHq_Disconnect = prototype(("TdxHq_Disconnect", tdxhqapi_dll),)


# /// <summary>
# /// 获取市场内所有证券的数量
# /// </summary>
# /// <param name="Market">市场代码,   0->深圳     1->上海</param>
# /// <param name="Result">此API执行返回后，Result内保存了返回的证券数量</param>
# /// <param name="ErrInfo">此API执行返回后，如果出错，保存了错误信息说明。一般要分配256字节的空间。没出错时为空字符串。</param>
# /// <returns>成功返货true, 失败返回false</returns>
# typedef bool(__stdcall* TdxHq_GetSecurityCountDelegate)(byte Market, short& Result, char* ErrInfo);
# bool  TdxHq_GetSecurityCount(byte Market, short& Result, char* ErrInfo);//获取指定市场内的证券数目
prototype = WINFUNCTYPE(c_bool, c_byte, POINTER(c_short), c_char_p)
paramflags = (1, "Market", 0), (1, "Result", None), (1, "ErrInfo", None)
TdxHq_GetSecurityCount = prototype(("TdxHq_GetSecurityCount", tdxhqapi_dll), paramflags)


# /// <summary>
# /// 获取市场内某个范围内的1000支股票的股票代码
# /// </summary>
# /// <param name="Market">市场代码,   0->深圳     1->上海</param>
# /// <param name="Start">范围开始位置,第一个股票是0, 第二个是1, 依此类推,位置信息依据TdxHq_GetSecurityCount返回的证券总数确定</param>
# /// <param name="Count">范围的大小，API执行后,保存了实际返回的股票数目,</param>
# /// <param name="Result">此API执行返回后，Result内保存了返回的证券代码信息,形式为表格数据，行数据之间通过\n字符分割，列数据之间通过\t分隔。一般要分配1024*1024字节的空间。出错时为空字符串。</param>
# /// <param name="ErrInfo">此API执行返回后，如果出错，保存了错误信息说明。一般要分配256字节的空间。没出错时为空字符串。</param>
# /// <returns>成功返货true, 失败返回false</returns>
# typedef bool(__stdcall* TdxHq_GetSecurityListDelegate)(byte Market, short Start, short& Count, char* Result, char* ErrInfo);
# bool  TdxHq_GetSecurityList(byte Market, short Start, short& Count, char* Result, char* ErrInfo);//获取市场内指定范围内的所有证券代码
prototype = WINFUNCTYPE(c_bool, c_byte, c_short, POINTER(c_short), c_char_p, c_char_p)
paramflags = (1, "Market", 0), (1, 'Start', 0), (1, 'Count', None), (1, "Result", None), (1, "ErrInfo", None)
TdxHq_GetSecurityList = prototype(("TdxHq_GetSecurityList", tdxhqapi_dll), paramflags)


# /// <summary>
# /// 获取证券指定范围的的K线数据
# /// </summary>
# /// <param name="Category">K线种类, 0->5分钟K线    1->15分钟K线    2->30分钟K线  3->1小时K线    4->日K线  5->周K线  6->月K线  7->1分钟  8->1分钟K线  9->日K线  10->季K线  11->年K线< / param>
# /// <param name="Market">市场代码,   0->深圳     1->上海</param>
# /// <param name="Zqdm">证券代码</param>
# /// <param name="Start">范围的开始位置,最后一条K线位置是0, 前一条是1, 依此类推</param>
# /// <param name="Count">范围的大小，API执行前,表示用户要请求的K线数目, API执行后,保存了实际返回的K线数目, 最大值800</param>
# /// <param name="Result">此API执行返回后，Result内保存了返回的查询数据, 形式为表格数据，行数据之间通过\n字符分割，列数据之间通过\t分隔。一般要分配1024*1024字节的空间。出错时为空字符串。</param>
# /// <param name="ErrInfo">此API执行返回后，如果出错，保存了错误信息说明。一般要分配256字节的空间。没出错时为空字符串。</param>
# /// <returns>成功返货true, 失败返回false</returns>
# typedef bool(__stdcall* TdxHq_GetSecurityBarsDelegate)(byte Category, byte Market, char* Zqdm, short Start, short& Count, char* Result, char* ErrInfo);
# bool  TdxHq_GetSecurityBars(byte Category, byte Market, char* Zqdm, short Start, short& Count, char* Result, char* ErrInfo);//获取股票K线
prototype = WINFUNCTYPE(c_bool, c_byte, c_byte, c_char_p, c_short, POINTER(c_short), c_char_p, c_char_p)
paramflags = (1, 'Category', 0), (1, "Market", 0), (1, 'Zqdm', None), (1, 'Start', 0), (1, 'Count', None), (1, "Result", None), (1, "ErrInfo", None)
TdxHq_GetSecurityBars = prototype(("TdxHq_GetSecurityBars", tdxhqapi_dll), paramflags)


# /// <summary>
# /// 获取指数的指定范围内K线数据
# /// </summary>
# /// <param name="Category">K线种类, 0->5分钟K线    1->15分钟K线    2->30分钟K线  3->1小时K线    4->日K线  5->周K线  6->月K线  7->1分钟  8->1分钟K线  9->日K线  10->季K线  11->年K线< / param>
# /// <param name="Market">市场代码,   0->深圳     1->上海</param>
# /// <param name="Zqdm">证券代码</param>
# /// <param name="Start">范围开始位置,最后一条K线位置是0, 前一条是1, 依此类推</param>
# /// <param name="Count">范围的大小，API执行前,表示用户要请求的K线数目, API执行后,保存了实际返回的K线数目,最大值800</param>
# /// <param name="Result">此API执行返回后，Result内保存了返回的查询数据, 形式为表格数据，行数据之间通过\n字符分割，列数据之间通过\t分隔。一般要分配1024*1024字节的空间。出错时为空字符串。</param>
# /// <param name="ErrInfo">此API执行返回后，如果出错，保存了错误信息说明。一般要分配256字节的空间。没出错时为空字符串。</param>
# /// <returns>成功返货true, 失败返回false</returns>
# typedef bool (__stdcall* TdxHq_GetIndexBarsDelegate)(byte Category, byte Market, char* Zqdm, short Start, short& Count, char* Result, char* ErrInfo);
# bool  TdxHq_GetIndexBars(byte Category, byte Market, char* Zqdm, short Start, short& Count, char* Result, char* ErrInfo);//获取指数K线
prototype = WINFUNCTYPE(c_bool, c_byte, c_byte, c_char_p, c_short, POINTER(c_short), c_char_p, c_char_p)
paramflags = (1, 'Category', 0), (1, "Market", 0), (1, 'Zqdm', None), (1, 'Start', 0), (1, 'Count', None), (1, "Result", None), (1, "ErrInfo", None)
TdxHq_GetIndexBars = prototype(("TdxHq_GetIndexBars", tdxhqapi_dll), paramflags)


# /// <summary>
# /// 获取分时数据
# /// </summary>
# /// <param name="Market">市场代码,   0->深圳     1->上海</param>
# /// <param name="Zqdm">证券代码</param>
# /// <param name="Result">此API执行返回后，Result内保存了返回的查询数据, 形式为表格数据，行数据之间通过\n字符分割，列数据之间通过\t分隔。一般要分配1024*1024字节的空间。出错时为空字符串。</param>
# /// <param name="ErrInfo">此API执行返回后，如果出错，保存了错误信息说明。一般要分配256字节的空间。没出错时为空字符串。</param>
# /// <returns>成功返货true, 失败返回false</returns>
# typedef bool (__stdcall* TdxHq_GetMinuteTimeDataDelegate)(byte Market, char* Zqdm, char* Result, char* ErrInfo);
# bool  TdxHq_GetMinuteTimeData(byte Market, char* Zqdm, char* Result, char* ErrInfo);//获取分时图数据
prototype = WINFUNCTYPE(c_bool, c_byte, c_char_p, c_char_p, c_char_p)
paramflags = (1, "Market", 0), (1, 'Zqdm', None), (1, "Result", None), (1, "ErrInfo", None)
TdxHq_GetMinuteTimeData = prototype(("TdxHq_GetMinuteTimeData", tdxhqapi_dll), paramflags)


# /// <summary>
# /// 获取历史分时数据
# /// </summary>
# /// <param name="Market">市场代码,   0->深圳     1->上海</param>
# /// <param name="Zqdm">证券代码</param>
# /// <param name="Date">日期, 比如2014年1月1日为整数20140101</param>
# /// <param name="Result">此API执行返回后，Result内保存了返回的查询数据, 形式为表格数据，行数据之间通过\n字符分割，列数据之间通过\t分隔。一般要分配1024*1024字节的空间。出错时为空字符串。</param>
# /// <param name="ErrInfo">此API执行返回后，如果出错，保存了错误信息说明。一般要分配256字节的空间。没出错时为空字符串。</param>
# /// <returns>成功返货true, 失败返回false</returns>
# typedef bool(__stdcall* TdxHq_GetHistoryMinuteTimeDataDelegate)(byte Market, char* Zqdm, int Date, char* Result, char* ErrInfo);
# bool  TdxHq_GetHistoryMinuteTimeData(byte Market, char* Zqdm, int date, char* Result, char* ErrInfo);//获取历史分时图数据
prototype = WINFUNCTYPE(c_bool, c_byte, c_char_p, c_int, c_char_p, c_char_p)
paramflags = (1, "Market", 0), (1, 'Zqdm', None), (1, 'date', 0), (1, "Result", None), (1, "ErrInfo", None)
TdxHq_GetHistoryMinuteTimeData = prototype(("TdxHq_GetHistoryMinuteTimeData", tdxhqapi_dll), paramflags)


# /// <summary>
# /// 获取分时成交某个范围内的数据
# /// </summary>
# /// <param name="Market">市场代码,   0->深圳     1->上海</param>
# /// <param name="Zqdm">证券代码</param>
# /// <param name="Start">范围开始位置,最后一条K线位置是0, 前一条是1, 依此类推</param>
# /// <param name="Count">范围大小，API执行前,表示用户要请求的K线数目, API执行后,保存了实际返回的K线数目</param>
# /// <param name="Result">此API执行返回后，Result内保存了返回的查询数据, 形式为表格数据，行数据之间通过\n字符分割，列数据之间通过\t分隔。一般要分配1024*1024字节的空间。出错时为空字符串。</param>
# /// <param name="ErrInfo">此API执行返回后，如果出错，保存了错误信息说明。一般要分配256字节的空间。没出错时为空字符串。</param>
# /// <returns>成功返货true, 失败返回false</returns>
# typedef bool(__stdcall* TdxHq_GetTransactionDataDelegate) (byte Market, char* Zqdm, short Start, short& Count, char* Result, char* ErrInfo);
# bool  TdxHq_GetTransactionData(byte Market, char* Zqdm, short Start, short& Count, char* Result, char* ErrInfo);//获取分时成交
prototype = WINFUNCTYPE(c_bool, c_byte, c_char_p, c_short, POINTER(c_short), c_char_p, c_char_p)
paramflags = (1, "Market", 0), (1, 'Zqdm', None), (1, 'Start', 0), (1, 'Count', None), (1, "Result", None), (1, "ErrInfo", None)
TdxHq_GetTransactionData = prototype(("TdxHq_GetTransactionData", tdxhqapi_dll), paramflags)


# /// <summary>
# /// 获取历史分时成交某个范围内的数据
# /// </summary>
# /// <param name="Market">市场代码,   0->深圳     1->上海</param>
# /// <param name="Zqdm">证券代码</param>
# /// <param name="Start">范围开始位置,最后一条K线位置是0, 前一条是1, 依此类推</param>
# /// <param name="Count">范围大小，API执行前,表示用户要请求的K线数目, API执行后,保存了实际返回的K线数目</param>
# /// <param name="Date">日期, 比如2014年1月1日为整数20140101</param>
# /// <param name="Result">此API执行返回后，Result内保存了返回的查询数据, 形式为表格数据，行数据之间通过\n字符分割，列数据之间通过\t分隔。一般要分配1024*1024字节的空间。出错时为空字符串。</param>
# /// <param name="ErrInfo">此API执行返回后，如果出错，保存了错误信息说明。一般要分配256字节的空间。没出错时为空字符串。</param>
# /// <returns>成功返货true, 失败返回false</returns>
# typedef bool(__stdcall* TdxHq_GetHistoryTransactionDataDelegate) (byte Market, char* Zqdm, short Start, short& Count, int Date, char* Result, char* ErrInfo);
# bool  TdxHq_GetHistoryTransactionData(byte Market, char* Zqdm, short Start, short& Count, int date, char* Result, char* ErrInfo);//获取历史分时成交
prototype = WINFUNCTYPE(c_bool, c_byte, c_char_p, c_short, POINTER(c_short), c_int, c_char_p, c_char_p)
paramflags = (1, "Market", 0), (1, 'Zqdm', None), (1, 'Start', 0), (1, 'Count', None), (1, 'date', 0), (1, "Result", None), (1, "ErrInfo", None)
TdxHq_GetHistoryTransactionData = prototype(("TdxHq_GetHistoryTransactionData", tdxhqapi_dll), paramflags)


# /// <summary>
# /// 批量获取多个证券的五档报价数据
# /// </summary>
# /// <param name="Market">市场代码,   0->深圳     1->上海, 第i个元素表示第i个证券的市场代码</param>
# /// <param name="Zqdm">证券代码, Count个证券代码组成的数组</param>
# /// <param name="Count">API执行前,表示用户要请求的证券数目,最大50(不同券商可能不一样,具体数目请自行咨询券商或测试), API执行后,保存了实际返回的数目</param>
# /// <param name="Result">此API执行返回后，Result内保存了返回的查询数据, 形式为表格数据，行数据之间通过\n字符分割，列数据之间通过\t分隔。一般要分配1024*1024字节的空间。出错时为空字符串。</param>
# /// <param name="ErrInfo">此API执行返回后，如果出错，保存了错误信息说明。一般要分配256字节的空间。没出错时为空字符串。</param>
# /// <returns>成功返货true, 失败返回false</returns>
# typedef bool(__stdcall* TdxHq_GetSecurityQuotesDelegate) (byte Market[], char* Zqdm[], short& Count, char* Result, char* ErrInfo);
# bool  TdxHq_GetSecurityQuotes(byte Market[], char* Zqdm[], short& Count, char* Result, char* ErrInfo);//获取盘口五档报价
prototype = WINFUNCTYPE(c_bool, POINTER(c_byte), POINTER(c_char_p), POINTER(c_short), c_char_p, c_char_p)
paramflags = (1, "Market", None), (1, 'Zqdm', None), (1, 'Count', None), (1, "Result", None), (1, "ErrInfo", None)
TdxHq_GetSecurityQuotes = prototype(("TdxHq_GetSecurityQuotes", tdxhqapi_dll), paramflags)


# /// <summary>
# /// 获取F10资料的分类
# /// </summary>
# /// <param name="Market">市场代码,   0->深圳     1->上海</param>
# /// <param name="Zqdm">证券代码</param>
# /// <param name="Result">此API执行返回后，Result内保存了返回的查询数据, 形式为表格数据，行数据之间通过\n字符分割，列数据之间通过\t分隔。一般要分配1024*1024字节的空间。出错时为空字符串。</param>
# /// <param name="ErrInfo">此API执行返回后，如果出错，保存了错误信息说明。一般要分配256字节的空间。没出错时为空字符串。</param>
# /// <returns>成功返货true, 失败返回false</returns>
# typedef bool(__stdcall* TdxHq_GetCompanyInfoCategoryDelegate) (byte Market, char* Zqdm, char* Result, char* ErrInfo);
# bool  TdxHq_GetCompanyInfoCategory(byte Market, char* Zqdm, char* Result, char* ErrInfo);//获取F10信息类别
prototype = WINFUNCTYPE(c_bool, c_byte, c_char_p, c_char_p, c_char_p)
paramflags = (1, "Market", 0), (1, 'Zqdm', None), (1, "Result", None), (1, "ErrInfo", None)
TdxHq_GetCompanyInfoCategory = prototype(("TdxHq_GetCompanyInfoCategory", tdxhqapi_dll), paramflags)


# /// <summary>
# /// 获取F10资料的某一分类的内容
# /// </summary>
# /// <param name="Market">市场代码,   0->深圳     1->上海</param>
# /// <param name="Zqdm">证券代码</param>
# /// <param name="FileName">类目的文件名, 由TdxHq_GetCompanyInfoCategory返回信息中获取</param>
# /// <param name="Start">类目的开始位置, 由TdxHq_GetCompanyInfoCategory返回信息中获取</param>
# /// <param name="Length">类目的长度, 由TdxHq_GetCompanyInfoCategory返回信息中获取</param>
# /// <param name="Result">此API执行返回后，Result内保存了返回的查询数据,出错时为空字符串。</param>
# /// <param name="ErrInfo">此API执行返回后，如果出错，保存了错误信息说明。一般要分配256字节的空间。没出错时为空字符串。</param>
# /// <returns>成功返货true, 失败返回false</returns>
# typedef bool(__stdcall* TdxHq_GetCompanyInfoContentDelegate) (byte Market, char* Zqdm, char* FileName, int Start, int Length, char* Result, char* ErrInfo);
# bool  TdxHq_GetCompanyInfoContent(byte Market, char* Zqdm, char* FileName, int Start, int Length, char* Result, char* ErrInfo);//获取F10信息内容
prototype = WINFUNCTYPE(c_bool, c_byte, c_char_p, c_char_p, c_int, c_int, c_char_p, c_char_p)
paramflags = (1, "Market", 0), (1, 'Zqdm', None), (1, 'FileName', None), (1, 'Start', 0), (1, 'Length', 0), (1, "Result", None), (1, "ErrInfo", None)
TdxHq_GetCompanyInfoContent = prototype(("TdxHq_GetCompanyInfoContent", tdxhqapi_dll), paramflags)


# /// <summary>
# /// 获取除权除息信息
# /// </summary>
# /// <param name="Market">市场代码,   0->深圳     1->上海</param>
# /// <param name="Zqdm">证券代码</param>
# /// <param name="Result">此API执行返回后，Result内保存了返回的查询数据,出错时为空字符串。</param>
# /// <param name="ErrInfo">此API执行返回后，如果出错，保存了错误信息说明。一般要分配256字节的空间。没出错时为空字符串。</param>
# /// <returns>成功返货true, 失败返回false</returns>
# typedef bool(__stdcall* TdxHq_GetXDXRInfoDelegate) (byte Market, char* Zqdm, char* Result, char* ErrInfo);
# bool  TdxHq_GetXDXRInfo(byte Market, char* Zqdm, char* Result, char* ErrInfo);//获取权息数据
prototype = WINFUNCTYPE(c_bool, c_byte, c_char_p, c_char_p, c_char_p)
paramflags = (1, "Market", 0), (1, 'Zqdm', None), (1, "Result", None), (1, "ErrInfo", None)
TdxHq_GetXDXRInfo = prototype(("TdxHq_GetXDXRInfo", tdxhqapi_dll), paramflags)


# /// <summary>
# /// 获取财务信息
# /// </summary>
# /// <param name="Market">市场代码,   0->深圳     1->上海</param>
# /// <param name="Zqdm">证券代码</param>
# /// <param name="Result">此API执行返回后，Result内保存了返回的查询数据,出错时为空字符串。</param>
# /// <param name="ErrInfo">此API执行返回后，如果出错，保存了错误信息说明。一般要分配256字节的空间。没出错时为空字符串。</param>
# /// <returns>成功返货true, 失败返回false</returns>
# typedef bool(__stdcall* TdxHq_GetFinanceInfoDelegate) (byte Market, char* Zqdm, char* Result, char* ErrInfo);
# bool  TdxHq_GetFinanceInfo(byte Market, char* Zqdm, char* Result, char* ErrInfo);//获取财务数据
prototype = WINFUNCTYPE(c_bool, c_byte, c_char_p, c_char_p, c_char_p)
paramflags = (1, "Market", 0), (1, 'Zqdm', None), (1, "Result", None), (1, "ErrInfo", None)
TdxHq_GetFinanceInfo = prototype(("TdxHq_GetFinanceInfo", tdxhqapi_dll), paramflags)
