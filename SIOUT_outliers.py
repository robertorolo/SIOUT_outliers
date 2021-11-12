# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SIOUT_outliers.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

from PyQt5 import QtCore, QtGui, QtWidgets
import pandas as pd
import plotly.graph_objects as go
import numpy as np

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(534, 133)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.comboBox = QtWidgets.QComboBox(Dialog)
        self.comboBox.setObjectName("comboBox")
        self.gridLayout.addWidget(self.comboBox, 1, 1, 1, 1)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 0, 1, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 2, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.pushButton_3 = QtWidgets.QPushButton(Dialog)
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridLayout.addWidget(self.pushButton_3, 3, 1, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.pushButton.setText(_translate("Dialog", "Carregar extrato do SIOUT"))
        self.pushButton_2.setText(_translate("Dialog", "Mostrar boxplots"))
        self.label_2.setText(_translate("Dialog", "Selecionar bacia"))
        self.pushButton_3.setText(_translate("Dialog", "Exportar outliers em csv"))
        
        self.pushButton.clicked.connect(self.carregar)
        self.pushButton_2.clicked.connect(self.plotar)
        self.pushButton_3.clicked.connect(self.exportar)

    def carregar(self):
        file_path = QtWidgets.QFileDialog.getOpenFileName(None, "Select short term campaing file", "", "CSV files (*.csv)")
        file_path = file_path[0]
        df = pd.read_csv(filepath_or_buffer=file_path, sep=';', encoding= 'unicode-escape', error_bad_lines=False)
        bacias = list(df['Bacia Hidrográfica'].unique())
        self.bacias = bacias
        for idx, i in enumerate(bacias):
            if not isinstance(i, str):
                del bacias[idx]
        self.comboBox.addItems(bacias)
        self.df = df

    def plotar(self):
        bacia = str(self.comboBox.currentText()) 
        dff = self.df[self.df['Bacia Hidrográfica'] == bacia]
        vazoes = dff[['Vazão janeiro', 'Vazão fevereiro', 'Vazão março', 'Vazão abril', 'Vazão maio', 'Vazão junho', 'Vazão julho', 'Vazão agosto', 'Vazão setembro', 'Vazão outubro', 'Vazão novembro', 'Vazão dezembro']].values
        num = dff['Número do cadastro'].values
        stat = dff['Status'].values
        num_stat = ['{} - {}'.format(i,j) for i,j in zip(num, stat)]

        un = dff['Unidade de medida da vazão'].values
        
        vazoes_mes = []
        for i in range(12):
            vs = vazoes[:,i]
            vs = [float(j.replace(',','.')) for j in vs]
            vazoes_mes.append(vs)
        
        tick_label = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']
        
        fig = go.Figure()
        for v, m in zip(vazoes_mes, tick_label):
            fig.add_trace(go.Box(y=v, name=m, hovertext=num_stat, boxpoints='all'))
        
        fig.update_yaxes(title='Vazão (m³/s)')
        fig.update_layout(title={'text': '{} - {} Processos'.format(bacia, len(dff))})

        fig.show()
        
    def exportar(self):
        #outdf = pd.DataFrame(columns=['Número do cadastro', 'Status', 'Bacia Hidrográfica'])
        dataframes = []
        for b in self.bacias:
            for m in ['Vazão janeiro', 'Vazão fevereiro', 'Vazão março', 'Vazão abril', 'Vazão maio', 'Vazão junho', 'Vazão julho', 'Vazão agosto', 'Vazão setembro', 'Vazão outubro', 'Vazão novembro', 'Vazão dezembro']:
                dff = self.df[self.df['Bacia Hidrográfica'] == b]
                x = dff[m].values
                x = np.array([float(i.replace(',','.')) for i in x])
                upper_quartile = np.percentile(x, 75)
                lower_quartile = np.percentile(x, 25)
                IQR = (upper_quartile - lower_quartile) * 1.5
                quartileSet = (lower_quartile - IQR, upper_quartile + IQR)
                f =  x > quartileSet[1]
                
                dfconcat = dff[f][['Número do cadastro', 'Status', 'Bacia Hidrográfica']]
                dataframes.append(dfconcat)
        
        outdf = pd.concat(dataframes)
        outdf = outdf.drop_duplicates()
        outdf.to_csv('outliers.csv', index=False)
        print('Arquivo exportado para a pasta do programa')
        
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
