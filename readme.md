# UniApp - Group 7

Ứng dụng Python gồm CLIUniApp cho Student/Admin và GUIUniApp cho sinh viên đã đăng ký. CLI và GUI dùng chung các model, controller và file `students.data`.

## Setup nhanh sau khi clone hoặc tải ZIP từ GitHub

Cài Miniconda/Anaconda và Git trước, sau đó clone repository và tạo môi trường. Repo riêng tư yêu cầu tài khoản GitHub có quyền truy cập:

```powershell
git clone https://github.com/quangtohe/UniApp.git
cd UniApp
conda env create -f environment.yml
conda activate uniapp-group7
python main.py --gui --demo
```

Nếu tải ZIP, giải nén rồi mở terminal tại thư mục chứa `main.py` và `environment.yml`, bắt đầu từ lệnh `conda env create`.

Bấm **Sign in** với tài khoản demo đã được điền sẵn: `preview@university.com` / `Abcde123`. Chế độ demo tự tạo `demo.data`; không cần file dữ liệu được tải từ GitHub.

Chạy CLI demo hoặc kiểm thử:

```powershell
python main.py --demo
python -m pytest -q --basetemp=tmp/pytest
```

Để dùng tài khoản tự đăng ký, chạy `python main.py`, chọn `S` → `r` để tạo tài khoản, rồi mở `python main.py --gui`. Hai lệnh này cùng dùng `students.data`.

Repository không chứa conda env, cache, database tài khoản, file `.env`, ZIP build hoặc các tài liệu Canvas tải về. Các dependencies được khai báo trong `environment.yml` và `requirement.txt`; Tkinter được cài qua package `tk` của conda.

## Nguồn đã đọc và đối chiếu

Đã đọc tài liệu analysis/design 18 trang của nhóm, đề chính thức **Assessment 1 - Part 2 and Part 3** (11 trang), phần Python liên quan trong slide bài 6–10 và các ảnh sample I/O của đề Part 2. Truy cập Canvas UTS thành công qua BrowserOS neo MCP.

