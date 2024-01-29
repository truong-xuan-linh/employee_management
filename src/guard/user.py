from flask_login import login_required, current_user

from flask import session as flask_session
from flask import render_template, request, redirect, url_for, Blueprint, jsonify
from pyzbar.pyzbar import decode
import io
import base64
import datetime
import calendar
from PIL import Image
import pandas as pd

from src.system.common import required_roles
from src.pccc.database import NhanVien
from src.on_leave.database import session, NghiPhep, func, and_, desc, or_, extract
from src.guard.database import RaVao

from src.system.common import send_email


guard = Blueprint("guard", __name__)

@guard.route('/qr-scan', methods=['GET', 'POST'])
@required_roles("guard", "head_guard")
def qr_scan():
    guard_type = request.args.get('guard_type')
    print("guard_type: ", guard_type)
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
            
            if guard_type == "frequently":
                return jsonify(status="Thành công", redirect_url=f"/guard/v2/infomation?manv={nhanvien.MaNV}")
            else:
                return jsonify(status="Thành công", redirect_url=f"/guard/infomation?manv={nhanvien.MaNV}")

        else:
            return jsonify(status="Không tìm thấy QR code")
    
    return render_template('guard/qr-scan.html')

@guard.route("/infomation", methods=['GET', 'POST'])
@required_roles("guard", "head_guard")
def infomation():
    manv = request.args.get("manv", "")
    employee =  session.query(NhanVien) \
                        .filter_by(MaNV=manv) \
                        .first()
                        
    if not employee:
        return "Nhân viên không có"
    
    
    current_time = datetime.datetime.now()
    on_leaves_infomation =  session.query(NghiPhep) \
                        .filter_by(MaNV=manv) \
                        .filter(extract('day', NghiPhep.GioRa) == current_time.day,
                                extract('month', NghiPhep.GioRa) == current_time.month,
                                extract('year', NghiPhep.GioRa) == current_time.year) \
                        .order_by(NghiPhep.ThoiGian).all()
    
    on_leave_time = ""
    for inf in on_leaves_infomation:
        on_leave_time += f'Từ: {inf.GioRa.hour}h{inf.GioRa.minute} đến: {inf.GioVao.hour}h{inf.GioVao.minute}, '
        
    if not on_leave_time:
        on_leave_time = "Chưa có"
        
    if request.method == "POST":
       
        if request.form.get("button-yes", False) == "yes":
            
            on_leave = session.query(NghiPhep) \
                        .filter_by(MaNV=manv) \
                        .filter(or_(NghiPhep.GioRaThucTe == None, NghiPhep.GioVaoThucTe == None), 
                                    NghiPhep.NghiGay==1,
                                    extract('day', NghiPhep.GioRa) == current_time.day) \
                        .order_by(NghiPhep.GioRa).first()
            
            if on_leave:
                if not on_leave.GioRaThucTe:
                    on_leave.GioRaThucTe = current_time
                else:
                    on_leave.GioVaoThucTe = current_time
                session.commit()
            
            return redirect(url_for('guard.qr_scan', guard_type="on-leave"))
        
    return render_template("guard/infomation.html", employee=employee, on_leave_time=on_leave_time)

@guard.route("/v2/infomation", methods=['GET', 'POST'])
@required_roles("head_guard", "guard")
def v2_infomation():
    manv = request.args.get("manv", "")
    employee =  session.query(NhanVien) \
                        .filter_by(MaNV=manv) \
                        .first()
                        
    if not employee:
        return "Nhân viên không có"
    
    is_out = True
    on_leave = session.query(RaVao) \
                    .filter_by(MaNV=manv) \
                    .order_by(desc(RaVao.ThoiGian)).first()

    if on_leave:
        print("on_leave")
        if not on_leave.GioVaoThucTe:
            is_out = False
            
    current_time = datetime.datetime.now()
        
    if request.method == "POST":
       
        if request.form.get("button-yes", False) == "yes":
            print(request.form.get("filter_type"))
            is_out = True if request.form.get("filter_type") == "out" else False
            if not is_out:
                on_leave.GioVaoThucTe = current_time
            else:
                
                on_leave = RaVao(MaNV=employee.MaNV,
                                HoTen=employee.HoTen,
                                BoPhan=employee.BoPhan,
                                PhongBan=employee.PhongBan,
                                GioVaoThucTe=None,
                                GioRaThucTe=current_time,
                                ThoiGian=current_time)
                session.add(on_leave)
                
            session.commit()
            
            return redirect(url_for('guard.qr_scan', guard_type="frequently"))
        
    return render_template("guard/infomation_v2.html", employee=employee, is_out=is_out)

@guard.route("/report", methods=['GET', 'POST'])
@required_roles("head_guard")
def report():
            
    current_time = datetime.datetime.now()
    
    _, day_end = calendar.monthrange(current_time.year, current_time.month)
    day_start = 1
    start = datetime.date(current_time.year, current_time.month, day_start)
    end = datetime.date(current_time.year, current_time.month, day_end)
    email_list = [""]
    
    if request.method == "POST":
       
        if request.form.get("button-yes", False) == "yes":
            start = request.form.get("start")
            end = request.form.get("end")
            email_list = request.form.getlist('email')
            
            start = datetime.datetime.strptime(start, "%Y-%m-%d").replace(hour=0, minute=0, second=0)
            end = datetime.datetime.strptime(end, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            
            leave_infomations = session.query(RaVao) \
                    .filter(RaVao.ThoiGian >= start, RaVao.ThoiGian <= end) \
                    .order_by(RaVao.HoTen).all()
            data = [{"MaNV": rv.MaNV , 
                     "HoTen": rv.HoTen, 
                     "BoPhan": rv.BoPhan, 
                     "PhongBan": rv.PhongBan, 
                     "GioVaoThucTe": rv.GioVaoThucTe.strftime("%H:%M:%S %d-%m-%Y") if rv.GioVaoThucTe else None, 
                     "GioRaThucTe": rv.GioRaThucTe.strftime("%H:%M:%S %d-%m-%Y") if rv.GioRaThucTe else None} for rv in leave_infomations]
            
            df = pd.DataFrame(data)
            df.to_excel("./instance/bao_cao_ra_vao.xlsx")
            
            header = f"[Báo cáo nghỉ phép] ngày {current_time.date()}"
            #Send email
            for email in email_list:
                if not email:
                    continue
                print(f"SEND MAIL TO {email}")
                send_email(email, header=header, content="", attachfile_dir="instance/bao_cao_ra_vao.xlsx")
            
            # return redirect(url_for('guard.qr_scan', guard_type="frequently"))
        
    return render_template("guard/report.html", start=start, end=end, email_list=email_list)

@guard.route("/directional", methods=['GET'])
@required_roles("guard", "head_guard")
def options():
    if "guard" in flask_session["role"]:
        print(flask_session["role"])
        return redirect(url_for('guard.qr_scan', guard_type="frequently"))
    
    return render_template("guard/directional.html", name=current_user.HoTen)