function addEmailField() {
    var container = document.getElementById('infomationContainer');
    var newRow = document.createElement('div');
    newRow.classList.add('row');
    newRow.innerHTML = `
        <label>Email:</label>
        <input type="email" name="email" required>
        <button type="button" onclick="removeEmailField(this)">-</button>
    `;
    container.appendChild(newRow);
}

function removeEmailField(button) {
    var container = document.getElementById('infomationContainer');
    var rowToRemove = button.parentNode;
    container.removeChild(rowToRemove);
}