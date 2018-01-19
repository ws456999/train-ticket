# coding: utf-8

"""Train tickets query via command-line

Usage: tickets [-gdctkz] <from> <to> <date>

Options:
  -h, --help        显示帮助菜单
  -g                高铁
  -c                城际
  -d                动车
  -t                特快
  -k                快速
  -z                直达

Example:
  tickets 南京 北京 2016-07-01
  tickets -dg 南京 北京 2016-07-01

"""

# 不小心爬虫爬错了，爬到www.12306.com去了，但是就这样吧

from docopt import docopt
from stations import stations
from prettytable import PrettyTable
from colorama import Fore

import requests

seatCodeMap = {
  '9': 0,
  'M': 1,
  'O': 2,
  '6': 3,
  '4': 4,
  '3': 5,
  '2': 6,
  '1': 7,
  'W': 8,
}

headers = '车次 出发/到达 出发/到达时间 历时 商务 一等 二等 高软 软卧 硬卧 软座 硬座 无座'.split()
# 添加颜色
def colored(color, string):
  return ''.join([getattr(Fore, color.upper()), string, Fore.RESET])

# 过滤车型
def filterType(row):
  arguments = docopt(__doc__)
  option = (''.join([key for key, value in arguments.items() if value is True])).replace('-', '')
  if (option == ''): return True
  return row['trainCode'][0].lower() in option

# 获取车次数据
def getData():
  arguments = docopt(__doc__)
  from_station = stations.get(arguments['<from>'])
  to_station = stations.get(arguments['<to>'])
  date = arguments['<date>']
# 构建URL
  url = 'http://api.12306.com/v1/train/trainInfos?purpose_codes=ADULT&deptDate={}&deptStationCode={}&arrStationCode={}'.format(
    date, from_station, to_station
  )
  r = requests.get(url)
  return r.json()['data']['trainInfos']

# 构建table
def createTable(rows):
  pt = PrettyTable()
  pt._set_field_names(headers)

  rows = filter(filterType, rows)
  for row in rows:
    what = ['--']*9
    for seat in row['seatList']:
      position = seatCodeMap[seat['seatCode']]
      what[position] = seat['seatNum']

    pt.add_row([
      row['trainCode'],
      colored('red', row['deptStationName']) + '\n' + colored('green', row['arrStationName']),
      colored('red', row['deptDate'] + ' ' + row['deptTime']) + '\n' + colored('green', row['arrDate'] + ' ' + row['arrTime'])
      ,
      row['runTime'],
    ] + what)
  print(pt)

# 初始化
def cli():
  rows = getData()
  createTable(rows)

if __name__ == '__main__':
  cli()
