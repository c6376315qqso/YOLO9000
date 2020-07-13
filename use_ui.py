import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from test import *
from PIL import Image, ImageQt


class MyTestWindow(QDialog, Ui_Dialog):
    def __init__(self):
        super(MyTestWindow, self).__init__()
        self.setupUi(self)
        self.image = None
        self.openButton.clicked.connect(self.slot_btn_chooseimage)
        self.detect9000Button.clicked.connect(self.slot_btn_dect9000)
        self.detectv2Button.clicked.connect(self.slot_btn_dectv2)
        self.saveButton.clicked.connect(self.slot_btn_save)
        self.clearButton.clicked.connect(self.slot_btn_clear)


    def slot_btn_chooseimage(self):
        image_path, ok = QFileDialog.getOpenFileName(self, '打开图片', filter='image file(*.jpg *.bmp *.png)')
        if not ok:
            return
        if self.image:
            self.image.close()
        self.image = Image.open(image_path)
        print(self.image.size)
        self.resize(self.image.size[0], self.image.size[1]+50)
        self.disPicture.setPixmap(QPixmap(image_path))

    def slot_btn_dect9000(self):
        if not self.image:
            QMessageBox.critical(self, '错误', '没有加载图片', QMessageBox.Yes)
            return
        from detect_yolo9000 import detect9000
        detected_image = detect9000(self.image.copy())
        self.disPicture.setPixmap(ImageQt.toqpixmap(detected_image))

    def slot_btn_dectv2(self):
        if not self.image:
            QMessageBox.critical(self, '错误', '没有加载图片', QMessageBox.Yes)
            return
        from detect_yolov2 import detectv2
        detected_image = detectv2(self.image.copy())
        self.disPicture.setPixmap(ImageQt.toqpixmap(detected_image))

    def slot_btn_save(self):
        if not self.image:
            QMessageBox.critical(self, '错误', '没有加载图片', QMessageBox.Yes)
            return
        try:
            save_path, ok = QFileDialog.getSaveFileName(self, '选择文件夹', filter='*.jpg')
            if not ok:
                return
            save_image = ImageQt.fromqpixmap(self.disPicture.pixmap())
            if not save_image:
                QMessageBox.critical(self, '错误', '没有加载图片!', QMessageBox.Yes)
                return
            print(save_path)
            save_image.save(save_path, quality=90)
        except:
            QMessageBox.critical(self, '错误', '保存文件失败!', QMessageBox.Yes)
            print('error while saving image!')
            return
        QMessageBox.information(self, 'YOLO系统', '保存成功!', QMessageBox.Yes)

    def slot_btn_clear(self):
        self.image = None
        self.disPicture.setPixmap(QPixmap(''))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyTestWindow()
    myWin.show()
    sys.exit(app.exec_())
