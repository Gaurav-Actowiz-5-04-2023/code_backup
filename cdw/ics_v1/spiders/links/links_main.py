import time
import scrapy,pymysql
import requests
from parsel import Selector
from ics_v1.items import IcsV1SiteMapLinksItemfinal
from scrapy.cmdline import execute
import ics_v1.db_config as db

def request_url(pdp_url):

    payload = {}
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': 'optimizelyEndUserId=oeu1712575697506r0.05273052206960971; utag_main_random_number=82; utag_main_vapi_domain=cdw.com; s_ecid=MCMID%7C82866238473463775800964311901517671853; _lc2_fpi=464f01cb1133--01htyqetnd6j5tx8js4p359yms; _lc2_fpi_meta={%22w%22:1712575703725}; bluecoreNV=false; __pdst=547a7d8ce71a41188859329071657eaa; _gcl_au=1.1.1139124387.1712575777; dtm_token_sc=AAAFqpmGZPnoSwBJojxIAAAAAAE; sa-user-id=s%253A0-cf2bd0e9-397d-5b0f-6fe8-41dd6746fe18.mgiMlCBzSyG%252FxU%252BA9PmUtb7XLPXlvOXlJAcNLGIl%252F6A; sa-user-id-v2=s%253AzyvQ6Tl9Ww9v6EHdZ0b-GNi9Ino.xWLDBdQTrV%252FPv5SktADY6upV0iMZHr1TacTJ80SQUL0; sa-user-id-v3=s%253AAQAKIB1wL9arrE34uZ-bbJ7x-sL9GFVWaDWm6ZpMeYpbNzZ7EHwYBCChqs-wBjABOgT7-sM6QgSokc3j.Okx5bzHT7sa9yoDgNUGtDIp0QkkqVtkEIIJAI%252FJYV00; _uetvid=48a13200f59b11ee96b33d46f5f65e04; utag_main_v_id=018ebd78925b0099dc1f51afd1a00506f009406700bd0; _fbp=fb.1.1712575779584.825896845; __qca=P0-426454749-1712575777635; _hjSessionUser_68143=eyJpZCI6Ijk5MTdlOGQ2LTU5YTQtNTk2MS1hNjRkLWJlYmM2ZDE3N2E1ZiIsImNyZWF0ZWQiOjE3MTI1NzU3ODM3NDMsImV4aXN0aW5nIjp0cnVlfQ==; dtm_token=AAAFqpmGZPnoSwBJojxIAAAAAAE; __qca=P0-194401613-1712575777635; OptanonAlertBoxClosed=2024-04-12T07:42:07.359Z; optimizelyEndUserId=oeu1712575697506r0.05273052206960971; 4112525968F44D5C99DF0BDE0C235561=_021478|2024-04-16,1173274|2024-04-15,470364|2024-04-14,7603273|2024-04-14,1035980|2024-04-14,1018234|2024-04-14,1011439|2024-04-14,1028090|2024-04-14,1042615|2024-04-14,1033626|2024-04-14,1018535|2024-04-14,1018516|2024-04-14; utag_main__sn=11; AMCV_6B61EE6A54FA17010A4C98A7%40AdobeOrg=-1124106680%7CMCIDTS%7C19829%7CMCMID%7C82866238473463775800964311901517671853%7CMCAAMLH-1713860473%7C7%7CMCAAMB-1713860473%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1713262873s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C5.2.0; utag_main_dc_visit=11; mp_cdw_mixpanel=%7B%22distinct_id%22%3A%20%2218ebd775f248e8-0cd98796b35383-26001a51-1fa400-18ebd775f25d85%22%2C%22bc_persist_updated%22%3A%201712929195017%2C%22bc_id_cache%22%3A%20%22%7B%5C%22liveintent_hash%5C%22%3A-1382151851%7D%22%7D; _rdt_uuid=1712929198455.f5362552-b4d9-4e59-8abf-a1b66d140751; cto_bundle=HfqX8l9raVA5MyUyRnNEa0o5VXpRNXRrJTJGZGdtUmJ6ZWtBS1JMRFE4aXhGd0tPY05wdDhPY0RNYXRLQk12WWhyaCUyRm5wcW9jZmFOTW5MNFU3SjBEdXhvQndoJTJGdjhCRGd5ZFh1JTJGUVBhZmhXV2hMVXF4YlVkbSUyRlM5UUlSM2xUamQ3UFB1S0pzMk5xT0YzcldGRmdoNzRocHAlMkJBUE0xQSUzRCUzRA; cto_bundle=HfqX8l9raVA5MyUyRnNEa0o5VXpRNXRrJTJGZGdtUmJ6ZWtBS1JMRFE4aXhGd0tPY05wdDhPY0RNYXRLQk12WWhyaCUyRm5wcW9jZmFOTW5MNFU3SjBEdXhvQndoJTJGdjhCRGd5ZFh1JTJGUVBhZmhXV2hMVXF4YlVkbSUyRlM5UUlSM2xUamQ3UFB1S0pzMk5xT0YzcldGRmdoNzRocHAlMkJBUE0xQSUzRCUzRA; needlepin=N190d171257570203342a95001a282819c894d5819d2f504819d2f75b00318f000819d2f51023200000001413819d2f5100000000000000cinvTargeted21413819ce0c7b412d8; AKA_A2=A; bm_mi=B188D57F562B2E02BEF0BA9CFFE9736F~YAAQhGvcF0U21k+PAQAAAvx2dReP3VsIezeewGwcg0GgGW+sPZGkxx3wQ0CL3/EISd0+w7J1cq1Cnv6gJEbXRLJCwEPXiwt/bkaKwAJxxd57oDU89waDRr5nWO656wlktdxNPIdWUT8y5T5ONryC5Gjo7OjA45nSENrNijQ0q1/9ml000p0qYtSNMT9IXDIekMthldmNxqlZNEMnARTlEVCxSxBClZK9xXJ2pFdD3Um/wZzre5kfafZi950leGluoaHUd/vpGNePz61UhNzo+Q066KxbPIS3mpK9fj1UY0mVP8zstT0ywJDzd3cpkknrCfpbY3+579DXjGrqxK0d60yBZU5UBLIPSE9RgsFEPNjWzrkhkd4=~1; _abck=587159A2838E87CD1CDA7A35764E10AC~0~YAAQhGvcF8021k+PAQAAcP92dQvAQyvW07034O/AQW7V3EIR9moyMV8iK474SVdlph9EiIfxhJMZZxgmnKj23lSFvd3N8pvxPDgt1WW4HI1x9HpFkByTC9aPiSwt/W0lAzLVym8TNkgEPmGbzrYxvb8smsL1Wia2ZGxjAxXSIdtOZhyz1nbJJRI+b8pJgafeuusdvk1Qca4ohX+HmIUN9vyf7ZbncVqaYFqgi7fibiGe7rHpCxsjUnCF5aMc2gfvv7c+Zz3HkhSUgFoprfRXjC3JRnf4DEoCyMYqq6cDYG7I1JHNHrTr8oEp4EJl62S0S0c/nbPZL+JlWm2umsRgUVW83siL8mes9onlRIOLTfMjK/iMcP1gR7zvBs6Al76YRlcRZYHs7fxObvqmM1XqcPe1yTtI~-1~-1~-1; ak_bmsc=A4086EF962A8A5561842F33F59187A23~000000000000000000000000000000~YAAQhGvcF4o31k+PAQAADQR3dRed96wa+9y/WAFa2HDMu0NR5XN0FL7iUdwV+9odwA5y60ugVOZlvtqySjnnb4YxPjBB30HLqrxJ03RG2Woj1Si7//X37E4GEo1Dnm5kMDg0K/IrINMIBL+aPEULUV5lOT7ph9dN9UFgFVH9zWx0DuHFJtKdJ1ychc26Q1Eqk3Ys/FbIByl8j+qCWRK/FdhHFpSh6sRJuadhq3ekyEarbVKt81EeNCxHokH5OV/tTUQNSyRyp+8ofq+mwjoTVefeDctRlFwNgO0cTfo7/M3V48a4vBfV+bFBkJ7qVNRVfYEFNNYYGVWG3q/0JeN//fhGPOucwUh6MMKuYfVdT+LS/RosY1Q+1mm6ikSTxjHLVpm3UyjKHn4nj63VCfdmRXjfcKW0SAtTpqhcCz6mK14pbPJ7JyAykm/2OqBiOCnZDIeenijPIwR08hum8iowdKeRw8PgI7PPd9xr/hFxh3yVGHDqS2NBzIDqkXLkuLma+lais6Hi7kWi1eURSvMCkWttY1x3fYg=; 70549A6B29AD46CF90DA19BC17972419=aayuPsfBHVnsWMoIELNPyUCIKtTlWuX-OWwKQVob0LZ2eJMszNREWRobFf2hO3ksqisYolnSTVZTjY3EZZpogG2bC2c1; A8A8F83D13EA4F8B917AA5F211762060=AD5591C9E38B41A5BCDBC92999FAA1A3; BA9AA5C91598458BA251A10B273627B6=7AB39CC8BF114D82A8169496803081EB; 265B10B0AD854F37A02410D8F39E9723=60582D6A-9CFC-4896-B916-9B3F19E12906; CartKey=70afe761f6344d78a5b291654bb3d0b7; bm_sz=041F12D7C7EF6C033A8F69FB5E8D4FD3~YAAQU542F2S5MXCPAQAANjOVdRej6LVpTxD/+IFcpeliGJ75YHdapvK/InTvZ7V5dqnPs1UKmLqUUijHDUJ1lzC9L2NaU1cOevG4iGp4mIWW2BQ67BHSkbY7rVHo85ONU5d+y/DsoMtIwGxMg8hMpTEZCTDMWB4SAPHJU5peLmgUkJUhoWv87gH3GpCe1u990aGrepTJYoeL/SDrGo88iJE2ZlkRKXj5NEn3MauuxNI59+n4N06SI0x/GqvDUO9ZTd773kS+S7SLyUIu2AwBSdHuSj72yYpfFxKDhYkcBx+jSpy34YgO1PaM4blFxf1VXOSJ0KKe794rNor69vMEoLynGiN3IS+Q49tN/mQKCcmofeDKUyhmBZawLXSBQ7ueA88rdDMnO7rB4+UGl3mCJW284Z6uuqyhtJQyKTHcnpyvFeOpoDYrSqfyrbo5qGuWwlR1iPoeMbaodqXm5qwX/IVJ5Sbzb0SewoFreuX657XalhLEHe7TXNhC+JU=~3753014~3487541; OptanonConsent=isGpcEnabled=0&datestamp=Tue+May+14+2024+11%3A01%3A04+GMT%2B0530+(India+Standard+Time)&version=202310.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=decdab39-cbd7-4460-aa8a-aaee7e17e4e0&interactionCount=2&landingPath=NotLandingPage&groups=C0003%3A1%2CC0004%3A1%2CC0001%3A1%2CC0002%3A1&AwaitingReconsent=false&geolocation=US%3BNY; bm_sv=EF6743135ADA709768E3E145E285948C~YAAQU542FzW6MXCPAQAAkDaVdReRkIVVflbARb530knQweant7i5cjeRFbJdduEDSYty3+xL6J6DTko+VTjwQGbecC1TQEYTi8YkpzinrALMHuTWUG7+A/rxCsNdWntsNFoDO38YDbwOP4NW7G7GW3JRd8NvvwR7c2C/KGNJleaOjkH7kNrF3/WHMik38rqdtL7MP+TGKInPuYDMNvUiHqSHvNY7IyRbel/AKLjm5jTIuBURbJzsiphMp3SGAg==~1; _abck=587159A2838E87CD1CDA7A35764E10AC~-1~YAAQU542F9JtMnCPAQAAQTGZdQs3V2GOj6tgVJlnpFmpQnrFRZ/aSK1Wxr3CRhJHMSHcKXIFQSSbADWY9Z6cEi9vXre0FIzPoLGggBWOG/W62sD7bL3nKyGXX1IKSczMbGn1z+h5d/YQwHx4X27uZvdxT+B5pslu4iTNy0HNbGNvvL1JG86rNDi/OpZfHVy2WtJ5EQ1lKsOsnbBA29xrz2TC+9rjPbUTBewHCRSWPrPSZw+EE8/Peg/jrb5y0UMyrKrxtY0GyNeO5iXXQc6Boni8DctQc6r8kR5LAZXVtwA+tY136YWsmdfnerpoFqmB9KaOnvQ1gU4QXVUr80M7FnRAsFbokLM/u8u7Pt9ZMgy06HeJFhLlp9UPYIN7S75hsh7ZDncsuKGCaIszv6Wxz0SUSqKx~0~-1~-1; bm_sv=EF6743135ADA709768E3E145E285948C~YAAQU542F9NtMnCPAQAAQTGZdRd0xqYoG0ah1mWRoI5kxcsuGeUwhXDs99gH+wgzWJXfdhTS83bSs6J5EU/o+1T16u9oBEGSsqHVjp/xsRj1K7SVIc5IK8t7e+Zu+uuiY/JZVURZxkryWT/u1lzT9uM2aAsUOE+0uhqC3JokXSC4oCs2fFGZIgJ5jWxXfgAmk6ZCIwU+w3L2c58eR8p7a8F5mSYPJAjyKHyD2QDp7ggef3nRq+NmGirt+AXGOA==~1; bm_sz=041F12D7C7EF6C033A8F69FB5E8D4FD3~YAAQU542F9RtMnCPAQAAQTGZdRe/27yG8m/fMWRZPSMJS2OUDV1JYLigabvhQCQZPfaBHCpsaNdDLqcyE0gYEf8ByFTuCirOqDfxwMO/v+NhCJ78hcnttYa6yWAS0EO2DhLRdWcMZl4ngO82OUDNyLKFWhDUbu++up0yZdqsFeZl6Bvx4Y0uc9PTvHhdLpa4QjrCVIVVDaVsCUMr6aBDuQ6f7BCz9cnSufVpVjEGMKR5BV03mpyQh74N5zkC7mUVEmXMnxG1BQeUAXf7Q2UZLoG+0KoJWu7vNWP6D9vlYe7dG5qcnPp0Fzhmo2hqAZy5nYb2vhEDpKyadjzawSDYVWs0mLmN0uW7HrM8D1poRXSIGVDevE7OsvyhH7Fsk0DGCg1lx4hNp1D+Of12bDiX4Ar6pOSMGiG72nHrik7G85GkSfqiiDCpvt/mO3L3A73aLiGL7AYNSfJyATPkE0kcYQXphz6eqMgfx0i1isFpJFAh68nBmr8tVTKowR8WMmAaza6b~3753014~3487541',
        'priority': 'u=0, i',
        # 'referer': 'https://www.cdw.com/search/computer-accessories/computer-components/?w=AA&b=LAW',
        'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }

    response = requests.request("GET", pdp_url, headers=headers, data=payload)

    response = Selector(response.text)

    urls = response.xpath('//h2//a[@class="search-result-product-url"]//@href').getall()

    return urls



