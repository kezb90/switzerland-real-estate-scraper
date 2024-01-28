import sys
import os
import re
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox, QFileDialog
import modules


class Form(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.priceList = [
            "50000 CHF",
            "100000 CHF",
            "150000 CHF",
            "200000 CHF",
            "300000 CHF",
            "400000 CHF",
            "500000 CHF",
            "600000 CHF",
            "700000 CHF",
            "800000 CHF",
            "900000 CHF",
            "1000000 CHF",
            "1250000 CHF",
            "1500000 CHF",
            "2000000 CHF",
            "2500000 CHF",
            "3000000 CHF",
            "4000000 CHF",
            "5000000 CHF",
        ]
        self.roomList = [
            "1",
            "1.5",
            "2",
            "2.5",
            "3",
            "3.5",
            "4",
            "4.5",
            "5",
            "5.5",
            "6",
            "6.5",
            "7",
            "7.5",
            "8",
        ]

        self.roomLabel = QtWidgets.QLabel("Room:")
        self.cityLabel = QtWidgets.QLabel("City:")
        self.priceLabel = QtWidgets.QLabel("Price:")
        self.typeLabel = QtWidgets.QLabel("Type:")

        self.cityEdit = QtWidgets.QLineEdit()

        self.priceSelect = QtWidgets.QComboBox()
        self.priceSelect.addItems(self.priceList)

        self.roomSelect = QtWidgets.QComboBox()
        self.roomSelect.addItems(self.roomList)

        self.typeSelect = QtWidgets.QComboBox()
        self.typeSelect.addItems(["buy", "rent"])

        self.crawlButton = QtWidgets.QPushButton("Submit")
        self.crawlButton.clicked.connect(self.crawlButtonClicked)

        self.image_dir_button = QtWidgets.QPushButton("Choose Image Directory")
        self.csv_dir_button = QtWidgets.QPushButton("Choose CSV Directory")

        # Add the new buttons to the layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.image_dir_button)
        layout.addWidget(self.csv_dir_button)
        layout.addWidget(self.cityLabel)
        layout.addWidget(self.cityEdit)
        layout.addWidget(self.priceLabel)
        layout.addWidget(self.priceSelect)
        layout.addWidget(self.typeLabel)
        layout.addWidget(self.typeSelect)
        layout.addWidget(self.roomLabel)
        layout.addWidget(self.roomSelect)
        layout.addWidget(self.crawlButton)

        self.setLayout(layout)
        self.image_dir_button.clicked.connect(self.choose_image_directory)
        self.csv_dir_button.clicked.connect(self.choose_csv_directory)

    image_dir = os.getcwd()
    csv_dir = os.getcwd()

    def choose_image_directory(self):
        image_dir = QFileDialog.getExistingDirectory(self, "Select Image Directory")
        if image_dir:
            # Store the selected directory for later use in the image saving logic
            self.image_dir = image_dir
        else:
            self.image_dir = os.getcwd()

    def choose_csv_directory(self):
        csv_dir = QFileDialog.getExistingDirectory(self, "Select CSV Directory")
        if csv_dir:
            # Store the selected directory for later use in the CSV saving logic
            self.csv_dir = csv_dir
        else:
            self.csv_dir = os.getcwd()

    def crawlButtonClicked(self):
        city = self.cityEdit.text()
        if not city:
            QMessageBox.warning(self, "Missing Information", "Please enter a city name")
        else:
            room = self.roomSelect.currentText()
            price_str = self.priceSelect.currentText()
            price = int(re.search(r"(\d+)", price_str).group(1))
            ad_type = self.typeSelect.currentText()
            # Call gather_data function to collect data from all possible urls
            data = modules.gather_data(str(ad_type), city, room, price)

            # Save all data into a csv file.
            print("Directory to save CSV file: ", f"{self.csv_dir}/output.csv")
            modules.save_data_as_csv(data, f"{self.csv_dir}/output.csv")
            # Save all images into a directory.
            print("Directory to save Image files: ", f"{self.image_dir}")

            for item in data:
                modules.save_images(
                    item["image_urls"], item["href"].replace("/", ""), self.image_dir
                )
            print("All Tasks Done Successfully!")
            # Show specific plot and statistic base on data
            # main.display_plot(data)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    form = Form()
    form.show()
    sys.exit(app.exec_())
