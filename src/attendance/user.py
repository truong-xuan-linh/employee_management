from flask import session as flask_session
from flask import render_template, request, redirect, url_for, Blueprint, jsonify

import io
import base64
import datetime
from PIL import Image
from pyzbar.pyzbar import decode

from src.pccc.database import NhanVien
from src.attendance.database import session, DiemDanh, KetQuaDiemDanh, func, and_, desc

from src.system.common import send_email
from src.system.common import required_roles

attendance = Blueprint("attendance", __name__)


@attendance.route('/qr-scan', methods=['GET', 'POST'])
@required_roles("user")
def qr_scan():
    if request.method == 'POST':
        # Get image from font-end and convert to RGB image
        image_data = request.json.get('image')

        img = Image.open(io.BytesIO(base64.b64decode(image_data.split(',')[1]))).convert("RGB")

        # Use pyzbar to detect QR codes
        decoded_objects = decode(img)

        # Check if QR codes are detected
        if decoded_objects:
            # Get the first detected QR code value
            value = decoded_objects[0].data.decode('utf-8')
            current_time = datetime.datetime.now()
            
            nhanvien = session.query(NhanVien).filter_by(MaNV=value).first()
            if not nhanvien:
                return jsonify(status="Không tìm thấy nhân viên")

            if not nhanvien.BoPhan == flask_session["bophan"]:
                return jsonify(status=f"Nhân viên {nhanvien.HoTen} không thuộc bộ phận {flask_session['bophan']}")

            check = session.query(DiemDanh).filter(and_(func.date(DiemDanh.ThoiGian) == current_time.date(), DiemDanh.MaNV == nhanvien.MaNV)).first()
            if check:
                return jsonify(status=f"{nhanvien.HoTen} đã được điểm danh trước đó")
            # Insert DB if QR code value is valid
            
            diemdanh = DiemDanh(MaNV=nhanvien.MaNV, HoTen=nhanvien.HoTen, BoPhan=nhanvien.BoPhan,
                              PhongBan=nhanvien.PhongBan, ThoiGian=current_time)
            
            session.add(diemdanh)
            session.commit()
                    
            return jsonify(status=f"Điểm danh {nhanvien.HoTen} thành công")

        else:
            return jsonify(status="Không tìm thấy QR code")

    employees = session.query(NhanVien).filter(NhanVien.MaNV.notin_(session.query(DiemDanh.MaNV))).filter_by(
        BoPhan=flask_session["bophan"]).all()
    
    return render_template('attendance/qr-scan.html', employees=employees)

@attendance.route("/qr-result", methods=['GET', 'POST'])
@required_roles("user")
def qr_result():
    
    email_check =  session.query(KetQuaDiemDanh) \
                        .filter_by(BoPhan=flask_session["bophan"]) \
                        .order_by(desc(KetQuaDiemDanh.ThoiGian)).first()
    if email_check:
        email_list = email_check.Mail.split(", ")
    else:
        email_list = [""]
        
    if request.method == "POST":

       
        if request.form.get("button-yes", False) == "yes":
            email_list = request.form.getlist('email')
            
            current_time = datetime.datetime.now()
            ketqua_check = session.query(KetQuaDiemDanh) \
                        .filter(and_(func.date(KetQuaDiemDanh.ThoiGian) == current_time.date(), KetQuaDiemDanh.BoPhan==flask_session["bophan"])).first()

            flask_session["hoanthanh"] = True
            employee_absent = session.query(NhanVien) \
                                    .filter(NhanVien.MaNV.notin_(session.query(DiemDanh.MaNV).filter(func.date(DiemDanh.ThoiGian) == current_time.date()))) \
                                    .filter_by(BoPhan=flask_session["bophan"]) \
                                    .all()
            employee_absent = [employee.HoTen for employee in employee_absent]
            
            employee_present =  session.query(DiemDanh).filter(and_(func.date(DiemDanh.ThoiGian) == current_time.date(), DiemDanh.BoPhan==flask_session["bophan"])).all()            
            employee_present = [employee.HoTen for employee in employee_present]
            
            if ketqua_check:
                ketqua_check.SoLuongVang = len(employee_absent)
                ketqua_check.SoLuongCoMat = len(employee_present)
                ketqua_check.Mail = ", ".join(email_list)
                session.commit()
                header = f"[UPDATE][{flask_session['bophan']}] Báo cáo điểm danh nhân viên ngày {current_time.date()}"
            else:
                
                ketqua = KetQuaDiemDanh(BoPhan=flask_session["bophan"], 
                                ThoiGian=current_time,
                                SoLuongVang=len(employee_absent),
                                SoLuongCoMat=len(employee_present),
                                Mail = ", ".join(email_list))
                
                session.add(ketqua)
                session.commit()
                header = f"[{flask_session['bophan']}] Báo cáo điểm danh nhân viên ngày {current_time.date()}"
                        
            content = f'''
            Thời gian: {current_time.date()},
            Bộ phận: {flask_session['bophan']},
            Nhân viên có mặt: {", ".join(employee_present)},
            Số lượng có mặt: {len(employee_present)},
            Nhân viên vắng mặt: {", ".join(employee_absent)},
            Số lượng vắng mặt: {len(employee_absent)},
                
            '''
            for email in email_list:
                send_email(email, header=header, content=content)
            
            return redirect(url_for('directional.options'))
        
    return render_template("attendance/qr-result.html", email_list = email_list)