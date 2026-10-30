# UniApp - Member 4 + Admin GUI + Registration

Phần triển khai Member 4 trên code gốc của Group 7: **University Menu + Database + GUIUniApp + Integration/Testing**.

## Phạm vi thay đổi

| File | Trách nhiệm Member 4 |
| --- | --- |
| `main.py` | Entry point chọn CLI/GUI, file dữ liệu và chế độ demo |
| `cli_uni_app.py` | University Menu A/S/X; gọi Student/Admin subsystem hiện có |
| `database.py` | Tạo, đọc, ghi, tìm và clear Student objects trong file; giữ format pickle cũ |
| `gui_controller.py` | Kết nối GUI với validation của Member 1, enrolment của Member 2 và tính average của Member 3 |
| `gui_uni_app.py` | Điều phối các cửa sổ Student/Admin, đăng nhập/đăng ký và style dùng chung |
| `registration_gui.py` | Form tạo tài khoản Student: tên, email, password và xác nhận password |
| `admin_gui.py` | Dashboard Admin, tìm kiếm, nhóm điểm/PASS/FAIL và xác nhận xoá |
| `admin_gui_controller.py` | Xác thực Admin riêng, kiểm tra phiên đăng nhập và thao tác database |
| `demo_data.py` | Tạo tài khoản demo trong file riêng để chạy thử sau khi tải source |
| `tests/` | Kiểm thử Database, các kết nối giữa module, CLI qua stdin và widget Tkinter thật |
| `environment.yml`, `requirement.txt` | Môi trường conda và package cho kiểm thử |

**Giữ nguyên nội dung** `subject.py`, `student_controller.py`, `subject_controller.py` và `admin_controller.py` của Members 1-3. Trong `student.py`, đã sửa `remove_subject()` để xoá đúng ID được chọn thay vì luôn xoá môn đầu tiên; đoạn hàm cũ được giữ bằng comment `##`. Không khôi phục các bản đã sửa toàn bộ nghiệp vụ trước đây.

Code gốc của `main.py` và `database.py` được giữ ở cuối file bằng comment `##`. Các class/function của Member 4 có docstring mô tả chức năng.

## Setup

Cài Git và tải source từ GitHub:

```powershell
git clone https://github.com/quangtohe/UniApp.git
cd UniApp
```

Cài Miniconda/Anaconda, mở terminal trong thư mục chứa `main.py` rồi chạy:

```powershell
conda env create -f environment.yml
conda activate uniapp-group7
python main.py --gui --demo
```

Trên máy hiện tại, môi trường `D:\UniApp\.conda` vẫn có sẵn:

```powershell
Set-Location D:\UniApp
.\.conda\python.exe main.py --gui --demo
```

App chỉ dùng thư viện chuẩn Python và Tkinter. Package `tk` được cài bằng conda; pytest dùng cho kiểm thử và được khai báo trong `requirement.txt`.

Nếu đã có một conda env với Python 3.12 và Tk:

```powershell
python -m pip install -r requirement.txt
```

## Đăng nhập demo

| Vai trò | Email | Password | Lệnh mở |
| --- | --- | --- | --- |
| Student | `preview@university.com` | `Abcde123` | `python main.py --gui --demo` |
| Admin | `admin@university.com` | `Admin123` | `python main.py --gui --admin --demo` |

Chọn **Student** hoặc **Admin** trên màn hình đăng nhập. Trong chế độ demo, chọn vai trò sẽ điền sẵn đúng tài khoản tương ứng; bấm **Sign in**. Sau khi logout, các trường được xoá; chọn lại vai trò để điền demo lần nữa.

Tài khoản Admin là identity riêng, không được thêm vào danh sách Student và không thể đăng nhập vào trang enrolment. Tài khoản Student không thể đăng nhập Admin. Hai dashboard dùng chung `demo.data` khi chạy với `--demo`.

Tài khoản Admin demo chỉ được chấp nhận khi có `--demo`. Credentials demo cũng được ghi ở đầu `environment.yml` để nhóm dễ tìm. File YAML mô tả môi trường cài đặt; credentials demo được định nghĩa tại `demo_data.py`.

### Student demo

```powershell
python main.py --gui --demo
```

- Email: `preview@university.com`
- Password: `Abcde123`
- GUI điền sẵn hai trường; bấm **Sign in**.
- `--demo` tự tạo `demo.data` cạnh source. Không cần file dữ liệu được đóng gói sẵn.
- Mở demo lần sau sẽ giữ các môn đã enrol và đưa password demo về `Abcde123`.
- CLI demo dùng cùng file: `python main.py --demo`.
- Chế độ demo không sửa file `students.data` hiện có.

### Admin demo và các bước showcase

