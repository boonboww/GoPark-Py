# GoPark-Py


# 🚗 GoPark-PY – Dịch vụ Nhận diện Biển số Xe (ALPR Service)

## 📌 Giới thiệu

**GoPark-PY** là một dịch vụ Python hỗ trợ **Automatic License Plate Recognition (ALPR)** – nhận diện và trích xuất biển số xe từ hình ảnh.
Dự án này được thiết kế như một dịch vụ độc lập, dễ tích hợp vào các ứng dụng quản lý bãi đỗ xe hoặc hệ thống giám sát.

## ⚙️ Chức năng chính

* Phát hiện và đọc biển số xe từ ảnh.
* Tiền xử lý ảnh để tăng độ chính xác nhận diện.
* Kết quả trả về dưới dạng văn bản.
* Dễ dàng mở rộng hoặc tích hợp API.

## 🛠️ Yêu cầu hệ thống

* Python >= 3.8
* Thư viện cần thiết (khai báo trong `requirements.txt`):

  ```bash
  pip install -r requirements.txt
  ```
* Cài đặt Tesseract OCR:

  * Windows: [Hướng dẫn cài đặt](https://github.com/UB-Mannheim/tesseract/wiki)
  * Linux/macOS:

    ```bash
    sudo apt install tesseract-ocr
    ```

## 🚀 Cách sử dụng

1. Tạo môi trường ảo và cài đặt thư viện:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```
2. Chạy dịch vụ:

   ```bash
   python alpr_service.py --image path/to/image.jpg
   ```

## 📂 Cấu trúc dự án

```
GOPARK-PY/
├── __pycache__/        # Cache của Python
├── venv/               # Virtual environment
├── alpr_service.py     # File chính chạy dịch vụ ALPR
├── requirements.txt    # Danh sách thư viện cần thiết
└── README.md           # Tài liệu dự án
```

## 📑 Kết quả

Khi chạy thành công, chương trình sẽ:

* Hiển thị ảnh gốc và vùng chứa biển số xe.
* In ra văn bản biển số đã nhận diện.

## 🤝 Đóng góp

Mọi đóng góp (issues, pull request) đều được hoan nghênh để cải thiện hệ thống.


