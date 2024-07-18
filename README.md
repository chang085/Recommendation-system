# Movie Recommendation System

## I. Giới thiệu

Dự án này cung cấp một hệ thống đề xuất phim (Movie Recommendation System) cho người dùng. Mục tiêu là tạo ra một nền tảng cho phép người dùng nhận được các đề xuất phim mới dựa trên dữ liệu về các phim mà họ đã xem.

## II. Cài đặt

Để cài đặt và chạy dự án này trên máy của bạn, hãy làm theo các bước sau:

1. Cài đặt các gói phụ thuộc:
    ```bash
    pip install numpy scipy
    ```
    ```bash
    pip install pandas scipy
    ```
3. Khởi chạy hệ thống:
    ```bash
    python RS.py
    ```

## III. Hướng dẫn sử dụng

### 1. Khởi động hệ thống

Đầu tiên, hãy đảm bảo rằng bạn đã cài đặt các gói phụ thuộc và khởi chạy hệ thống theo các bước trong phần cài đặt. Sau đó, chạy file `RS.py` để bắt đầu hệ thống đề xuất phim.

### 2. Đăng ký hoặc đăng nhập

Khi hệ thống bắt đầu, bạn sẽ thấy một lựa chọn để đăng nhập hoặc đăng ký:

- **Đăng ký**: 
  - Nhập tên của bạn.
  - Nhập mật khẩu.
  - Nhập tuổi.
  - Nhập giới tính.
  - Sau khi đăng ký, bạn sẽ được tự động đăng nhập.

- **Đăng nhập**: 
  - Nhập tên và mật khẩu của bạn.
  - Nếu thông tin đúng, bạn sẽ được đăng nhập vào hệ thống.

### 3. Nhận đề xuất phim

Sau khi đăng nhập, bạn có thể nhận các đề xuất phim dựa trên sở thích cá nhân và dữ liệu của bạn:

- **Dành cho người dùng mới**:
  - Hệ thống sẽ đề xuất các phim được đánh giá cao nhất và các phim phổ biến nhất.
  - Các phim này sẽ được hiển thị ngay sau khi bạn đăng ký hoặc đăng nhập thành công.

- **Dành cho người dùng hiện tại**:
  - Hệ thống sẽ dự đoán các phim bạn có thể thích dựa trên các phim bạn đã xem và đánh giá trước đó.
  - Để nhận các dự đoán này, hãy chọn "Predicted Ratings for New Movies" sau khi đăng nhập thành công.

### 4. Đề xuất dựa trên giới tính

- Nếu bạn muốn nhận đề xuất dựa trên giới tính, hệ thống sẽ cung cấp danh sách các phim phù hợp với sở thích của nam hoặc nữ:
  - **Nam**: Phim thuộc thể loại Hành động, Phiêu lưu, Tội phạm, Kinh dị.
  - **Nữ**: Phim thuộc thể loại Chính kịch.

  Để nhận các đề xuất này, hệ thống sẽ tự động phân loại sau khi bạn đăng nhập dựa trên giới tính bạn cung cấp khi đăng ký.

### 5. Dự đoán đánh giá phim

- Hệ thống có thể dự đoán các đánh giá phim mà bạn chưa xem dựa trên sự tương đồng với người dùng khác.
- Các dự đoán này sẽ được hiển thị dưới dạng danh sách các phim cùng với dự đoán đánh giá của bạn cho mỗi phim.

## IV. Tổng kết

Dự án này giúp người dùng quản lý thông tin cá nhân, dữ liệu phim và đánh giá phim một cách dễ dàng và hiệu quả. Hệ thống đề xuất phim cung cấp nhiều tính năng để người dùng có thể khám phá các phim mới dựa trên sở thích cá nhân và xu hướng hiện tại. Nếu bạn có bất kỳ câu hỏi hoặc góp ý nào, vui lòng liên hệ với chúng tôi qua email: 22010085@st.phenikaa-uni.edu.vn