class LinksSpider(scrapy.Spider):
    name = 'links_main'
    start_urls = [f'https://www.cdw.com/']

    VENDOR_ID = "ACT-B3-010"
    VENDOR_NAME = "CDW"

    def __init__(self, name=None, start=1, end=1, **kwargs):
        super().__init__(name, **kwargs)
        # DATABASE CONNECTION
        self.con = pymysql.connect(host=db.db_host, user=db.db_user, password=db.db_password, db=db.db_name)
        self.cursor = self.con.cursor()
        self.start = start
        self.end = end
        self.counter = 1

    def start_requests(self):
        select_query = [
                    f"select id, product_urls from {db.sitemap_table_3} where",
                    f"status='pending' and id between {self.start} and {self.end}"
                ]
        self.cursor.execute(" ".join(select_query))

        count=0
        for data in self.cursor.fetchall():
            cookies = {
                'optimizelyEndUserId': 'oeu1712575697506r0.05273052206960971',
                'utag_main_random_number': '82',
                'utag_main_vapi_domain': 'cdw.com',
                's_ecid': 'MCMID%7C82866238473463775800964311901517671853',
                '_lc2_fpi': '464f01cb1133--01htyqetnd6j5tx8js4p359yms',
                '_lc2_fpi_meta': '{%22w%22:1712575703725}',
                'bluecoreNV': 'false',
                '__pdst': '547a7d8ce71a41188859329071657eaa',
                '_gcl_au': '1.1.1139124387.1712575777',
                'dtm_token_sc': 'AAAFqpmGZPnoSwBJojxIAAAAAAE',
                'sa-user-id': 's%253A0-cf2bd0e9-397d-5b0f-6fe8-41dd6746fe18.mgiMlCBzSyG%252FxU%252BA9PmUtb7XLPXlvOXlJAcNLGIl%252F6A',
                'sa-user-id-v2': 's%253AzyvQ6Tl9Ww9v6EHdZ0b-GNi9Ino.xWLDBdQTrV%252FPv5SktADY6upV0iMZHr1TacTJ80SQUL0',
                'sa-user-id-v3': 's%253AAQAKIB1wL9arrE34uZ-bbJ7x-sL9GFVWaDWm6ZpMeYpbNzZ7EHwYBCChqs-wBjABOgT7-sM6QgSokc3j.Okx5bzHT7sa9yoDgNUGtDIp0QkkqVtkEIIJAI%252FJYV00',
                '_uetvid': '48a13200f59b11ee96b33d46f5f65e04',
                'utag_main_v_id': '018ebd78925b0099dc1f51afd1a00506f009406700bd0',
                '_fbp': 'fb.1.1712575779584.825896845',
                '__qca': 'P0-426454749-1712575777635',
                '_hjSessionUser_68143': 'eyJpZCI6Ijk5MTdlOGQ2LTU5YTQtNTk2MS1hNjRkLWJlYmM2ZDE3N2E1ZiIsImNyZWF0ZWQiOjE3MTI1NzU3ODM3NDMsImV4aXN0aW5nIjp0cnVlfQ==',
                'dtm_token': 'AAAFqpmGZPnoSwBJojxIAAAAAAE',
                '__qca': 'P0-194401613-1712575777635',
                'OptanonAlertBoxClosed': '2024-04-12T07:42:07.359Z',
                'optimizelyEndUserId': 'oeu1712575697506r0.05273052206960971',
                'AMCV_6B61EE6A54FA17010A4C98A7%40AdobeOrg': '-1124106680%7CMCIDTS%7C19860%7CMCMID%7C81709133174155428357968145689486395526%7CMCAAMLH-1716445766%7C12%7CMCAAMB-1716445766%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1715848166s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C5.2.0',
                'rr_rcs': 'eF5jYSlN9jBJSbNMSzYw001KMTfSNTFMMdG1NEoy1jUyMDNONTAwtzA0SuPKLSvJTOEzMjDVNdQ1BACJjw3G',
                'utag_main__sn': '14',
                'utag_main_dc_visit': '14',
                'cto_bundle': 'QDlotF9raVA5MyUyRnNEa0o5VXpRNXRrJTJGZGdtZXNVNWtoTE1rZVhiS1dKU3BpRHF1eHNBQVJ6SklLNW5XNndPUkhYOGdxN1VRJTJCU2JLR1NhWEtabWYlMkJTWnNwZE5rWWZEd0Y2emw4YnV6YTJOclJMMTlsdzl6SlY4NyUyRldOc3Fxa2cxdGpKZDZjT3VaVnYzYmNCN21MQlZpQTUzeTlnJTNEJTNE',
                'cto_bundle': 'QDlotF9raVA5MyUyRnNEa0o5VXpRNXRrJTJGZGdtZXNVNWtoTE1rZVhiS1dKU3BpRHF1eHNBQVJ6SklLNW5XNndPUkhYOGdxN1VRJTJCU2JLR1NhWEtabWYlMkJTWnNwZE5rWWZEd0Y2emw4YnV6YTJOclJMMTlsdzl6SlY4NyUyRldOc3Fxa2cxdGpKZDZjT3VaVnYzYmNCN21MQlZpQTUzeTlnJTNEJTNE',
                'mp_cdw_mixpanel': '%7B%22distinct_id%22%3A%20%2218ebd775f248e8-0cd98796b35383-26001a51-1fa400-18ebd775f25d85%22%2C%22bc_persist_updated%22%3A%201712929195017%2C%22bc_id_cache%22%3A%20%22%7B%5C%22liveintent_hash%5C%22%3A-1382151851%7D%22%7D',
                '_rdt_uuid': '1715842044674.4ca3a29b-17d9-47d4-8860-b838021f67c8',
                'needlepin': 'N190d171257570203344639001c2d2819c894d5819fa67c7819fa7b22003242000819d2f51023200000001411819fa6838000000000dmktnumb2024Q21411819fa7a3e41277000cinvTargeted21413819ce0c7b412d8',
                '4112525968F44D5C99DF0BDE0C235561': '_991210|2024-05-17,6068169|2024-05-16,6716541|2024-05-16,999603|2024-05-16,1005635|2024-05-16,6605095|2024-05-16,7133096|2024-05-16,5441720|2024-05-16,6695911|2024-05-16,4058087|2024-05-16,7308045|2024-05-16,2007473|2024-05-16',
                'AKA_A2': 'A',
                '_abck': '587159A2838E87CD1CDA7A35764E10AC~0~YAAQTvzaF83WEe2PAQAAheFyBgwRws9A0m3BvsZUwraBKbXFOgfwTM9LLFzP962yO2qbRXy8n8ZstzzU7Dx6InbvaaN+ACAXQuI2ajt8Wx/Cpbm1TShC00nf8lpmAj7s88QGgKHOEnUjwaG83ruedwuFB3YXG7A5ScVZTcka847G7ol5QDkBO91ygQPmiYIDkfJClhP0s26/kmoH5fyE8Hz+zvzwxNFglHQcmX4xRpwpD/S6XQJu5LQl8KAUYvbNscdrgXNPzj/XGo4D0lpLQROydGBOad9mkU9FeTsTZRnHaAcgPn7WhoPnh4m3oPRJPVBSATiLV2/YomF2Fxa8QRUdcnV+dLtdADy+EWzKp6xZjo63/WqN707bXLgcJMesmaAdy/vvqzLV/kt9l7B50Qz53ZOI~-1~-1~-1',
                '70549A6B29AD46CF90DA19BC17972419': 'E_w8faArDhGs4HNoQBgTBM0E8WJly8kMG5te1tgY2JpRsnW9ulpS8_5P88hqd7NbKcKSgPrfqQE5k5deM3goOnYLwpM1',
                'ak_bmsc': 'D643ED7FC297E23D904297E674A51EB2~000000000000000000000000000000~YAAQENYsF5fw7wWQAQAAfFF8BhjvlbTMFwQ9KwakUGy1uak94fw0kGoHHJI2/wu+c3t7xX2EV92+uSdDlH8x/g8ZwIPXu925HX0vQlz3BOAsRk3m69yn+W7v7QBw890MJHxo4H47M3waO9NMMGbRiOEvspI5vwIdxU+uHeVRGwKvhaYJAAr9XNiBVRtltDyXANZzPqgPUslNckVa4yzl3U36F8XOJfejehY+l6wt5KyCYlJcJS530NWMQrhHuv1QE4+C9Qy+Sg9r3KGe/ZHgq4Oltzys1GdyjPIseuwAoXLph4Q++Krwuwow/XGLCPWLCDBlk7n/IaiVm6yL9yvN7rFjkRvV3Bl+1d8NiJUv0XqI0dfmb5JBvROXvZUdjvkLoCP6owIeHhJ9kqjDH6eq4YocsqlQoW/gSmiIiqWCdUoSNTD5lZNjsytP9LipVs7m5KyExDnBWherujYn/9lTkUCJoJ8SHy7QJUGxV3SpkLS/HZ4Fjhd0g5nFITBNPDyrVWmYNDKXLgEiW+5THcCA/g==',
                '265B10B0AD854F37A02410D8F39E9723': 'F0AF03C5-4DF3-4877-AB17-DF7DFFD4B54F',
                'CartKey': '87d1be2dbc424a4090f20fa60f420f17',
                'A8A8F83D13EA4F8B917AA5F211762060': '3590BC5EA12746A5907EE6FCB9215603',
                'BA9AA5C91598458BA251A10B273627B6': '6D6C4838AD9041988203F1DBF8C984E5',
                'bm_sz': '58EF64E6F141D20C757964E22DA2F8B8~YAAQENYsFybz7wWQAQAAz5x8BhjrR0nXDdM4KHY3yzMWP1aBGu9av9Y5O9edwP8XEV7grmr/FRrju+vf/4oVnEFk/5IF/ZnPCBhbsqXu/gh6YuqDjdG0CICbZhlcx9MF/TAlU12skVnrUJGSYqDiiFq7b01ommUjvbzl/lUM56LUz/a4+64Wh3GD9EHsioYpKR4czSKethLS7JJMueLGxYneR4HMePp4qD23Z2RaGqr3OrKAXM3eR+gBE1U+Ye+HH99j/iUGaZjJHSI/5A5f0VXWH+ZkzM2tdPRm0Fpgiv4SRRRv7ulOLdUKvtDG7Yr34XP0cyQSRqEnBhNpCo3NV7O1GboxvJRMX9L4qswJt87ndKVrhbpApLawJhntWzucE8jvVzPinV1N3G3Fh28EnAVh9Q==~4403769~4403248',
                'OptanonConsent': 'isGpcEnabled=0&datestamp=Tue+Jun+11+2024+14%3A19%3A08+GMT%2B0530+(India+Standard+Time)&version=202310.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=decdab39-cbd7-4460-aa8a-aaee7e17e4e0&interactionCount=2&landingPath=NotLandingPage&groups=C0003%3A1%2CC0004%3A1%2CC0001%3A1%2CC0002%3A1&AwaitingReconsent=false&geolocation=US%3BNY',
                'bm_mi': '3DCE7864C8A2213A49E41611309815CD~YAAQENYsF78Q8AWQAQAA6rmABhihhMyjpLe6EjYKt27081dK2UdgyUP5LiqfaPSGD9cLaOXdjNzuokksRwcUSRO9wsZT+t3s2s1Yr4etZ8z7PLeNaspCJOuvkw+OBUb0LnzjxYJPzU4ssgNlQhmoLFX+tFpbrS01OosgY9s20Qh1H0OxsEORBCe+TQwfukPgFShmm2RyDuxAI8YylkOvhUf0Y9Kk/KlsUq3TLo7JKO+yZSb1btBNV17wTFkbWHONhen2KosSpZRVDHU+aDiNsVVWyr3sd95UgF4uZHPYWlEzYueqIJ4yVi+EXfLw82AkvmzpgUg9o+PNGHnyb3E1/8C1Zl9K9CxhPS2HHb3/Mizm8AjDzNio~1',
                'bm_sv': '6460E45FBBC3F622A4863BCA89B152BD~YAAQENYsF8AQ8AWQAQAA6rmABhhbIpeV0SnT292cdVV1fDJnOHRjLmBdqWsyeiJE+4WKpUDxhB+fcu7QWpdeBO/mFJg0wYjjLnxfNHRTp3LHM2Umb/uLaP1IubT90Fbr8EKHV/kuLex8pALXNGx0dXOLU/5u4jDxfeQFzg3IaPuKOAZYvgkSMv8Ng7S9cwWjYh3foggeuyKAGV6wS0KFgHRaELqhKg8h38bWq9NiAJCNCgZXRvUniBkaBJ2Ngw==~1',
            }

            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'en-US,en;q=0.9',
                # 'cookie': 'optimizelyEndUserId=oeu1712575697506r0.05273052206960971; utag_main_random_number=82; utag_main_vapi_domain=cdw.com; s_ecid=MCMID%7C82866238473463775800964311901517671853; _lc2_fpi=464f01cb1133--01htyqetnd6j5tx8js4p359yms; _lc2_fpi_meta={%22w%22:1712575703725}; bluecoreNV=false; __pdst=547a7d8ce71a41188859329071657eaa; _gcl_au=1.1.1139124387.1712575777; dtm_token_sc=AAAFqpmGZPnoSwBJojxIAAAAAAE; sa-user-id=s%253A0-cf2bd0e9-397d-5b0f-6fe8-41dd6746fe18.mgiMlCBzSyG%252FxU%252BA9PmUtb7XLPXlvOXlJAcNLGIl%252F6A; sa-user-id-v2=s%253AzyvQ6Tl9Ww9v6EHdZ0b-GNi9Ino.xWLDBdQTrV%252FPv5SktADY6upV0iMZHr1TacTJ80SQUL0; sa-user-id-v3=s%253AAQAKIB1wL9arrE34uZ-bbJ7x-sL9GFVWaDWm6ZpMeYpbNzZ7EHwYBCChqs-wBjABOgT7-sM6QgSokc3j.Okx5bzHT7sa9yoDgNUGtDIp0QkkqVtkEIIJAI%252FJYV00; _uetvid=48a13200f59b11ee96b33d46f5f65e04; utag_main_v_id=018ebd78925b0099dc1f51afd1a00506f009406700bd0; _fbp=fb.1.1712575779584.825896845; __qca=P0-426454749-1712575777635; _hjSessionUser_68143=eyJpZCI6Ijk5MTdlOGQ2LTU5YTQtNTk2MS1hNjRkLWJlYmM2ZDE3N2E1ZiIsImNyZWF0ZWQiOjE3MTI1NzU3ODM3NDMsImV4aXN0aW5nIjp0cnVlfQ==; dtm_token=AAAFqpmGZPnoSwBJojxIAAAAAAE; __qca=P0-194401613-1712575777635; OptanonAlertBoxClosed=2024-04-12T07:42:07.359Z; optimizelyEndUserId=oeu1712575697506r0.05273052206960971; AMCV_6B61EE6A54FA17010A4C98A7%40AdobeOrg=-1124106680%7CMCIDTS%7C19860%7CMCMID%7C81709133174155428357968145689486395526%7CMCAAMLH-1716445766%7C12%7CMCAAMB-1716445766%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1715848166s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C5.2.0; rr_rcs=eF5jYSlN9jBJSbNMSzYw001KMTfSNTFMMdG1NEoy1jUyMDNONTAwtzA0SuPKLSvJTOEzMjDVNdQ1BACJjw3G; utag_main__sn=14; utag_main_dc_visit=14; cto_bundle=QDlotF9raVA5MyUyRnNEa0o5VXpRNXRrJTJGZGdtZXNVNWtoTE1rZVhiS1dKU3BpRHF1eHNBQVJ6SklLNW5XNndPUkhYOGdxN1VRJTJCU2JLR1NhWEtabWYlMkJTWnNwZE5rWWZEd0Y2emw4YnV6YTJOclJMMTlsdzl6SlY4NyUyRldOc3Fxa2cxdGpKZDZjT3VaVnYzYmNCN21MQlZpQTUzeTlnJTNEJTNE; cto_bundle=QDlotF9raVA5MyUyRnNEa0o5VXpRNXRrJTJGZGdtZXNVNWtoTE1rZVhiS1dKU3BpRHF1eHNBQVJ6SklLNW5XNndPUkhYOGdxN1VRJTJCU2JLR1NhWEtabWYlMkJTWnNwZE5rWWZEd0Y2emw4YnV6YTJOclJMMTlsdzl6SlY4NyUyRldOc3Fxa2cxdGpKZDZjT3VaVnYzYmNCN21MQlZpQTUzeTlnJTNEJTNE; mp_cdw_mixpanel=%7B%22distinct_id%22%3A%20%2218ebd775f248e8-0cd98796b35383-26001a51-1fa400-18ebd775f25d85%22%2C%22bc_persist_updated%22%3A%201712929195017%2C%22bc_id_cache%22%3A%20%22%7B%5C%22liveintent_hash%5C%22%3A-1382151851%7D%22%7D; _rdt_uuid=1715842044674.4ca3a29b-17d9-47d4-8860-b838021f67c8; needlepin=N190d171257570203344639001c2d2819c894d5819fa67c7819fa7b22003242000819d2f51023200000001411819fa6838000000000dmktnumb2024Q21411819fa7a3e41277000cinvTargeted21413819ce0c7b412d8; 4112525968F44D5C99DF0BDE0C235561=_991210|2024-05-17,6068169|2024-05-16,6716541|2024-05-16,999603|2024-05-16,1005635|2024-05-16,6605095|2024-05-16,7133096|2024-05-16,5441720|2024-05-16,6695911|2024-05-16,4058087|2024-05-16,7308045|2024-05-16,2007473|2024-05-16; AKA_A2=A; _abck=587159A2838E87CD1CDA7A35764E10AC~0~YAAQTvzaF83WEe2PAQAAheFyBgwRws9A0m3BvsZUwraBKbXFOgfwTM9LLFzP962yO2qbRXy8n8ZstzzU7Dx6InbvaaN+ACAXQuI2ajt8Wx/Cpbm1TShC00nf8lpmAj7s88QGgKHOEnUjwaG83ruedwuFB3YXG7A5ScVZTcka847G7ol5QDkBO91ygQPmiYIDkfJClhP0s26/kmoH5fyE8Hz+zvzwxNFglHQcmX4xRpwpD/S6XQJu5LQl8KAUYvbNscdrgXNPzj/XGo4D0lpLQROydGBOad9mkU9FeTsTZRnHaAcgPn7WhoPnh4m3oPRJPVBSATiLV2/YomF2Fxa8QRUdcnV+dLtdADy+EWzKp6xZjo63/WqN707bXLgcJMesmaAdy/vvqzLV/kt9l7B50Qz53ZOI~-1~-1~-1; 70549A6B29AD46CF90DA19BC17972419=E_w8faArDhGs4HNoQBgTBM0E8WJly8kMG5te1tgY2JpRsnW9ulpS8_5P88hqd7NbKcKSgPrfqQE5k5deM3goOnYLwpM1; ak_bmsc=D643ED7FC297E23D904297E674A51EB2~000000000000000000000000000000~YAAQENYsF5fw7wWQAQAAfFF8BhjvlbTMFwQ9KwakUGy1uak94fw0kGoHHJI2/wu+c3t7xX2EV92+uSdDlH8x/g8ZwIPXu925HX0vQlz3BOAsRk3m69yn+W7v7QBw890MJHxo4H47M3waO9NMMGbRiOEvspI5vwIdxU+uHeVRGwKvhaYJAAr9XNiBVRtltDyXANZzPqgPUslNckVa4yzl3U36F8XOJfejehY+l6wt5KyCYlJcJS530NWMQrhHuv1QE4+C9Qy+Sg9r3KGe/ZHgq4Oltzys1GdyjPIseuwAoXLph4Q++Krwuwow/XGLCPWLCDBlk7n/IaiVm6yL9yvN7rFjkRvV3Bl+1d8NiJUv0XqI0dfmb5JBvROXvZUdjvkLoCP6owIeHhJ9kqjDH6eq4YocsqlQoW/gSmiIiqWCdUoSNTD5lZNjsytP9LipVs7m5KyExDnBWherujYn/9lTkUCJoJ8SHy7QJUGxV3SpkLS/HZ4Fjhd0g5nFITBNPDyrVWmYNDKXLgEiW+5THcCA/g==; 265B10B0AD854F37A02410D8F39E9723=F0AF03C5-4DF3-4877-AB17-DF7DFFD4B54F; CartKey=87d1be2dbc424a4090f20fa60f420f17; A8A8F83D13EA4F8B917AA5F211762060=3590BC5EA12746A5907EE6FCB9215603; BA9AA5C91598458BA251A10B273627B6=6D6C4838AD9041988203F1DBF8C984E5; bm_sz=58EF64E6F141D20C757964E22DA2F8B8~YAAQENYsFybz7wWQAQAAz5x8BhjrR0nXDdM4KHY3yzMWP1aBGu9av9Y5O9edwP8XEV7grmr/FRrju+vf/4oVnEFk/5IF/ZnPCBhbsqXu/gh6YuqDjdG0CICbZhlcx9MF/TAlU12skVnrUJGSYqDiiFq7b01ommUjvbzl/lUM56LUz/a4+64Wh3GD9EHsioYpKR4czSKethLS7JJMueLGxYneR4HMePp4qD23Z2RaGqr3OrKAXM3eR+gBE1U+Ye+HH99j/iUGaZjJHSI/5A5f0VXWH+ZkzM2tdPRm0Fpgiv4SRRRv7ulOLdUKvtDG7Yr34XP0cyQSRqEnBhNpCo3NV7O1GboxvJRMX9L4qswJt87ndKVrhbpApLawJhntWzucE8jvVzPinV1N3G3Fh28EnAVh9Q==~4403769~4403248; OptanonConsent=isGpcEnabled=0&datestamp=Tue+Jun+11+2024+14%3A19%3A08+GMT%2B0530+(India+Standard+Time)&version=202310.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=decdab39-cbd7-4460-aa8a-aaee7e17e4e0&interactionCount=2&landingPath=NotLandingPage&groups=C0003%3A1%2CC0004%3A1%2CC0001%3A1%2CC0002%3A1&AwaitingReconsent=false&geolocation=US%3BNY; bm_mi=3DCE7864C8A2213A49E41611309815CD~YAAQENYsF78Q8AWQAQAA6rmABhihhMyjpLe6EjYKt27081dK2UdgyUP5LiqfaPSGD9cLaOXdjNzuokksRwcUSRO9wsZT+t3s2s1Yr4etZ8z7PLeNaspCJOuvkw+OBUb0LnzjxYJPzU4ssgNlQhmoLFX+tFpbrS01OosgY9s20Qh1H0OxsEORBCe+TQwfukPgFShmm2RyDuxAI8YylkOvhUf0Y9Kk/KlsUq3TLo7JKO+yZSb1btBNV17wTFkbWHONhen2KosSpZRVDHU+aDiNsVVWyr3sd95UgF4uZHPYWlEzYueqIJ4yVi+EXfLw82AkvmzpgUg9o+PNGHnyb3E1/8C1Zl9K9CxhPS2HHb3/Mizm8AjDzNio~1; bm_sv=6460E45FBBC3F622A4863BCA89B152BD~YAAQENYsF8AQ8AWQAQAA6rmABhhbIpeV0SnT292cdVV1fDJnOHRjLmBdqWsyeiJE+4WKpUDxhB+fcu7QWpdeBO/mFJg0wYjjLnxfNHRTp3LHM2Umb/uLaP1IubT90Fbr8EKHV/kuLex8pALXNGx0dXOLU/5u4jDxfeQFzg3IaPuKOAZYvgkSMv8Ng7S9cwWjYh3foggeuyKAGV6wS0KFgHRaELqhKg8h38bWq9NiAJCNCgZXRvUniBkaBJ2Ngw==~1',
                'priority': 'u=0, i',
                'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            }

            yield scrapy.Request(
                url=data[1],
                callback=self.parse,
                headers=headers,
                cookies=cookies,
                dont_filter=True,
                meta={'url':data[1],'counter':self.counter}
            )
            count+=1
            if count == 10:
                print('Taking Time for 5 seconds')
                time.sleep(5)
                count=0

    def parse(self, response,**kwargs):

        item = IcsV1SiteMapLinksItemfinal()
        url = response.meta['url']
        if "search-scope-pagination-range" in response.text:
            count = response.xpath('//div[@class="search-scope-pagination-range"]//text()').getall()[-1].replace(' of ','').replace(',','')

        else:
            count = '1'
        counter = response.meta['counter']
        urls = response.xpath('//h2//a[@class="search-result-product-url"]//@href').getall()

        if urls:
            for i in urls:
                item['vendor_id'] = self.VENDOR_ID
                item['vendor_name'] = self.VENDOR_NAME
                item['product_urls'] = 'https://www.cdw.com' + i
                yield item

            if int(count) > 24:
                self.counter = self.counter + 1
                next_page = f'{url}&pcurrent={self.counter}'
                if self.counter <= (int(count) / 24) + 1:
                    if next_page:
                        next_page = f'{url}&pcurrent={self.counter}'
                        yield scrapy.Request(url=next_page, callback=self.parse,
                                             meta={'counter': self.counter, 'url': url, 'count': count})
            try:
                update = f'update {db.sitemap_table_3} set status="Done" where product_urls="{url}"'
                self.cursor.execute(update)
                self.con.commit()
                print("UPDATE_DONE....")
            except Exception as e:
                print(e)

        else:

            import requests

            cookies = {
                'optimizelyEndUserId': 'oeu1712575697506r0.05273052206960971',
                'utag_main_random_number': '82',
                'utag_main_vapi_domain': 'cdw.com',
                's_ecid': 'MCMID%7C82866238473463775800964311901517671853',
                '_lc2_fpi': '464f01cb1133--01htyqetnd6j5tx8js4p359yms',
                '_lc2_fpi_meta': '{%22w%22:1712575703725}',
                'bluecoreNV': 'false',
                '__pdst': '547a7d8ce71a41188859329071657eaa',
                '_gcl_au': '1.1.1139124387.1712575777',
                'dtm_token_sc': 'AAAFqpmGZPnoSwBJojxIAAAAAAE',
                'sa-user-id': 's%253A0-cf2bd0e9-397d-5b0f-6fe8-41dd6746fe18.mgiMlCBzSyG%252FxU%252BA9PmUtb7XLPXlvOXlJAcNLGIl%252F6A',
                'sa-user-id-v2': 's%253AzyvQ6Tl9Ww9v6EHdZ0b-GNi9Ino.xWLDBdQTrV%252FPv5SktADY6upV0iMZHr1TacTJ80SQUL0',
                'sa-user-id-v3': 's%253AAQAKIB1wL9arrE34uZ-bbJ7x-sL9GFVWaDWm6ZpMeYpbNzZ7EHwYBCChqs-wBjABOgT7-sM6QgSokc3j.Okx5bzHT7sa9yoDgNUGtDIp0QkkqVtkEIIJAI%252FJYV00',
                '_uetvid': '48a13200f59b11ee96b33d46f5f65e04',
                'utag_main_v_id': '018ebd78925b0099dc1f51afd1a00506f009406700bd0',
                '_fbp': 'fb.1.1712575779584.825896845',
                '__qca': 'P0-426454749-1712575777635',
                '_hjSessionUser_68143': 'eyJpZCI6Ijk5MTdlOGQ2LTU5YTQtNTk2MS1hNjRkLWJlYmM2ZDE3N2E1ZiIsImNyZWF0ZWQiOjE3MTI1NzU3ODM3NDMsImV4aXN0aW5nIjp0cnVlfQ==',
                'dtm_token': 'AAAFqpmGZPnoSwBJojxIAAAAAAE',
                '__qca': 'P0-194401613-1712575777635',
                'OptanonAlertBoxClosed': '2024-04-12T07:42:07.359Z',
                'optimizelyEndUserId': 'oeu1712575697506r0.05273052206960971',
                'AMCV_6B61EE6A54FA17010A4C98A7%40AdobeOrg': '-1124106680%7CMCIDTS%7C19860%7CMCMID%7C81709133174155428357968145689486395526%7CMCAAMLH-1716445766%7C12%7CMCAAMB-1716445766%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1715848166s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C5.2.0',
                'rr_rcs': 'eF5jYSlN9jBJSbNMSzYw001KMTfSNTFMMdG1NEoy1jUyMDNONTAwtzA0SuPKLSvJTOEzMjDVNdQ1BACJjw3G',
                'utag_main__sn': '14',
                'utag_main_dc_visit': '14',
                'cto_bundle': 'QDlotF9raVA5MyUyRnNEa0o5VXpRNXRrJTJGZGdtZXNVNWtoTE1rZVhiS1dKU3BpRHF1eHNBQVJ6SklLNW5XNndPUkhYOGdxN1VRJTJCU2JLR1NhWEtabWYlMkJTWnNwZE5rWWZEd0Y2emw4YnV6YTJOclJMMTlsdzl6SlY4NyUyRldOc3Fxa2cxdGpKZDZjT3VaVnYzYmNCN21MQlZpQTUzeTlnJTNEJTNE',
                'cto_bundle': 'QDlotF9raVA5MyUyRnNEa0o5VXpRNXRrJTJGZGdtZXNVNWtoTE1rZVhiS1dKU3BpRHF1eHNBQVJ6SklLNW5XNndPUkhYOGdxN1VRJTJCU2JLR1NhWEtabWYlMkJTWnNwZE5rWWZEd0Y2emw4YnV6YTJOclJMMTlsdzl6SlY4NyUyRldOc3Fxa2cxdGpKZDZjT3VaVnYzYmNCN21MQlZpQTUzeTlnJTNEJTNE',
                'mp_cdw_mixpanel': '%7B%22distinct_id%22%3A%20%2218ebd775f248e8-0cd98796b35383-26001a51-1fa400-18ebd775f25d85%22%2C%22bc_persist_updated%22%3A%201712929195017%2C%22bc_id_cache%22%3A%20%22%7B%5C%22liveintent_hash%5C%22%3A-1382151851%7D%22%7D',
                '_rdt_uuid': '1715842044674.4ca3a29b-17d9-47d4-8860-b838021f67c8',
                'needlepin': 'N190d171257570203344639001c2d2819c894d5819fa67c7819fa7b22003242000819d2f51023200000001411819fa6838000000000dmktnumb2024Q21411819fa7a3e41277000cinvTargeted21413819ce0c7b412d8',
                '4112525968F44D5C99DF0BDE0C235561': '_991210|2024-05-17,6068169|2024-05-16,6716541|2024-05-16,999603|2024-05-16,1005635|2024-05-16,6605095|2024-05-16,7133096|2024-05-16,5441720|2024-05-16,6695911|2024-05-16,4058087|2024-05-16,7308045|2024-05-16,2007473|2024-05-16',
                'AKA_A2': 'A',
                '_abck': '587159A2838E87CD1CDA7A35764E10AC~0~YAAQTvzaF83WEe2PAQAAheFyBgwRws9A0m3BvsZUwraBKbXFOgfwTM9LLFzP962yO2qbRXy8n8ZstzzU7Dx6InbvaaN+ACAXQuI2ajt8Wx/Cpbm1TShC00nf8lpmAj7s88QGgKHOEnUjwaG83ruedwuFB3YXG7A5ScVZTcka847G7ol5QDkBO91ygQPmiYIDkfJClhP0s26/kmoH5fyE8Hz+zvzwxNFglHQcmX4xRpwpD/S6XQJu5LQl8KAUYvbNscdrgXNPzj/XGo4D0lpLQROydGBOad9mkU9FeTsTZRnHaAcgPn7WhoPnh4m3oPRJPVBSATiLV2/YomF2Fxa8QRUdcnV+dLtdADy+EWzKp6xZjo63/WqN707bXLgcJMesmaAdy/vvqzLV/kt9l7B50Qz53ZOI~-1~-1~-1',
                '70549A6B29AD46CF90DA19BC17972419': 'E_w8faArDhGs4HNoQBgTBM0E8WJly8kMG5te1tgY2JpRsnW9ulpS8_5P88hqd7NbKcKSgPrfqQE5k5deM3goOnYLwpM1',
                '265B10B0AD854F37A02410D8F39E9723': 'F0AF03C5-4DF3-4877-AB17-DF7DFFD4B54F',
                'CartKey': '87d1be2dbc424a4090f20fa60f420f17',
                'A8A8F83D13EA4F8B917AA5F211762060': '3590BC5EA12746A5907EE6FCB9215603',
                'BA9AA5C91598458BA251A10B273627B6': '6D6C4838AD9041988203F1DBF8C984E5',
                'bm_mi': '3DCE7864C8A2213A49E41611309815CD~YAAQENYsF78Q8AWQAQAA6rmABhihhMyjpLe6EjYKt27081dK2UdgyUP5LiqfaPSGD9cLaOXdjNzuokksRwcUSRO9wsZT+t3s2s1Yr4etZ8z7PLeNaspCJOuvkw+OBUb0LnzjxYJPzU4ssgNlQhmoLFX+tFpbrS01OosgY9s20Qh1H0OxsEORBCe+TQwfukPgFShmm2RyDuxAI8YylkOvhUf0Y9Kk/KlsUq3TLo7JKO+yZSb1btBNV17wTFkbWHONhen2KosSpZRVDHU+aDiNsVVWyr3sd95UgF4uZHPYWlEzYueqIJ4yVi+EXfLw82AkvmzpgUg9o+PNGHnyb3E1/8C1Zl9K9CxhPS2HHb3/Mizm8AjDzNio~1',
                'bm_sv': '6460E45FBBC3F622A4863BCA89B152BD~YAAQENYsF6ER8AWQAQAA5NWABhhlSdqfgn/KqiedQR41WP5Z5sc4Le7Wy+tSEC58s3tIiQw/YSiBzx3lOAmzL6Vm0izH3Q3AX18bxCiP2MgpEZeVDlz5ErRB5mf6ppNdHY/SPMhRyLs0aSUavAFdZAiwFZURaVWwNn6vYK6+eAuOIbsg5/4enNNdyiqMW4qxYRY/O/Kv6afbMc7b/V0oj4GkPZJdJXeT1Zx6OWMk0zBIJuY8mFXUb8XGAugxVQ==~1',
                'ak_bmsc': 'D643ED7FC297E23D904297E674A51EB2~000000000000000000000000000000~YAAQENYsF0468AWQAQAASmCHBhi3XoU0otFd9U8SnpqgzQIB79n7LcnF6rYKcOE8BJ5za1jXc9pjy8t9LgcYU1gecBKoF0ySJDLpARD4edYBx9C/Vkw6CZm4l9bIU/DIJHMOx/dRxn/Q/iaSDJEZlvPNftT0e0CvToZHE8o+ALTl/EJlW1Z2ZRCcvBVe52fNwgYi4HqrjfRvyDhHiJ19CYKGlN5rlAjAdJ/KvwlZciy3G9IxbTW3ryd3qi8htzBInOIplEPqxgk5SWZaPIviJjbDm6/LkWeQ+RrE7UgfUYDLtnJGJkLus2fcaVoV1sY5E0olPR+/vw+LbtRs0SjjHc4iMsQRzWW8mlkhX6pQmtgNAMdsaZ6lViWphUTDJyK1cFLWJO//oPe2d9hX2zuG0WuS1Bowwtlv/4ir95iBfC3Sx15NmGoWmPQc82d0ILIyIsjCJ9kchmwO+0i/FRF/bcZDEr7nYPfvw67k4sZOih6BAL8PIpnbmdSN2bZDu+FMqUDg6jqsGmPyR7EGosXX+6094pwfUxRyrZAY',
                'bm_sz': '58EF64E6F141D20C757964E22DA2F8B8~YAAQENYsF2Q68AWQAQAAPmOHBhipkrLCXEV7bMheIkF6v4gjTaPKbN5zP82DrrfoczGgNoF6ma+f7eHSMfF4AMAwbDqx0SKb2txmYIawaVnd3wUk1OrMdE/UYQzU8UpLQrQeDjLPA1w3ZHMQASGtUaHEGX8NFw1CrTEsLJlsevED4YAZ+xX0Te4hcaA65LkWFfAItuI7YhaD8KxabZ4G0p2HJ7OL/GcQ/bEX5y+5UjLMd1mtWgTVZgP6vi15mLjlx5JShb1JmhqsCa/Sm9dhXx4C9g/rhahcv0vS2jx1FfdUiiso2t+cYVNbsDHtaXZHTjyCl9z08rPZXDxrjEKxwrZx9cOl9fWSdycgbk00JwKzaxGjriVhpeUWYRiUrFMXZwo7Z/vtuPtI/Tx2QeOBFXbDL0s8c6pffp6G9r7kpqrpheQMqR0t~4403769~4403248',
                'OptanonConsent': 'isGpcEnabled=0&datestamp=Tue+Jun+11+2024+14%3A30%3A55+GMT%2B0530+(India+Standard+Time)&version=202310.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=decdab39-cbd7-4460-aa8a-aaee7e17e4e0&interactionCount=2&landingPath=NotLandingPage&groups=C0003%3A1%2CC0004%3A1%2CC0001%3A1%2CC0002%3A1&AwaitingReconsent=false&geolocation=US%3BNY',
            }

            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'en-US,en;q=0.9',
                'cache-control': 'max-age=0',
                # 'cookie': 'optimizelyEndUserId=oeu1712575697506r0.05273052206960971; utag_main_random_number=82; utag_main_vapi_domain=cdw.com; s_ecid=MCMID%7C82866238473463775800964311901517671853; _lc2_fpi=464f01cb1133--01htyqetnd6j5tx8js4p359yms; _lc2_fpi_meta={%22w%22:1712575703725}; bluecoreNV=false; __pdst=547a7d8ce71a41188859329071657eaa; _gcl_au=1.1.1139124387.1712575777; dtm_token_sc=AAAFqpmGZPnoSwBJojxIAAAAAAE; sa-user-id=s%253A0-cf2bd0e9-397d-5b0f-6fe8-41dd6746fe18.mgiMlCBzSyG%252FxU%252BA9PmUtb7XLPXlvOXlJAcNLGIl%252F6A; sa-user-id-v2=s%253AzyvQ6Tl9Ww9v6EHdZ0b-GNi9Ino.xWLDBdQTrV%252FPv5SktADY6upV0iMZHr1TacTJ80SQUL0; sa-user-id-v3=s%253AAQAKIB1wL9arrE34uZ-bbJ7x-sL9GFVWaDWm6ZpMeYpbNzZ7EHwYBCChqs-wBjABOgT7-sM6QgSokc3j.Okx5bzHT7sa9yoDgNUGtDIp0QkkqVtkEIIJAI%252FJYV00; _uetvid=48a13200f59b11ee96b33d46f5f65e04; utag_main_v_id=018ebd78925b0099dc1f51afd1a00506f009406700bd0; _fbp=fb.1.1712575779584.825896845; __qca=P0-426454749-1712575777635; _hjSessionUser_68143=eyJpZCI6Ijk5MTdlOGQ2LTU5YTQtNTk2MS1hNjRkLWJlYmM2ZDE3N2E1ZiIsImNyZWF0ZWQiOjE3MTI1NzU3ODM3NDMsImV4aXN0aW5nIjp0cnVlfQ==; dtm_token=AAAFqpmGZPnoSwBJojxIAAAAAAE; __qca=P0-194401613-1712575777635; OptanonAlertBoxClosed=2024-04-12T07:42:07.359Z; optimizelyEndUserId=oeu1712575697506r0.05273052206960971; AMCV_6B61EE6A54FA17010A4C98A7%40AdobeOrg=-1124106680%7CMCIDTS%7C19860%7CMCMID%7C81709133174155428357968145689486395526%7CMCAAMLH-1716445766%7C12%7CMCAAMB-1716445766%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1715848166s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C5.2.0; rr_rcs=eF5jYSlN9jBJSbNMSzYw001KMTfSNTFMMdG1NEoy1jUyMDNONTAwtzA0SuPKLSvJTOEzMjDVNdQ1BACJjw3G; utag_main__sn=14; utag_main_dc_visit=14; cto_bundle=QDlotF9raVA5MyUyRnNEa0o5VXpRNXRrJTJGZGdtZXNVNWtoTE1rZVhiS1dKU3BpRHF1eHNBQVJ6SklLNW5XNndPUkhYOGdxN1VRJTJCU2JLR1NhWEtabWYlMkJTWnNwZE5rWWZEd0Y2emw4YnV6YTJOclJMMTlsdzl6SlY4NyUyRldOc3Fxa2cxdGpKZDZjT3VaVnYzYmNCN21MQlZpQTUzeTlnJTNEJTNE; cto_bundle=QDlotF9raVA5MyUyRnNEa0o5VXpRNXRrJTJGZGdtZXNVNWtoTE1rZVhiS1dKU3BpRHF1eHNBQVJ6SklLNW5XNndPUkhYOGdxN1VRJTJCU2JLR1NhWEtabWYlMkJTWnNwZE5rWWZEd0Y2emw4YnV6YTJOclJMMTlsdzl6SlY4NyUyRldOc3Fxa2cxdGpKZDZjT3VaVnYzYmNCN21MQlZpQTUzeTlnJTNEJTNE; mp_cdw_mixpanel=%7B%22distinct_id%22%3A%20%2218ebd775f248e8-0cd98796b35383-26001a51-1fa400-18ebd775f25d85%22%2C%22bc_persist_updated%22%3A%201712929195017%2C%22bc_id_cache%22%3A%20%22%7B%5C%22liveintent_hash%5C%22%3A-1382151851%7D%22%7D; _rdt_uuid=1715842044674.4ca3a29b-17d9-47d4-8860-b838021f67c8; needlepin=N190d171257570203344639001c2d2819c894d5819fa67c7819fa7b22003242000819d2f51023200000001411819fa6838000000000dmktnumb2024Q21411819fa7a3e41277000cinvTargeted21413819ce0c7b412d8; 4112525968F44D5C99DF0BDE0C235561=_991210|2024-05-17,6068169|2024-05-16,6716541|2024-05-16,999603|2024-05-16,1005635|2024-05-16,6605095|2024-05-16,7133096|2024-05-16,5441720|2024-05-16,6695911|2024-05-16,4058087|2024-05-16,7308045|2024-05-16,2007473|2024-05-16; AKA_A2=A; _abck=587159A2838E87CD1CDA7A35764E10AC~0~YAAQTvzaF83WEe2PAQAAheFyBgwRws9A0m3BvsZUwraBKbXFOgfwTM9LLFzP962yO2qbRXy8n8ZstzzU7Dx6InbvaaN+ACAXQuI2ajt8Wx/Cpbm1TShC00nf8lpmAj7s88QGgKHOEnUjwaG83ruedwuFB3YXG7A5ScVZTcka847G7ol5QDkBO91ygQPmiYIDkfJClhP0s26/kmoH5fyE8Hz+zvzwxNFglHQcmX4xRpwpD/S6XQJu5LQl8KAUYvbNscdrgXNPzj/XGo4D0lpLQROydGBOad9mkU9FeTsTZRnHaAcgPn7WhoPnh4m3oPRJPVBSATiLV2/YomF2Fxa8QRUdcnV+dLtdADy+EWzKp6xZjo63/WqN707bXLgcJMesmaAdy/vvqzLV/kt9l7B50Qz53ZOI~-1~-1~-1; 70549A6B29AD46CF90DA19BC17972419=E_w8faArDhGs4HNoQBgTBM0E8WJly8kMG5te1tgY2JpRsnW9ulpS8_5P88hqd7NbKcKSgPrfqQE5k5deM3goOnYLwpM1; 265B10B0AD854F37A02410D8F39E9723=F0AF03C5-4DF3-4877-AB17-DF7DFFD4B54F; CartKey=87d1be2dbc424a4090f20fa60f420f17; A8A8F83D13EA4F8B917AA5F211762060=3590BC5EA12746A5907EE6FCB9215603; BA9AA5C91598458BA251A10B273627B6=6D6C4838AD9041988203F1DBF8C984E5; bm_mi=3DCE7864C8A2213A49E41611309815CD~YAAQENYsF78Q8AWQAQAA6rmABhihhMyjpLe6EjYKt27081dK2UdgyUP5LiqfaPSGD9cLaOXdjNzuokksRwcUSRO9wsZT+t3s2s1Yr4etZ8z7PLeNaspCJOuvkw+OBUb0LnzjxYJPzU4ssgNlQhmoLFX+tFpbrS01OosgY9s20Qh1H0OxsEORBCe+TQwfukPgFShmm2RyDuxAI8YylkOvhUf0Y9Kk/KlsUq3TLo7JKO+yZSb1btBNV17wTFkbWHONhen2KosSpZRVDHU+aDiNsVVWyr3sd95UgF4uZHPYWlEzYueqIJ4yVi+EXfLw82AkvmzpgUg9o+PNGHnyb3E1/8C1Zl9K9CxhPS2HHb3/Mizm8AjDzNio~1; bm_sv=6460E45FBBC3F622A4863BCA89B152BD~YAAQENYsF6ER8AWQAQAA5NWABhhlSdqfgn/KqiedQR41WP5Z5sc4Le7Wy+tSEC58s3tIiQw/YSiBzx3lOAmzL6Vm0izH3Q3AX18bxCiP2MgpEZeVDlz5ErRB5mf6ppNdHY/SPMhRyLs0aSUavAFdZAiwFZURaVWwNn6vYK6+eAuOIbsg5/4enNNdyiqMW4qxYRY/O/Kv6afbMc7b/V0oj4GkPZJdJXeT1Zx6OWMk0zBIJuY8mFXUb8XGAugxVQ==~1; ak_bmsc=D643ED7FC297E23D904297E674A51EB2~000000000000000000000000000000~YAAQENYsF0468AWQAQAASmCHBhi3XoU0otFd9U8SnpqgzQIB79n7LcnF6rYKcOE8BJ5za1jXc9pjy8t9LgcYU1gecBKoF0ySJDLpARD4edYBx9C/Vkw6CZm4l9bIU/DIJHMOx/dRxn/Q/iaSDJEZlvPNftT0e0CvToZHE8o+ALTl/EJlW1Z2ZRCcvBVe52fNwgYi4HqrjfRvyDhHiJ19CYKGlN5rlAjAdJ/KvwlZciy3G9IxbTW3ryd3qi8htzBInOIplEPqxgk5SWZaPIviJjbDm6/LkWeQ+RrE7UgfUYDLtnJGJkLus2fcaVoV1sY5E0olPR+/vw+LbtRs0SjjHc4iMsQRzWW8mlkhX6pQmtgNAMdsaZ6lViWphUTDJyK1cFLWJO//oPe2d9hX2zuG0WuS1Bowwtlv/4ir95iBfC3Sx15NmGoWmPQc82d0ILIyIsjCJ9kchmwO+0i/FRF/bcZDEr7nYPfvw67k4sZOih6BAL8PIpnbmdSN2bZDu+FMqUDg6jqsGmPyR7EGosXX+6094pwfUxRyrZAY; bm_sz=58EF64E6F141D20C757964E22DA2F8B8~YAAQENYsF2Q68AWQAQAAPmOHBhipkrLCXEV7bMheIkF6v4gjTaPKbN5zP82DrrfoczGgNoF6ma+f7eHSMfF4AMAwbDqx0SKb2txmYIawaVnd3wUk1OrMdE/UYQzU8UpLQrQeDjLPA1w3ZHMQASGtUaHEGX8NFw1CrTEsLJlsevED4YAZ+xX0Te4hcaA65LkWFfAItuI7YhaD8KxabZ4G0p2HJ7OL/GcQ/bEX5y+5UjLMd1mtWgTVZgP6vi15mLjlx5JShb1JmhqsCa/Sm9dhXx4C9g/rhahcv0vS2jx1FfdUiiso2t+cYVNbsDHtaXZHTjyCl9z08rPZXDxrjEKxwrZx9cOl9fWSdycgbk00JwKzaxGjriVhpeUWYRiUrFMXZwo7Z/vtuPtI/Tx2QeOBFXbDL0s8c6pffp6G9r7kpqrpheQMqR0t~4403769~4403248; OptanonConsent=isGpcEnabled=0&datestamp=Tue+Jun+11+2024+14%3A30%3A55+GMT%2B0530+(India+Standard+Time)&version=202310.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=decdab39-cbd7-4460-aa8a-aaee7e17e4e0&interactionCount=2&landingPath=NotLandingPage&groups=C0003%3A1%2CC0004%3A1%2CC0001%3A1%2CC0002%3A1&AwaitingReconsent=false&geolocation=US%3BNY',
                'priority': 'u=0, i',
                'referer': 'https://www.cdw.com/search/cables/ethernet-cables/?w=BD&b=MKI',
                'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            }

            response = requests.get(url=url, cookies=cookies,
                                    headers=headers)

            response = Selector(response.text)

            urls = response.xpath('//h2//a[@class="search-result-product-url"]//@href').getall()

            if urls:
                for i in urls:
                    item['vendor_id'] = self.VENDOR_ID
                    item['vendor_name'] = self.VENDOR_NAME
                    item['product_urls'] = 'https://www.cdw.com' + i
                    yield item

                if int(count) > 24:
                    self.counter = self.counter + 1
                    next_page = f'{url}&pcurrent={self.counter}'
                    if self.counter <= (int(count) / 24) + 1:
                        if next_page:
                            next_page = f'{url}&pcurrent={self.counter}'
                            yield scrapy.Request(url=next_page, callback=self.parse,
                                                 meta={'counter': self.counter, 'url': url, 'count': count})
                try:
                    update = f'update {db.sitemap_table_3} set status="Done" where product_urls="{url}"'
                    self.cursor.execute(update)
                    self.con.commit()
                    print("UPDATE_DONE....")
                except Exception as e:
                    print(e)


            # print('response_issue')
            # try:
            #     update = f'update {db.sitemap_table_3} set status="response_issue" where product_urls="{url}"'
            #     self.cursor.execute(update)
            #     self.con.commit()
            #     print("UPDATE_DONE....")
            # except Exception as e:
            #     print(e)

        if counter == int(count)/24:
            print('hello')
        else:
            return

if __name__ == '__main__':
        execute(f"scrapy crawl links_main -a start=124 -a end=124".split())
