from email import encoders
from email.mime.base import MIMEBase
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.header import Header
import datetime
import os


def custom_df(df, header):
    temp_df = pd.DataFrame([df.columns], columns=df.columns)
    df = pd.concat([temp_df, df])
    df = df.set_axis(header, axis=1)
    return df


def create_excel_file(results, new_history, staff_absent_df, filename):
    # Convert new_history to DataFrame
    new_history_df = pd.DataFrame(new_history, index=[0])
    new_history_df.columns = ["Mốc thời gian", "Kết quả", "Lý do", "Thời gian diễn ra thực tế",
                              "Tổng số có mặt trong ngày", "Có mặt tại nơi tập trung", "Vắng mặt"]

    new_history_header = ["CÔNG TY CP DỆT MAY 29/3 \nĐỘI PCCC",
                          "BÁO CÁO TỔNG HỢP \nĐIỂM DANH QUÂN SỐ CÓ MẶT TẠI NƠI TẬP TRUNG",
                          "HCB-CSR-THTN/BM1 \nLần soát xét : 01/00 \nNgày hiệu lực: 30/12/2023 \nNgười soạn thảo: Phòng Tổng hợp",
                          "", "", "", ""
                          ]
    new_history_df = custom_df(new_history_df, new_history_header)

    # Create a DataFrame for detailed results
    detailed_results = []
    for department, result in results.items():
        detailed_results.append({
            'Mốc thời gian': result['last_time'],
            'Xí nghiệp/Phòng ban': department,
            'Tổ/Bộ phận': department,
            'Tổng số có mặt trong ngày': result['total'],
            'Có mặt tại nơi tập trung': result['num_done'],
            'Vắng mặt': result['total'] - result['num_done'],
        })
    detailed_results_df = pd.DataFrame(detailed_results)
    detailed_results_header = ["CÔNG TY CP DỆT MAY 29/3 \nĐỘI PCCC",
                               "BÁO CÁO CHI TIẾT \nĐIỂM DANH QUÂN SỐ CÓ MẶT TẠI NƠI TẬP TRUNG",
                               "HCB-CSR-THTN/BM1 \nLần soát xét : 01/00 \nNgày hiệu lực: 30/12/2023 \nNgười soạn thảo: Phòng Tổng hợp",
                               "", "", ""]
    detailed_results_df = custom_df(detailed_results_df, detailed_results_header)

    # Create a DataFrame for absent staff
    absent_staff = []
    for idx in range(staff_absent_df.__len__()):
        row = staff_absent_df.iloc[idx]
        absent_staff.append({
            'Tổ/Bộ phận': row.BoPhan,
            'Xí nghiệp/Phòng ban': row.PhongBan,
            'Họ Tên': row.HoTen,
            "Mã số": row.MaNV
        })
    absent_staff_df = pd.DataFrame(absent_staff, columns=['Tổ/Bộ phận', 'Xí nghiệp/Phòng ban', 'Họ Tên', 'Mã số'])
    absent_staff_df = pd.DataFrame(absent_staff_df)
    absent_staff_header = ["CÔNG TY CP DỆT MAY 29/3 \nĐỘI PCCC",
                           "DANH SÁCH VẮNG MẶT TẠI NƠI TẬP TRUNG",
                           "HCB-CSR-THTN/BM1 \nLần soát xét : 01/00 \nNgày hiệu lực: 30/12/2023 \nNgười soạn thảo: Phòng Tổng hợp",
                           ""
                           ]
    absent_staff_df = custom_df(absent_staff_df, absent_staff_header)

    # Get the directory name
    dir_name = "Báo cáo diễn tập"  # replace with your directory

    # Create the directory if it does not exist
    os.makedirs(dir_name, exist_ok=True)

    # Replace invalid characters in filename
    filename = filename.replace("/", "_").replace("\\", "_")

    # Create the full file path
    filename = os.path.join(dir_name, filename)

    # Write to Excel file
    with pd.ExcelWriter(filename) as writer:
        new_history_df.to_excel(writer, sheet_name='Kết quả diễn tập', index=False)
        detailed_results_df.to_excel(writer, sheet_name='Chi tiết', index=False)
        absent_staff_df.to_excel(writer, sheet_name='Danh sách vắng', index=False)
    print(f"File {filename} has been created.")

