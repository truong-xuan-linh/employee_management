from flask_login import login_required
from flask import session as flask_session
from flask import render_template, request, redirect, url_for, session, Blueprint, jsonify
from pyzbar.pyzbar import decode
import io
import base64
import datetime
from PIL import Image

from src.pccc.database import session, NhanVien, DienTap, KetQua, DienTap2
from src.system.common import required_roles

user = Blueprint("user", __name__)


@user.route('/qr-scan', methods=['GET', 'POST'])
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

            check = session.query(DienTap).filter_by(MaNV=nhanvien.MaNV).first()
            if check:
                return jsonify(status=f"{nhanvien.HoTen} đã được điểm danh trước đó")
            # Insert DB if QR code value is valid
            current_time = datetime.datetime.now()
            taphuan = DienTap(MaNV=nhanvien.MaNV, HoTen=nhanvien.HoTen, BoPhan=nhanvien.BoPhan,
                              PhongBan=nhanvien.PhongBan, ThoiGian=current_time)
            session.add(taphuan)
            session.commit()

            # After submit, if user still continue scan qr code then delete department in KetQua database
            if flask_session.get("hoanthanh", False) == True:
                ketqua_check = session.query(KetQua).filter_by(BoPhan=flask_session["bophan"])
                if ketqua_check:
                    ketqua_check.delete()
                    session.commit()
            return jsonify(status=f"Điểm danh {nhanvien.HoTen} thành công")

        else:
            return jsonify(status="Không tìm thấy QR code")

    employees = session.query(NhanVien).filter(NhanVien.MaNV.notin_(session.query(DienTap.MaNV))).filter_by(
        BoPhan=flask_session["bophan"]).all()
    return render_template('pccc/qr-scan.html', status="Hãy nhập gì đi", employees=employees)


@user.route("/qr-result", methods=['GET', 'POST'])
@required_roles("user")
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

    return render_template("pccc/qr-result.html")

@user.route("/form", methods=['GET', 'POST'])
@required_roles("user")
def form_infomation():
    
    bophan = flask_session["bophan"]
    phongban = flask_session["phongban"]
    
    if request.method == "POST":
        if request.form.get("button-yes", False) == "yes":

            present = int(request.form.get("present"))
            current_time = datetime.datetime.now()
            
            taphuan = DienTap2(BoPhan=bophan, PhongBan=phongban, SoLuongCoMat=present, ThoiGian=current_time)
            session.add(taphuan)
            session.commit()
            

            return redirect(url_for('directional.options'))
        
    return render_template("pccc/form.html", bophan=bophan, phongban=phongban)