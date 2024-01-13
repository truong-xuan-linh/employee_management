from flask_login import login_required
from flask import session as flask_session
from flask import render_template, request, redirect, url_for, Blueprint, jsonify
from pyzbar.pyzbar import decode
import io
import base64
import datetime
from PIL import Image

from src.system.common import required_roles
from src.pccc.database import NhanVien
from src.on_leave.database import session, NghiPhep, func, and_, desc, or_, extract
from src.system.common import send_email


guard = Blueprint("guard", __name__)

@guard.route('/qr-scan', methods=['GET', 'POST'])
@required_roles("guard")
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
                    
            return jsonify(status="Thành công", redirect_url=f"/guard/infomation?manv={nhanvien.MaNV}")

        else:
            return jsonify(status="Không tìm thấy QR code")

    
    return render_template('guard/qr-scan.html')

@guard.route("/infomation", methods=['GET', 'POST'])
@required_roles("guard")
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
            
            return redirect(url_for('guard.qr_scan'))
        
    return render_template("guard/infomation.html", employee=employee, on_leave_time=on_leave_time)