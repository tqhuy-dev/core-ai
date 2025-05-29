
# 📄 Tài liệu đặc tả tính năng: Truy thu cho nhân viên theo bộ phận

## 1. 🎯 Mục tiêu

Tự động xác định và tạo danh sách nhân viên cần **truy thu trách nhiệm** dựa trên:
- Thời gian đơn hàng lưu kho tại từng bưu cục
- Danh sách chức vụ bị truy thu (và chức vụ thay thế nếu không có ai phù hợp)
- Khoảng thời gian nhân viên làm việc tại bưu cục

## 2. 📌 Phạm vi áp dụng

- Áp dụng cho **phiếu rủi ro** được tạo với 1 hoặc nhiều **bưu cục được chỉ định**
- Xác định nhân viên bị truy thu theo từng bưu cục riêng biệt

## 3. 🧩 Thành phần dữ liệu chính

### 3.1. Đơn hàng

| Trường         | Ý nghĩa                                   |
|----------------|--------------------------------------------|
| order_id       | Mã đơn hàng                                |
| post_office_code | Mã bưu cục                              |
| stored_date    | Ngày lưu kho tại bưu cục tương ứng         |

### 3.2. Phiếu rủi ro

| Trường hợp                         | `start_day`           | `end_day`             |
|------------------------------------|------------------------|------------------------|
| Có `stored_date` tại bưu cục       | = `stored_date`        | = 23:00 ngày tạo phiếu |
| Không có `stored_date` tại bưu cục | = 00:00 ngày tạo phiếu | = 23:00 ngày tạo phiếu |

### 3.3. Cấu hình truy thu theo bưu cục

| Bưu cục        | Chức vụ     | Chức vụ thay thế              |
|----------------|-------------|-------------------------------|
| PO001          | Giao nhận   | Tổ trưởng, Phó giao nhận      |

### 3.4. Nhân viên theo bưu cục

| Mã nhân viên | Bưu cục | Chức vụ     | from_date   | to_date     |
|--------------|---------|-------------|-------------|-------------|
| EMP001       | PO001   | Giao nhận   | 2025-01-01  | *(null)*    |

to_date luôn lớn hơn from_date hoặc to_date bằng null
## 4. 🔁 Logic xác định nhân viên bị truy thu (theo từng bưu cục)

### Bước 1: Xác định `start_day` và `end_day` theo từng bưu cục

(Dựa theo bảng ở 3.2)

### Bước 2: Xác định danh sách **chức vụ áp dụng**

- Lấy danh sách nhân viên thuộc **chức vụ bị truy thu**
- Nếu không có nhân viên thuộc **chức vụ bị truy thu** → Lấy danh sách **chức vụ thay thế**
- Nếu không có ai hợp lệ, tạo phiếu lỗi

### Bước 3: Lọc theo thời gian làm việc của nhân viên

Điều kiện hợp lệ:

```
from_date ≤ end_day
và (to_date ≥ start_day hoặc to_date = null)
```

## 5. 📥 Kết quả đầu ra

| Trường             | Ý nghĩa                         |
|--------------------|---------------------------------|
| post_office_code   | Mã bưu cục                      |
| employees          | danh sách nhân viên bị truy thu |
| start_day / end_day | Mốc thời gian áp dụng theo phiếu |


