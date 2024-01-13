document.addEventListener('DOMContentLoaded', function() {
    var form = document.querySelector('form');
    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Ngăn chặn việc submit form mặc định

        // Lấy giá trị từ form
        var employee = document.querySelector('#employee').value;
        var start = document.querySelector('input[name="start"]').value;
        var end = document.querySelector('input[name="end"]').value;

        // Tạo đối tượng dữ liệu để gửi đi
        var data = {
            employee: employee,
            start: start,
            end: end
        };

        // Gửi yêu cầu POST đến API
        fetch('/on-leave/infomation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            // Xử lý dữ liệu trả về và điền vào bảng
            var tableBody = document.querySelector('tbody');
            tableBody.innerHTML = ''; // Xóa dữ liệu cũ trước khi thêm mới

            data.on_leaves.forEach(function(leave) {
                var row = document.createElement('tr');
                row.innerHTML = '<td>' + leave.GioRa + '</td>' +
                                '<td>' + leave.GioVao + '</td>' +
                                '<td>' + leave.GioRaThucTe + '</td>' +
                                '<td>' + leave.GioVaoThucTe + '</td>';
                tableBody.appendChild(row);
            });
        })
        .catch(error => console.error('Error:', error));
    });
});