```powershell
python main.py --gui --admin --demo
```

1. Bấm **Sign in** với tài khoản Admin đã được điền sẵn.
2. Xem Total students, Enrolments, PASS, FAIL và bảng ID/Name/Email/Subjects/Average/Grade/Result.
3. Chọn **Group by grade** hoặc **PASS / FAIL** ở danh sách cạnh ô tìm kiếm. Sinh viên chưa enrol được xếp **NOT GRADED**.
4. Tìm bằng tên, email hoặc ID; xoá nội dung tìm kiếm để xem lại tất cả.
5. Bấm **Refresh** để đọc thay đổi đã lưu bởi CLI hoặc Student GUI.
6. Chọn một dòng sinh viên, bấm **Remove selected student**. **Cancel** giữ dữ liệu; nút xác nhận chỉ xoá đúng sinh viên đó cùng các môn của họ.
7. **Clear all records** yêu cầu gõ chính xác `CLEAR` mới bật nút xác nhận. **Cancel** hoặc Escape huỷ thao tác.
8. **Log out** đóng dashboard/hộp thoại, xoá credentials và thu hồi phiên Admin.

Database demo mới tạo có một Student chưa enrol; có thể vào Student demo để enrol trước rồi xem kết quả trong Admin. Khi bị clear hoặc xoá, demo Student được tạo lại vào lần khởi động `--demo` tiếp theo; Admin vẫn đăng nhập được ngay cả khi danh sách sinh viên rỗng.

### Admin cho dữ liệu của bài tập

Với `students.data` hoặc `--data`, cấu hình tài khoản riêng trong terminal trước khi mở app:

```powershell
$env:UNIAPP_ADMIN_EMAIL = 'manager@university.com'
$env:UNIAPP_ADMIN_PASSWORD = 'ChooseYourOwnPassword123'
python main.py --gui --admin
# Hoặc: python main.py --gui --admin --data tmp/practice.data
```

Đặt password riêng của nhóm thay cho ví dụ trên. Không có cấu hình thì Admin GUI sẽ báo chưa được cấu hình. `--admin` chỉ chọn vai trò đăng nhập ban đầu và yêu cầu `--gui`; không bỏ qua xác thực. Cơ chế này phục vụ ứng dụng bài tập chạy cục bộ. Menu Admin CLI gốc vẫn hoạt động như trước và chưa có bước xác thực riêng.

## Dùng tài khoản thật của bài tập

Có thể đăng ký trực tiếp trong GUI:

```powershell
python main.py --gui
```

1. Chọn **Student**, bấm **Create student account**.
2. Nhập Full name, University email, Password và Confirm password.
3. Email phải kết thúc bằng `@university.com`. Password bắt đầu bằng chữ hoa, có ít nhất 5 chữ cái đứng trước ít nhất 3 chữ số ở cuối; ví dụ `Abcde123`.
4. Bấm **Create account** hoặc Enter. App kiểm tra các trường bắt buộc, format, xác nhận password và email trùng trước khi lưu.
5. Thành công sẽ trở về Login, hiện Student ID và điền sẵn email. Nhập password để **Sign in**.

**Back to sign in**, Escape hoặc đóng form sẽ huỷ thông tin chưa lưu. **Show passwords** hiện/ẩn cả hai trường password. Khi input sai hoặc lưu thất bại, thông báo lỗi xuất hiện trên form để sửa và thử lại. Đăng ký Student không tạo quyền Admin; nút đăng ký chỉ xuất hiện ở vai trò Student đã đăng xuất.

Form lưu vào file đang chọn: `students.data` mặc định, `demo.data` khi chạy `--demo`, hoặc file truyền qua `--data`. Student đăng ký bằng GUI có thể đăng nhập CLI và xuất hiện trong Admin dùng cùng file.

Để đăng ký bằng CLI, khởi động:

```powershell
python main.py
```

Tại University Menu, chọn `S` rồi `r`. Vì Student System được giữ nguyên từ Member 1, thứ tự đăng ký là **Name → Email → Password**. Ví dụ:

```text
Name: Test Student
Email: test@university.com
Password: Abcde123
```

Email/password được kiểm tra bằng chính các hàm validation hiện có của Member 1. Sau khi đăng ký, mở GUI:

```powershell
python main.py --gui
```

Hai chế độ này dùng chung `students.data`. Có thể dùng file riêng:

```powershell
python main.py --data tmp/practice.data
python main.py --gui --data tmp/practice.data
```

Không dùng đồng thời `--demo` và `--data`.

## Luồng CLI

```text
University System: (A)dmin, (S)tudent, or X :
    A -> AdminController.admin_menu()
    S -> StudentController.student_menu()
    X -> kết thúc ứng dụng
```

