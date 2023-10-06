# HBYS e-Sonuc
## Hastane Laboratuvar Sonuç Alma Sistemi - Sonuç Görüntüleyici
## Probel HBYS :hospital:
## Prolabsonuc :ambulance:

:uk: Hospital E-Result Data Monitoring and Reporting Application for Turkish Probel HBYS e-hospital systems

:tr: Probel tarafından tasarlanmış HBYS hastane laboratuvar sonuç alma (e-sonuç) sistemleri tarafından üretilen pdf dosyalarını analiz ederek test sonuçlarını ayıklamak ve görüntülemek amacıyla Python dilinde yazılmış bir araçtır.
Tüm Probel HBYS hastane sonuç alma sistemlerinin ürettiği tahlil sonuçlarıyla uyumlu çalışmaktadır.

Tüm pdf dosyaları sistemden indirilerek `pdf` klasörüne kopyalandıktan sonra scriptler çalıştırılmalıdır.
- :hospital: `generate.py` : PDF dosyalarını işler, onlardan yapılandırılmış verileri çıkarır ve verileri JSON formatında `data.json` dosyasına kaydeder. PDF'den HTML'ye dönüşüm için `pdf2htmlEX` aracını kullanır ve çeşitli veri çıkarma ve temizleme işlemleri gerçekleştirir.
- :chart_with_downwards_trend: `display.py`  : `data.json` dosyasındaki sonuç bilgilerini grafiksel olarak tarihe göre sıralanmış şekilde görüntüler.

---

## :star: PDF to JSON Data Conversion Script - generate.py
This script processes PDF files, extracts structured data from them, and saves the data in a JSON format.
The PDF files should be downloaded in the 'pdf' folder from any of Turkish 'Probel' hospital system

### Requirements:
- chardet: Character encoding detection library
- pdf2htmlEX: PDF to HTML conversion tool in 'exe' folder

### Usage:
1. Place your PDF files in the 'pdf' folder.
2. Run the script to process the PDF files and generate JSON data.

#### The script performs the following steps:
1. Converts PDF files to HTML format using pdf2htmlEX.
2. Extracts data from the generated HTML files.
3. Cleans and processes the extracted data.
4. Saves the cleaned data as a JSON file named 'data.json'.

## :star: JSON to Line Chart Visualization Script - display.py
This script visualizes special JSON data generated by the 'generate.py' script using line charts.
The data consists of blood-test results or similar tests in a well-known Turkish 'Probel' hospital system

### Requirements:
- matplotlib: comprehensive library for creating static, animated, and interactive visualizations in Python

### Usage:
1. Run the 'generate.py' with already downloaded PDF files in 'pdf' directory and have the 'data.json' file.
2. Run the script to visualize the data in the 'data.json' file.
3. Use the combobox or arrow buttons to navigate between different data.

## 📋 Gereksinimler (Requirements)
Before running the script, ensure you have the following requirements installed:
- Python 3.x
- Libraries listed in `requirements.txt`
- `pdf2htmlEX` tool in `exe` folder (from [pdf2htmlEX GitHub](https://github.com/coolwanglu/pdf2htmlEX/wiki/Download)

:uk: To install the necessary libraries, use:
Gerekli kütüphanelerin kurulumu için aşağıdaki komut çalıştırılmalıdır:
```
pip install -r requirements.txt
```

## :floppy_disk: Sonuçların İndirilmesi (Downloading Results)
TODO

## :syringe: Kullanım (Usage)
TODO
```
python generate.py
python display.py
```

## :bug: Known Issues
- `generate.py` - pdf : data without old value cannot be parsed because of the regexp in extract_lines_with_specified_format function.

## :pill: Future Improvements
- `display.py` - Show Last 6 months, 3 months...
- `display.py` - Show important event dates in the chart as vertical lines with text on them, have them in events.json with date and text.
- `display.py` - Zoom in out, select area in the chart
- Add CSV support, have csv directory and check both pdf and csv and process the existing files.

## :snowman: Author
Eray Öztürk ([@diffstorm](https://github.com/diffstorm))

## :heart_eyes: Credits
[pdf2htmlEX PDF to HTML renderer](https://github.com/coolwanglu/pdf2htmlEX) by [Lu Wang](https://github.com/coolwanglu)

## 🚔 LICENSE
This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.

```
This README.md file provides users with detailed information about how to use the HBYS e-Sonuc tool and its features. Users can also find detailed explanation about getting the data from HBYS e-sonuc system. Don't forget to include the necessary license information in your project.
```
