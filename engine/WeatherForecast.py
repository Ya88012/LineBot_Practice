import requests
import csv
from math import *

def ForeCast(lat, lon):
	result = ""
	def geodistance(lng1, lat1, lng2, lat2):
		lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])
		dlon = lng2 - lng1
		dlat = lat2 - lat1
		a = sin(dlat/2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon/2) ** 2 
		distance = 2 * asin(sqrt(a)) * 6371
		return distance

	#用經緯度查詢天氣狀況
	def OWM_Search_Coordinates(lat, lon):
		result = ""
		Url = "http://api.openweathermap.org/data/2.5/weather?appid=ca281c48bc140757eb22cae1a90b6179&lat={}&lon={}".format(lat, lon)
		Res = requests.get(Url).json()
		# print(Res)
		if Res["cod"] == 200:
				result += "城市名稱： "+Res["name"]+"\n"
				result += "經度： "+str(Res["coord"]["lon"])+"\t"
				result += "緯度： "+str(Res["coord"]["lat"])+"\n"
				result += "天氣狀況： "+Res["weather"][0]["description"]+"\n"
				result += "溫度： "+str(Res["main"]["temp"	])+"\n"
				result += "最高溫： "+str(float(Res["main"]["temp_max"])-273.15)+"\t"
				result += "最低溫： "+str(float(Res["main"]["temp_min"])-273.15)+"\n"
				result += "風速： "+str(Res["wind"]["speed"])
		else:
			result += Res["message"]

		return result

	#用經緯度查詢輻射站資訊
	def RadiationSearch(lat2, lon2):
		Url = "https://quality.data.gov.tw/dq_download_csv.php?nid=6095&md5_url=ddbe148a00d339f228fc8e4337968057"
		WebContent = requests.get(Url)
		WebContent.encoding = 'UTF-8'

		# print(WebContent.text)
		# Info = WebContent.text.split("\n")
		# for Row in Info:
		# 	Temp = Row.split(",")
		# 	print(Temp)

		StationList = []
		Info = csv.reader(WebContent.text.splitlines(), dialect="excel", delimiter=",")
		for Row in Info:
			StationList.append(Row)
		# print(StationList)

		Min = 1000000000
		for i in range(1,len(StationList)):
			k = geodistance(float(StationList[i][4]), float(StationList[i][5]), lon2, lat2)
			# print(k)
			if k < Min:
				Min = k
				MinStation = StationList[i][0]
				MinRadiation = float(StationList[i][2])

		return ("{} 微西弗 在 {} 站".format(MinRadiation, MinStation))

	def AQIAlarm(lat, lon):
		Url = "https://quality.data.gov.tw/dq_download_csv.php?nid=40448&md5_url=a7467aba7dc5f7f79f51d757dd7cbf52"
		WebContent = requests.get(Url)
		Info = csv.reader(WebContent.text.splitlines(), dialect="excel", delimiter=",")
		StationList = []

		for row in Info:
			StationList.append(row)

		Min = 1000000000
		for i in range(1,len(StationList)):
			# print(StationList[i])
			if StationList[i][-1] != "" and StationList[i][-2] != "":
				k = geodistance(float(StationList[i][-2]), float(StationList[i][-1]), lon, lat)
				if k < Min:
					# print(k)
					Min = k
					MinStation = StationList[i][0]
					if 0 < int(StationList[i][2]) and int(StationList[i][2]) <= 50:
						AQI = "綠色"
					elif 50 < int(StationList[i][2]) and int(StationList[i][2]) <= 100:
						AQI = "黃色"
					elif 100 < int(StationList[i][2]) and int(StationList[i][2]) <= 150:
						AQI = "橘色"
					elif 150 < int(StationList[i][2]) and int(StationList[i][2]) <= 200:
						AQI = "紅色"
					elif 200 < int(StationList[i][2]) and int(StationList[i][2]) <= 300:
						AQI = "紫色"
					elif 300 < int(StationList[i][2]) and int(StationList[i][2]) <= 500:
						AQI = "棗紅色"
					PM25 = int(StationList[i][11])

		return "AQI指數為{}警報\nPM2.5：{}\t\t在{}測得#".format(AQI, PM25, MinStation)

	result += OWM_Search_Coordinates(lat, lon)
	result += RadiationSearch(lat, lon)
	result += AQIAlarm(lat, lon)
	return result