Member 4 chỉ thêm University Menu. Các submenu bên dưới giữ đúng lựa chọn trong code gốc:

| Menu | Lựa chọn |
| --- | --- |
| Student | `l` login, `r` register, `x` trở về University |
| Subject Enrolment | `1` enrol, `2` show, `3` remove, `4` change password, `5` logout |
| Admin | `1` show, `2` group, `3` PASS/FAIL, `4` remove student, `5` clear, `6` trở về University |

Admin clear vẫn yêu cầu gõ `CLEAR`, theo code Member 3 đang có. Trả về từ Student/Admin sẽ tiếp tục vòng lặp University Menu. EOF/Ctrl+C được xử lý để kết thúc gọn.

## Các cửa sổ GUI

1. **Login:** Tk root chứa LoginView, email/password, nút Sign in và Show password.
2. **Enrolment:** Toplevel hiển thị tên/ID, số môn, average, overall grade; có Enrol, View subjects, Refresh overview và Log out.
3. **Subjects:** Toplevel riêng hiển thị Subject ID/Mark/Grade; chọn một dòng để bật **Remove selected subject**, có xác nhận trước khi xoá, empty state khi chưa có môn và Back to overview.
4. **Exception:** Toplevel báo lỗi thiếu trường, format sai, credentials sai, enrol quá 4 môn hoặc lỗi đọc/ghi file. Got it/Enter/Escape đóng thông báo.
5. **Admin:** Toplevel riêng quản lý sinh viên, tìm kiếm và nhóm kết quả; chỉ mở sau khi xác thực Admin.
6. **Confirmation:** Toplevel xác nhận xoá môn, xoá một sinh viên hoặc clear; clear yêu cầu nhập `CLEAR`.
7. **Registration:** Toplevel đăng ký Student; xác nhận password, kiểm tra email trùng và chuyển về Login sau khi lưu thành công.

Nút Enrol vẫn nhận lần bấm thứ năm để hiển thị Exception window; dữ liệu không có môn thứ năm. Logout đóng các cửa sổ con, xoá credentials và đưa password về chế độ ẩn.

### Xoá môn trong GUI

1. Đăng nhập Student, bấm **View subjects**.
2. Chọn đúng dòng môn cần xoá, rồi bấm **Remove selected subject**.
3. Hộp thoại ghi rõ Subject ID; **Cancel** hoặc Escape huỷ thao tác, **Remove subject** xác nhận xoá.
4. Sau khi lưu thành công, bảng môn, số môn, average và grade được cập nhật. Xoá môn cuối cùng đưa tài khoản về trạng thái chưa có điểm và cho phép enrol lại.

Khi chưa chọn dòng hoặc danh sách rỗng, nút xoá bị vô hiệu hoá. Nếu lưu thất bại, GUI báo lỗi và giữ nguyên môn trong phiên hiện tại. Trước khi xoá, hệ thống đọc lại dữ liệu để kiểm tra môn và Student vẫn tồn tại. Đóng Subjects hoặc logout sẽ huỷ hộp thoại chưa xác nhận. Tài khoản Admin và các sinh viên khác không bị thay đổi khi Student xoá môn của mình.

Tkinter chỉ dùng một Tk root và một mainloop. Các cửa sổ khác kế thừa Toplevel. Màu/font/style tập trung trong PortalTheme; PortalSidebar dùng chung cho login và overview. Mỗi container dùng một geometry manager.

## Cách tích hợp với code hiện có

Các controller gốc đều tự tạo `Database()` và một số controller còn tạo controller con. `Database.configure_default()` được gọi tại startup để tất cả các constructor này dùng cùng file được chọn bởi `--data` hoặc `--demo`.

GUI cần nhận dữ liệu và exception, trong khi các hàm gốc của Member 1/2 có thao tác `input()`/`print()`. Vì vậy `GUIController` làm lớp kết nối:

- `authenticate()` dùng `validate_email()`/`validate_password()` của StudentController rồi đọc Student objects từ file.
- `enrol_subject()` lấy sinh viên mới nhất, kiểm tra giới hạn, gọi `SubjectController.enrol_subject()` gốc và đọc lại kết quả sau khi lưu. Output CLI của lời gọi này được giữ khỏi cửa sổ GUI.
- `remove_subject()` đọc lại Student, tìm đúng ID, gọi hàm model đã sửa và `SubjectController.save_student()`, rồi xác minh kết quả lưu trước khi cập nhật phiên GUI.
- `view_enrolment()` đọc lại danh sách môn để giao diện không dùng dữ liệu cũ.
- `summary()` dùng `AdminController.average_mark()` và `grade_from_average()` hiện có để hiển thị kết quả nhất quán với admin.

