# Ứng dụng Tạo Truyện Tranh từ Văn Bản 🎨

## 📝 Giới thiệu
Ứng dụng Tạo Truyện Tranh là một công cụ cho phép người dùng chuyển đổi câu chuyện văn bản thành truyện tranh PDF đẹp mắt. Ứng dụng tích hợp các mô hình ngôn ngữ và hình ảnh tiên tiến để tạo ra trải nghiệm sáng tạo mượt mà.

![ui.png](ui.png)

## ✨ Tính năng chính
- **Nhập câu chuyện**: Nhập trực tiếp hoặc tải lên file .txt
- **Tùy chỉnh phong cách**: Lựa chọn giữa nhiều phong cách nghệ thuật (comic, anime, cổ tích, hiện thực)
- **Bố cục linh hoạt**: Hỗ trợ từ 1-6 khung hình với nhiều kiểu bố cục khác nhau
- **Tùy chỉnh văn bản**: Điều chỉnh cỡ chữ và vị trí hội thoại
- **Xuất PDF**: Tạo file PDF chất lượng cao với hình ảnh và nội dung câu chuyện

## 🚀 Cài đặt
1. Cài đặt Python 3.x
2. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

## 🔑 Yêu cầu
- OpenAI API Key để tạo hình ảnh
- Fonts Unicode (DejaVuSans hoặc ArialUnicode) cho hỗ trợ tiếng Việt

## 💻 Cách sử dụng
1. Khởi chạy ứng dụng:
```bash
python ui.kt.py
```

2. Giao diện người dùng gồm 4 tab chính:
   - **📝 Nhập câu chuyện**: Nhập nội dung hoặc tải file
   - **🎨 Phong cách truyện tranh**: Chọn số khung hình và phong cách
   - **✍️ Cài đặt văn bản**: Điều chỉnh font chữ và vị trí
   - **⚙️ Cài đặt nâng cao**: Tùy chỉnh bố cục và các tùy chọn khác

## 📐 Bố cục tùy chỉnh
Hỗ trợ định dạng JSON cho bố cục tùy chỉnh. Ví dụ:

### Bố cục 3 khung hình:
```json
[
  [0, 0, 0.6, 1],
  [0.6, 0, 0.4, 0.5],
  [0.6, 0.5, 0.4, 0.5]
]
```

### Bố cục 5 khung hình:
```json
[
  [0, 0, 0.6, 0.6],
  [0.6, 0, 0.4, 0.3],
  [0.6, 0.3, 0.4, 0.3],
  [0, 0.6, 0.3, 0.4],
  [0.3, 0.6, 0.7, 0.4]
]
```

## 🎯 Lưu ý khi sử dụng
- File câu chuyện nên ở định dạng .txt với encoding UTF-8
- Hỗ trợ tối đa 6 khung hình cho mỗi trang
- Đảm bảo đủ dung lượng ổ cứng cho việc lưu trữ hình ảnh và PDF
- Kiểm tra kết nối internet ổn định để tạo hình ảnh

## 🛠️ Cấu trúc thư mục
```
├── ui.kt.py              # Giao diện người dùng chính
├── mock_image_generation.py  # Tạo hình ảnh mẫu
├── image_generation.py   # Tạo hình ảnh thật
├── prompt_template.py    # Mẫu prompt cho việc tạo hình
├── Fonts/               # Thư mục chứa font
└── images/              # Thư mục lưu hình ảnh tạo ra
```