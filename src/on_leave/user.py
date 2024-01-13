from flask_login import login_required
from flask import session as flask_session
from flask import render_template, request, redirect, url_for, Blueprint, jsonify
from pyzbar.pyzbar import decode
import io
import base64
import datetime
from PIL import Image

from src.pccc.database import NhanVien
from src.on_leave.database import session, NghiPhep, func, and_, desc
from src.system.common import send_email
from src.system.common import required_roles

on_leave = Blueprint("on-leave", __name__)

@on_leave.route('/qr-scan', methods=['GET', 'POST'])
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
            
            nhanvien = session.query(NhanVien).filter_by(MaNV=value).first()

            if not nhanvien:
                return jsonify(status="Không tìm thấy nhân viên")

            if not nhanvien.BoPhan == flask_session["bophan"]:
                return jsonify(status=f"Nhân viên {nhanvien.HoTen} không thuộc bộ phận {flask_session['bophan']}")
                    
            return jsonify(status="Thành công", redirect_url=f"/on-leave/infomation?manv={nhanvien.MaNV}")

        else:
            return jsonify(status="Không tìm thấy QR code")

    
    return render_template('on_leave/qr-scan.html')

@on_leave.route("/infomation", methods=['GET', 'POST'])
@required_roles("user")
def infomation():
    manv = request.args.get("manv", "")
    employee =  session.query(NhanVien) \
                        .filter_by(MaNV=manv) \
                        .first()
                        
    if not employee:
        return "Nhân viên không có"
    
    #Get lastest email
    email_check =  session.query(NghiPhep) \
                        .filter_by(BoPhan=employee.BoPhan) \
                        .order_by(NghiPhep.ThoiGian).first()
    if email_check:
        email_list = email_check.Mail.split(", ")
    else:
        email_list = [""]

    if request.method == "POST":
       
        if request.form.get("button-yes", False) == "yes":
            email_list = request.form.getlist('email')
            time_in = datetime.datetime.strptime(request.form.get("in"), "%Y-%m-%dT%H:%M")
            time_out = datetime.datetime.strptime(request.form.get("out"), "%Y-%m-%dT%H:%M")
            on_leave_type = request.form.get("type") == "on"
            current_time = datetime.datetime.now()
                
            nghiphep = NghiPhep(MaNV = employee.MaNV, 
                                HoTen = employee.HoTen, 
                                BoPhan = employee.BoPhan, 
                                PhongBan = employee.PhongBan, 
                                GioVao = time_in, 
                                GioRa = time_out, 
                                ThoiGian = current_time, 
                                NghiGay = on_leave_type, 
                                Mail = ", ".join(email_list))
            
            session.add(nghiphep)
            session.commit()
            header = f"[{employee.HoTen}] Xin nghỉ phép từ {time_in} đến {time_out}"
            
            content = f'''
            Mã nhân viên: {employee.MaNV}
            Họ tên: {employee.HoTen}
            Bộ phận: {employee.BoPhan}
            Phòng ban: {employee.PhongBan}
            Xin nghỉ từ: {time_in} đến: {time_out}
            '''
            
            #Send email
            for email in email_list:
                if not email:
                    continue
                send_email(email, header=header, content=content)
            
            return redirect(url_for('directional.options'))
        
    return render_template("on_leave/infomation.html", employee=employee, email_list=email_list)