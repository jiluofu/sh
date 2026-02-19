import akshare as ak
import pandas as pd

def get_today_a_share_news():
    """获取当天A股相关新闻和公告"""
    # print("===== 实时财经新闻 =====")
    # economic_news = ak.news_economic()
    # print(economic_news.head())
    
    print("\n===== 财联社今日快讯 =====")
    cls_news = ak.news_cctv()
    print(cls_news.head())
    
    # print("\n===== 上证指数相关新闻 =====")
    # sh_news = ak.news_stock_sina(stock="sh000001")
    # print(sh_news.head())
    
    # print("\n===== 贵州茅台公司新闻 =====")
    # stock_news = ak.stock_news_em(stock="600519")
    # print(stock_news.head())
    
    # print("\n===== 平安银行公司公告 =====")
    # announcement = ak.stock_news_gg(stock="000001")
    # print(announcement.head())

if __name__ == "__main__":
    get_today_a_share_news()