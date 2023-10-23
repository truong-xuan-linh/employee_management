from flask_login import login_required
from flask import session as flask_session
from flask import render_template, request, flash, redirect, url_for, session, Blueprint, jsonify

import io 
import cv2
import base64
import datetime
import numpy as np
from PIL import Image

from src.pccc.database import session, NhanVien, TapHuan, KetQua

user = Blueprint("user", __name__)

@user.route('/qr-scan', methods=['GET', 'POST'])
@login_required
def qr_scan():
    if request.method == 'POST':
        
        # Get image from font-end and convert to RGB image
        image_data = request.json.get('image')
        
        img = Image.open(io.BytesIO(base64.b64decode(image_data.split(',')[1]))).convert("RGB")
        
        #Init QR detector
        detector = cv2.QRCodeDetector()
        
        #Get QR value from image
        value, _, _ = detector.detectAndDecode(np.array(img)[:,:,::-1])
        
        if value:
            nhanvien = session.query(NhanVien).filter_by(MaNV=value).first()
            if not nhanvien:
                return jsonify(status = "Không tìm thấy nhân viên") #jsonify({'redirect_url': "/user/qr-result?content=Không tìm thấy nhân viên"})
            
            if not nhanvien.BoPhan == flask_session["bophan"]:
                return jsonify(status=f"Nhân viên {nhanvien.HoTen} không thuộc bộ phận {flask_session['bophan']}") #return jsonify({'redirect_url': f"/user/qr-result?content=Nhân viên {nhanvien.HoTen} không thuộc bộ phận {flask_session['bophan']}"})
            
            check = session.query(TapHuan).filter_by(MaNV=nhanvien.MaNV).first()
            if check:
                return jsonify(status=f"{nhanvien.HoTen} đã được điểm danh trước đó") #return jsonify({'redirect_url': f"/user/qr-result?content={nhanvien.HoTen} đã được điểm danh trước đó"})
            
            # Insert DB if QR code value is valid
            current_time = datetime.datetime.now() 
            taphuan = TapHuan(MaNV=nhanvien.MaNV, HoTen=nhanvien.HoTen, BoPhan=nhanvien.BoPhan, PhongBan=nhanvien.PhongBan, ThoiGian=current_time)
            session.add(taphuan)
            session.commit()
            
            # After submit, if user still continue scan qr code then delete department in KetQua database
            if flask_session.get("hoanthanh", False) == True:
                ketqua_check = session.query(KetQua).filter_by(BoPhan=flask_session["bophan"])
                if ketqua_check:
                    ketqua_check.delete()
                    session.commit()
            return jsonify(status=f"Điểm danh {nhanvien.HoTen} thành công") #return jsonify({'redirect_url': f"/user/qr-result?content=Điểm danh {nhanvien.HoTen} thành công"})
            
        else:
            return jsonify(status="Không tìm thấy QR code")
            
    return render_template('qr-scan.html')


@user.route("/qr-result", methods=['GET', 'POST'])
@login_required
def qr_result():
    if request.method == "POST":
        
        # If user confirm submission then update department in KetQua database is Done
        if request.form.get("button-yes", False) == "yes":
            flask_session["hoanthanh"] = True
            ketqua_check = session.query(KetQua).filter_by(BoPhan=flask_session["bophan"]).first()
            
            if ketqua_check:
                ketqua_check.HoanThanh = True
                session.commit()
                
            else:
                current_time = datetime.datetime.now()
                ketqua = KetQua(BoPhan=flask_session["bophan"], HoanThanh=True, ThoiGian=current_time)
                session.add(ketqua)
                session.commit()
                
            return redirect(url_for('login'))
        
        elif request.form.get("button-back", False) == "yes":
            return redirect(url_for('user.qr_scan'))
        
    return render_template("qr-result.html")
    