def create_excel_file_v2(results, new_history, filename):
    # Convert new_history to DataFrame
    new_history_df = pd.DataFrame(new_history, index=[0])
    new_history_df.columns = ["Mốc thời gian", "Kết quả", "Lý do", "Thời gian diễn ra thực tế",
                              "Tổng số có mặt trong ngày", "Có mặt tại nơi tập trung", "Vắng mặt"]

    new_history_header = ["CÔNG TY CP DỆT MAY 29/3 \nĐỘI PCCC",
                          "BÁO CÁO TỔNG HỢP \nĐIỂM DANH QUÂN SỐ CÓ MẶT TẠI NƠI TẬP TRUNG",
                          "HCB-CSR-THTN/BM1 \nLần soát xét : 01/00 \nNgày hiệu lực: 30/12/2023 \nNgười soạn thảo: Phòng Tổng hợp",
                          "", "", "", ""
                          ]
    new_history_df = custom_df(new_history_df, new_history_header)

    # Create a DataFrame for detailed results
    detailed_results = []
    for department, result in results.items():
        detailed_results.append({
            'Mốc thời gian': result['last_time'],
            'Xí nghiệp/Phòng ban': department,
            'Tổ/Bộ phận': department,
            'Tổng số có mặt trong ngày': result['total'],
            'Có mặt tại nơi tập trung': result['num_done'],
            'Vắng mặt': result['total'] - result['num_done'],
        })
    detailed_results_df = pd.DataFrame(detailed_results)
    detailed_results_header = ["CÔNG TY CP DỆT MAY 29/3 \nĐỘI PCCC",
                               "BÁO CÁO CHI TIẾT \nĐIỂM DANH QUÂN SỐ CÓ MẶT TẠI NƠI TẬP TRUNG",
                               "HCB-CSR-THTN/BM1 \nLần soát xét : 01/00 \nNgày hiệu lực: 30/12/2023 \nNgười soạn thảo: Phòng Tổng hợp",
                               "", "", ""]
    detailed_results_df = custom_df(detailed_results_df, detailed_results_header)


    # Get the directory name
    dir_name = "Báo cáo diễn tập"  # replace with your directory

    # Create the directory if it does not exist
    os.makedirs(dir_name, exist_ok=True)

    # Replace invalid characters in filename
    filename = filename.replace("/", "_").replace("\\", "_")

    # Create the full file path
    filename = os.path.join(dir_name, filename)

    # Write to Excel file
    with pd.ExcelWriter(filename) as writer:
        new_history_df.to_excel(writer, sheet_name='Kết quả diễn tập', index=False)
        detailed_results_df.to_excel(writer, sheet_name='Chi tiết', index=False)
    print(f"File {filename} has been created.")

def send_email_with_attachment(recipient, filename, new_history):
    # Set up the SMTP server
    s = smtplib.SMTP_SSL(host='mail.hachiba.com.vn', port=465)
    s.login('vuthanh.hoa@hachiba.com.vn', 'Ho*!!811th')

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = 'vuthanh.hoa@hachiba.com.vn'
    msg['To'] = recipient

    # Format the date
    date = datetime.datetime.strptime(new_history['MocThoiGian'], "%d/%m/%Y - %H:%M").date()
    msg['Subject'] = Header(f"Báo cáo kết quả diễn tập PCCC ngày {date.strftime('%d-%m-%Y')}", 'utf-8')

    # Get the directory name
    dir_name = "Báo cáo diễn tập"  # replace with your directory

    # Create the full file path
    filename = os.path.join(dir_name, filename)

    # Add the attachment
    part = MIMEBase('application', 'vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    with open(filename, 'rb') as file:
        part.set_payload(file.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(filename)}')
    msg.attach(part)

    # Send the email
    s.send_message(msg)
    s.quit()