`AdminGUIController` kiểm tra phiên Admin trước mọi báo cáo/thao tác xoá, dùng lại `AdminController.average_mark()`/`grade_from_average()` và lưu qua Database. `AdminWindow` trình bày dữ liệu và mở hộp thoại xác nhận; không gọi các hàm `input()` của CLI. `GUIController.register_student()` dùng validator và bộ sinh ID của Member 1, tạo Student gốc và lưu qua Database. GUI kiểm tra thêm tên bắt buộc và xác nhận password. Các file controller gốc của Members 1-3 vẫn giữ nguyên.

## Database

- File mặc định `students.data` nằm cạnh `database.py`, độc lập với thư mục terminal.
- File chưa tồn tại sẽ được tạo cùng danh sách rỗng.
- File rỗng/hỏng được báo bằng DatabaseError, không tự reset.
- StudentUnpickler chỉ cho phép hai model gốc Student/Subject.
- Khi lưu, ghi snapshot vào file tạm trước, rồi dùng `os.replace()` thay file chính.
- Tra cứu, enrolment, xoá và clear đều đọc/ghi file qua Database.
- Chưa có khoá transaction giữa nhiều tiến trình; dùng một tiến trình ghi tại một thời điểm và Refresh để xem thay đổi từ giao diện khác.

## Integration/testing

```powershell
python -m pytest -q --basetemp=tmp/pytest
```

Đã xác minh **90 passed, 0 skipped**. Các test dùng file tạm và không sử dụng database chính. Test GUI dùng một Tk interpreter, giữ cửa sổ ẩn; nếu máy không có display, cần kiểm tra GUI lại trên máy có giao diện.

| File test | Nội dung |
| --- | --- |
| `tests/test_member4_integration.py` | Tương thích pickle gốc, file lỗi, lỗi lưu atomic, cùng file cho controller lồng nhau, đăng ký CLI/login GUI, enrol bằng Member 2, average bằng Member 3, account bị xoá, CLI stdin, demo và option startup |
| `tests/test_member4_gui.py` | Luồng Student, đăng ký, Admin, chọn/huỷ/xác nhận xoá môn, cập nhật chỉ số, lỗi lưu, dữ liệu cũ và logout huỷ thao tác chờ |
| `tests/test_admin_gui_controller.py` | Quyền Admin, tài khoản riêng, cấu hình demo/thật, ranh giới điểm, PASS/FAIL, tìm kiếm, xoá chính xác, clear và startup flags |
| `tests/test_gui_registration.py` | Validation đăng ký, email trùng, giữ password/enrolments cũ, ID duy nhất, đăng nhập CLI/Admin đọc được account mới và lỗi lưu |
| `tests/test_subject_removal.py` | Model/CLI xoá đúng môn, adapter GUI đọc dữ liệu mới, giữ nguyên tài khoản khác, lỗi lưu không đổi phiên và xoá hết rồi enrol lại |
| `tests/conftest.py` | Tạo database riêng cho từng test và đăng ký sinh viên qua code Member 1 gốc |

## Điểm cần phối hợp với Members 1-3

Đã sửa lỗi `Student.remove_subject()` so sánh một subject với chính nó: dùng biến lặp riêng và đối chiếu với ID môn được yêu cầu. CLI chọn `3. Remove a subject` và GUI chọn **Remove selected subject** đều lưu danh sách sau khi xoá đúng môn.

Luồng đổi password gốc chưa kiểm tra format hoặc confirmation. Password không hợp lệ được lưu có thể không qua validation khi đăng nhập sau đó; phần này cần phối hợp với Member 2.

Các submenu Subject/Admin vẫn dùng số; nhóm có thể phối hợp đổi wording/phím cho khớp hoàn toàn sample I/O của đề. Các kiểm thử Member 4 ở đây xác minh tích hợp với API hiện có, không khẳng định toàn bộ nghiệp vụ của Members 1-3 đã hoàn tất.

## Demo phần Member 4

1. Chạy `python main.py --gui --demo`; thử để trống hoặc nhập sai để hiện cửa sổ lỗi.
2. Login bằng tài khoản demo; mở View subjects khi chưa có môn.
3. Enrol 4 lần; thử lần 5 và kiểm tra bảng vẫn có 4 môn.
4. Logout/login lại để chứng minh enrolments được đọc từ file.
5. Chạy `python main.py --demo`; vào Student và Admin rồi trở về University.
6. Chạy test và mở code main/Database/GUIController để giải thích vai trò tích hợp.

Khi chia sẻ source, không kèm `.conda`, package cache, `tmp`, dữ liệu tài khoản thật hoặc file `.env`. ZIP Member 4 chứa toàn bộ source cần chạy cùng README và các file setup.
