function toggleVisibility() {
    var optionValue = document.getElementById("option").value;
    var fieldContainer = document.getElementById("fieldContainer");
    var fieldLabel = document.getElementById("fieldLabel");
    var fieldScan = document.getElementById("fieldScan");

    if (optionValue === "all") {
        fieldContainer.style.display = "none";
        fieldScan.style.display = "none";
        fieldLabel.style.display = "none";

    } else {
        fieldContainer.style.display = "block";

        if (optionValue === "employee") {
            fieldLabel.innerText = "Mã nhân viên:";
            fieldScan.style.display = "block";
            fieldLabel.style.display = "block";
        } else if (optionValue === "department") {
            fieldLabel.innerText = "Phòng ban:";
            fieldScan.style.display = "none";
            fieldLabel.style.display = "block";
        }
    }
}

function setDefaultDateTimeValues() {
    var now = new Date();
    var today = now.toISOString().slice(0, 10);
    var defaultStartTime = today ;
    var defaultEndTime = today ;

    document.getElementById("start_date").value = defaultStartTime;
    document.getElementById("end_date").value = defaultEndTime;
  }
  
setDefaultDateTimeValues();
toggleVisibility();