| Nguồn Canvas - môn 32555, Spring 2026 | Nội dung áp dụng |
| --- | --- |
| [Part 2: Software Development](https://canvas.uts.edu.au/courses/40838/assignments/276051), [đề Part 2 & Part 3](https://canvas.uts.edu.au/courses/40838/files/12414037?wrap=1) | Bốn menu, regex, lưu object, điểm trung bình, sample I/O, bốn cửa sổ GUI và rubric |
| [Bài 6: Classes and Objects](https://canvas.uts.edu.au/courses/40838/files/12417661?wrap=1) | Class, constructor, instance method, `__str__`, module Python |
| [Bài 7: Collections and Data Structure](https://canvas.uts.edu.au/courses/40838/files/12417665?wrap=1) | List chứa Student/Subject, lookup, remove, set chống trùng ID, dictionary nhóm kết quả |
| [Bài 8: Object Oriented Programming](https://canvas.uts.edu.au/courses/40838/files/12417671?wrap=1) | Trách nhiệm từng class; đặt tính điểm tại Student; menu lặp nhập lựa chọn; kế thừa widget Tkinter |
| [Bài 9: Files, Exceptions and Testing](https://canvas.uts.edu.au/courses/40838/files/12417677?wrap=1) | Đọc/ghi file, exception, custom exception, kiểm thử Python; slide có nhắc cả unittest và pytest |
| [Bài 10: Python GUI - Tkinter](https://canvas.uts.edu.au/courses/40838/files/12417683?wrap=1) | Một Tk root, Toplevel, Frame, Entry/StringVar, Button callback, geometry managers và MVC |

Các link cần tài khoản có quyền truy cập môn. Bản tải phục vụ đối chiếu nằm trong `tmp/course-materials/`, được loại khỏi Git và không cần để chạy app.

**Điều chỉnh so với tài liệu nhóm:** đề Part 2 trang 3 và ảnh sample trang 6 xác định grade/PASS/FAIL của **sinh viên theo điểm trung bình**, không phải nhóm từng môn. Rubric trang 8–9 yêu cầu bốn loại cửa sổ GUI. Triển khai hiện tại ưu tiên đề chính thức cho các điểm khác nhau này.

## Phân công

| Thành viên | Trách nhiệm | File chính |
| --- | --- | --- |
| Member 1 | Student System, register/login, validation, Student model | `student_controller.py`, `validator.py`, `student.py` |
| Member 2 | Enrol/view/remove subject, đổi mật khẩu, Subject/Grade; phối hợp Student model | `subject_controller.py`, `subject.py`, `grade.py`, `student.py` |
| Member 3 | Admin System: danh sách, nhóm grade, PASS/FAIL, xoá sinh viên, clear | `admin_controller.py` |
| Member 4 | University Menu, Database, GUI, integration/testing, hướng dẫn chạy | `main.py`, `cli_uni_app.py`, `database.py`, `gui_uni_app.py`, `tests/`, `environment.yml`, `requirement.txt` |

Đây là phân chia trách nhiệm theo module, không phải xác nhận đóng góp cá nhân đã thực hiện. Nhóm cần ghi lại đóng góp thực tế và chuẩn bị walkthrough phần của từng thành viên cho showcase.

## Kiến trúc và cách áp dụng bài giảng

- **Model:** Student sở hữu thông tin tài khoản, tối đa bốn Subject và các phương thức tính average/overall grade. Subject sinh mark và tính grade. Database đọc/ghi Student objects cùng enrolment.
- **Controller:** StudentController đăng ký/xác thực; SubjectController quản lý enrolment/password; AdminController quản lý báo cáo và xoá dữ liệu. Cả CLI và GUI dùng chung các service này.
- **View:** CLI là các vòng menu nhập lựa chọn. GUI gồm LoginView (Frame trên root), EnrolmentWindow, SubjectWindow và ExceptionWindow (các Toplevel riêng).
- **Tkinter:** chỉ một Tk root và một mainloop. Kế thừa Frame/Toplevel và gọi `super().__init__`. Mỗi container dùng một geometry manager; `grid` và `pack` chỉ được dùng ở các container khác nhau.
- **Trách nhiệm class:** tính điểm trung bình/grade tổng hợp ở Student, không lặp công thức trong view hoặc admin. Giá trị được tính từ danh sách môn hiện tại mỗi khi cần nên thay đổi ngay sau enrol/drop và đúng sau khi đọc lại file.
- **Tương thích:** giữ tên module/class controller hiện có và tên field của object cũ. Không ép đổi toàn bộ API sang tên trong diagram hoặc thêm inheritance không cần thiết. Các thay đổi nghiệp vụ đi qua method của model/controller.
- **Comment:** mọi class/function có docstring tiếng Anh mô tả chức năng. Code được thay thế vẫn nằm trong cùng file dưới các dòng `##`; bản gốc và bản trước khi đối chiếu Canvas đều được giữ. Khi nhóm sửa tiếp, giữ quy tắc comment code cũ rồi thêm code mới.

## Quy tắc nghiệp vụ

| Hạng mục | Hành vi |
| --- | --- |
| Email | Regex constant; phần tên hợp lệ, kết thúc bằng `@university.com`; phát hiện trùng và lookup không phân biệt hoa/thường |
| Password | Bắt đầu bằng chữ hoa; ít nhất 5 chữ cái ASCII liên tiếp, sau đó ít nhất 3 chữ số ASCII. Ví dụ `Abcde123`. Không tự xoá khoảng trắng của password |
| Student ID | Unique trong dữ liệu, từ `000001` đến `999999`, hiển thị đủ 6 chữ số |
| Subject ID | Môn mới lấy ID chưa dùng trong toàn bộ dữ liệu, từ `001` đến `999`; nếu hết ID thì báo lỗi |
| Mark | Số nguyên ngẫu nhiên từ 25 đến 100 |
| Grade của môn | Z: dưới 50; P: 50 đến dưới 65; C: 65 đến dưới 75; D: 75 đến dưới 85; HD: từ 85 |
| Average của sinh viên | Trung bình cộng của các môn đang enrol; đủ 4 môn thì chia 4. Không làm tròn trước khi phân loại; chỉ hiển thị 2 chữ số thập phân |
| Admin grouping | Mỗi sinh viên có điểm xuất hiện đúng một nhóm theo grade của average |
| PASS/FAIL | Average từ 50 là PASS, dưới 50 là FAIL. Chưa có môn thì NOT GRADED, không tự coi là FAIL |
| Đổi password | Phím `c`; kiểm tra format, yêu cầu Confirm Password, nhập lại confirmation nếu lệch; được dùng lại password hiện tại |
| Enrol limit | Kiểm tra bản ghi mới nhất từ file, tối đa 4 môn; lần thứ 5 hiển thị lỗi và không lưu thêm |

Đề ghi average của bốn môn và yêu cầu tính lại mỗi lần enrol. Khi chưa đủ bốn môn, app dùng average các môn hiện có để hiển thị kết quả hiện tại; không coi môn chưa enrol là điểm 0. Khi chưa có môn, average/overall grade là None. Quy tắc riêng cho sinh viên chưa đủ bốn môn không được đề mô tả thêm.

## Môi trường conda và dependencies

Môi trường đã tạo tại `D:\UniApp\.conda`: Python 3.12.16, Tk 8.6, pytest 8.3.5. App dùng thư viện chuẩn Python; pytest chỉ cần cho kiểm thử.

Chạy trên máy hiện tại trong PowerShell:

```powershell
Set-Location D:\UniApp
.\.conda\python.exe main.py
.\.conda\python.exe main.py --gui
```

Có thể activate nếu terminal đã khởi tạo conda:

```powershell
conda activate D:\UniApp\.conda
python main.py
```

Tạo môi trường trên máy thành viên khác, từ thư mục dự án:

```powershell
conda env create -f environment.yml
conda activate uniapp-group7
python main.py
```

Hoặc cài theo từng bước:

```powershell
conda create -n uniapp-group7 -c conda-forge python=3.12 pip tk -y
conda activate uniapp-group7
python -m pip install -r requirement.txt
```

Tkinter đến từ Python và package `tk` của conda; không cài bằng pip. `requirement.txt` dùng đúng tên file theo yêu cầu nhóm.

Nếu launcher `conda` trên máy hiện tại báo `The system cannot execute the specified program`, có thể dùng Python base để gọi module conda:

```powershell
& 'C:\Users\Admin\miniconda3\python.exe' -m conda env create -f environment.yml
```

## Chạy CLI theo sample I/O

Các prompt chính và mức thụt dòng được điều chỉnh theo ảnh sample trong đề:

```text
University System: (A)dmin, (S)tudent, or X :
    Student System (l/r/x):
        Student Course Menu (c/e/r/s/x):
    Admin System (c/g/p/r/s/x):
```

| Menu | Lựa chọn |
| --- | --- |
| University | `A` Admin, `S` Student, `X` thoát |
| Student | `l` login, `r` register, `x` trở về University |
| Student Course | `c` change password, `e` enrol, `r` remove, `s` show, `x` logout |
| Admin | `c` clear, `g` group, `p` partition, `r` remove by student ID, `s` show, `x` trở về University |

Lựa chọn chữ không phân biệt hoa/thường. Các alias số và `p` đổi mật khẩu cũ vẫn được nhận để giữ tương thích nhưng không hiển thị trong prompt chính.

Đăng ký theo thứ tự Email → Password → kiểm tra tồn tại → Name. Email/password sai định dạng được nhập lại trong cùng thao tác. Login đúng định dạng nhưng sai thông tin trở về Student menu. Xoá sinh viên thực hiện theo ID như sample. Clear yêu cầu `Y`; `N` hoặc input khác không xoá dữ liệu.

Ví dụ nhóm average: một sinh viên có các điểm 60, 65, 70, 78 có average 68.25, chỉ xuất hiện ở nhóm C và PASS. Không hiển thị thành bốn kết quả sinh viên riêng.

## Chạy GUI và bốn cửa sổ

```powershell
.\.conda\python.exe main.py --gui
```

**Chạy thử ngay sau khi giải nén ZIP:** dùng chế độ `--demo`. Ứng dụng tự tạo tài khoản email `preview@university.com`, password `Abcde123` trong file `demo.data` cạnh source và điền sẵn hai trường login:

```powershell
python main.py --gui --demo
```

Trên máy hiện tại có thể dùng `.\.conda\python.exe` thay cho `python`; trên máy khác activate conda env theo hướng dẫn phía trên. Bấm **Sign in** để đăng nhập demo, không cần đăng ký trước hoặc có sẵn file trong `tmp/`.

Để CLI dùng cùng tài khoản và dữ liệu demo, chạy `python main.py --demo`. Mỗi lần bật `--demo`, tài khoản demo được đảm bảo tồn tại và mật khẩu được đưa về `Abcde123`; các môn đã enrol và tài khoản khác trong file demo vẫn được giữ. Không dùng đồng thời `--demo` và `--data`.

Chế độ thường `python main.py --gui` vẫn đọc `students.data` và yêu cầu tài khoản đã đăng ký qua CLI. `--demo` dùng file riêng, không sửa dữ liệu này. Tài khoản `test@university.com` / `Abcde123` trong pytest chỉ nằm trong database tạm của từng test.

`environment.yml` có chú thích thông tin demo để dễ tra cứu, nhưng chức năng của file này là tạo môi trường conda. Ứng dụng đọc tài khoản từ file dữ liệu qua Database, không tự tạo tài khoản từ YAML.

Giao diện dùng nền sáng, sidebar xanh đậm và điểm nhấn xanh ngọc. `PortalTheme` quản lý màu/font/style chung; `PortalSidebar` hiển thị nhận diện và thông tin sinh viên. Vẫn dùng Tkinter/ttk chuẩn, không cần cài thêm thư viện giao diện. Các cửa sổ mới được đặt giữa màn hình; lỗi được đặt giữa cửa sổ đang thao tác.

1. **Login window:** form đăng nhập trong card, dùng nút **Sign in**; có **Show password** để hiện/ẩn mật khẩu. Logout sẽ xoá credentials và khôi phục chế độ ẩn mật khẩu. Tài khoản được đăng ký qua CLI.
2. **Enrolment window:** mở khi login thành công, có ba thẻ Enrolled, Average Mark, Overall Grade và thanh tiến độ. Sidebar hiển thị tên/ID; các nút Enrol, View subjects, Refresh overview và Log out dùng lại controller hiện có.
3. **Subject window:** bấm View subjects để mở Toplevel riêng với bảng Subject ID, Mark, Grade, các hàng xen màu và thông báo khi chưa có môn. **Back to overview** đóng cửa sổ này, giữ đăng nhập; có thể mở lại.
4. **Exception window:** Toplevel báo thiếu trường, email sai, credentials sai, lỗi dữ liệu hoặc enrol quá bốn môn. Bấm **Got it**, Enter hoặc Escape để quay lại thao tác.

Nút Enrol vẫn nhận lần bấm thứ năm để minh hoạ exception theo rubric; controller chặn thao tác và file không có môn thứ năm. Khi bảng môn đang mở, enrol/refresh cập nhật bảng từ dữ liệu mới nhất. Logout đóng các cửa sổ con và xoá nội dung credentials khỏi form.

Dùng database riêng khi demo (CLI/GUI phải trỏ cùng file):

```powershell
.\.conda\python.exe main.py --data tmp/demo.data
.\.conda\python.exe main.py --gui --data tmp/demo.data
```

Không có tài khoản demo được thêm vào dữ liệu thật. Database mặc định là `students.data` cạnh `database.py`, không phụ thuộc thư mục terminal hiện tại.

## Lưu trữ

Database vẫn lưu pickle Student objects để tương thích dữ liệu ban đầu. Mỗi thao tác đọc/ghi CRUD đi qua file. File chưa tồn tại sẽ được tạo; file rỗng/hỏng có lỗi rõ ràng và không bị âm thầm reset. Unpickler chỉ cho phép các model của app. Lưu một snapshot tạm thành công trước khi thay file chính để tránh file bị ghi dở.

Hai bản ghi ban đầu vẫn đọc được. SHA-256 của `students.data` trước/sau cập nhật giữ nguyên:

```text
7964a812c17692f88f12b8f982d0287359e91b3fe810b40d686bdc4ea2b076d2
```

App giữ định dạng password kế thừa trong file để không làm hỏng dữ liệu cũ. File snapshot chưa có transaction lock giữa nhiều tiến trình: chỉ nên để một tiến trình ghi tại một thời điểm; Refresh dùng để đọc lại thay đổi từ giao diện khác.

## Kiểm thử

```powershell
.\.conda\python.exe -m pytest -q --basetemp=tmp/pytest
```

Kết quả xác minh ngày **30/10/2026: 73 passed, 0 skipped**, trên Windows với conda env của dự án. Có kiểm thử Tkinter thật, ở chế độ cửa sổ ẩn. Các test GUI dùng một Tk root như vòng đời thật của ứng dụng, và tạo view/data riêng cho từng test.

`tmp/pytest` chỉ dành cho pytest; nội dung thư mục này có thể được pytest làm sạch khi chạy lại. Dùng đường dẫn này tránh hạn chế thư mục Temp của Windows sandbox. Trên máy headless không có display, test GUI có thể skip và cần chạy lại trên máy có GUI; lỗi cài Tcl/Tk không được coi như test đã đạt.

| File test | Các tình huống chính |
| --- | --- |
| `tests/test_accounts_enrolment.py` | Regex; đăng ký/login; trùng email/ID; enrol 4 môn; object cũ; unique subject ID; xoá đúng môn; biên grade; đổi password; lỗi lưu không sửa session |
| `tests/test_admin_storage_cli.py` | Grade/PASS/FAIL theo average; các biên chưa làm tròn; average sau enrol/drop/reopen; sinh viên chưa có môn; Y/N clear; xoá ID; confirmation/reuse password; tương thích pickle; file hỏng; lỗi atomic save; luồng CLI bằng stdin |
| `tests/test_gui.py` | Login sai; bốn đối tượng cửa sổ riêng; bảng môn; fifth-enrol exception; logout/login lại; mở lại bảng môn; refresh dữ liệu CLI; account bị admin xoá |
| `tests/test_demo.py` | Tạo tài khoản demo ở file mới; đăng nhập bằng credentials công bố; giữ enrolments khi mở lại; khôi phục password demo; không sửa tài khoản khác; điền sẵn GUI; từ chối option mâu thuẫn |

Các test dùng file tạm và không ghi vào database thật. Những test của bản trước Canvas đã được giữ bằng comment `##` và thay bằng kiểm tra đúng rubric; việc 58 test cũ pass không chứng minh đúng cách grouping theo đề chính thức.

## Checklist demo và đóng gói

1. Tạo tài khoản hợp lệ trong CLI; minh hoạ format sai và tài khoản trùng.
2. Login, show 0 môn, enrol 4 môn, thử lần 5, xoá đúng ID rồi enrol lại.
3. Dùng `c` đổi password; nhập confirmation lệch rồi đúng; logout và login bằng password mới.
4. Admin `s/g/p` hiển thị danh sách và kết quả theo average; thử ID không tồn tại; minh hoạ `c` với N rồi Y trên dữ liệu demo.
5. GUI login bằng tài khoản từ CLI; mở enrolment/subject window; thử lần enrol thứ năm để mở exception; kiểm tra dữ liệu sau logout/login.
6. Chạy test, đọc module mình phụ trách và chuẩn bị giải thích đóng góp thực tế.
7. Gộp CLI và GUI vào cùng project; theo đề, tên zip cho nhóm/lab này là `group7-Cmp108.zip`. Bao gồm source, test, README, environment và requirement; không kèm `.conda/`, `.conda-pkgs/`, `tmp/`, dữ liệu tài khoản thật hoặc cache. Nếu không kèm `students.data`, ứng dụng tự tạo file mới và cần đăng ký bằng CLI trước khi mở GUI.

Không có thao tác upload/nộp bài nào được thực hiện trong phiên làm việc này.
