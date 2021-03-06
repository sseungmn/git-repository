from PyQt5.QtWidgets import QApplication, QWidget, QToolTip, QPushButton 
from PyQt5 import QtWebEngineWidgets
from PyQt5.QtGui import QFont
import folium, sys, glob, os, json, requests, io
import pandas as pd
import numpy as np

KAKAO_RESTAPI_KEY='8fa6416a77b3813a841d2808c0f7b1e5'
GOOGLEMAP_KEY='AIzaSyDZNfQvIoC2csKlVe-dThVkTf1eeo3YEo4'

class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        QToolTip.setFont(QFont('SansSerif', 10))

        self.setToolTip('This is a <b>QWidget</b> widget')

        btn = QPushButton('Button', self)
        btn.setToolTip('This is a <b>QPushButton</b> widget')
        btn.resize(btn.sizeHint())
        btn.move(50, 50)

        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Tooltips')
        self.show()


class dr:

    path = 'Data/'
    file = glob.glob(os.path.join(path+"*.xlsx"))[0]
    df = pd.read_excel(file, sheet_name='대여소현황')

    dataset=df[['대여소_구', '대여소명', '대여소주소', '위도', '경도', '거치대수']]

    dr_songpa = dataset[dataset['대여소_구'].str.contains('송파구')]
    dr_songpa.index=range(len(dr_songpa))
    data_size = len(dr_songpa)
    loc = [37.4952, 127.130]

    map_dr = folium.Map(location = loc, zoom_start=12)

    for i in range(data_size):
        folium.Marker(list(dr_songpa.iloc[i][['위도','경도']]),
                popup = dr_songpa.iloc[i][['대여소주소']],
                icon=folium.Icon(color='green')).add_to(map_dr)

    def find_location(self, address):
        url = f'https://dapi.kakao.com/v2/local/search/keyword.json?query={address}'
        headers = {
            "Authorization": f"KakaoAK {KAKAO_RESTAPI_KEY}"
            }
        places = requests.get(url, headers = headers).text
        jObject = json.loads(places).get("documents")[0]
        des = [jObject.get('x'), jObject.get('y')]
        return des

    def find_closest(self, address):
        min_ = 10000
        val = 0
        now = self.find_location(address)

        for i in range(self.data_size):
            temp = int(1000*np.sqrt(
                np.square(float(self.dr_songpa.iloc[i][['위도']]-float(now[1]))) +
                np.square(float(self.dr_songpa.iloc[i][['경도']]-float(now[0]))))
                )
            if min_ > temp:
                val = i
                min_ = temp
            
            return self.dr_songpa.iloc[val]

if __name__ == '__main__':

    app = QApplication(sys.argv)
    m = dr().map_dr
    data = io.BytesIO()
    m.save(data, close_file=False)

    w = QtWebEngineWidgets.QWebEngineView()
    w.setHtml(data.getvalue().decode())
    w.resize(640, 480)
    w.show()
    sys.exit(app.exec_())
