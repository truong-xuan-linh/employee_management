function toggleContent(elementId) {
    var element = document.getElementById(elementId);
    var showBtn = element.nextElementSibling;
    var lessBtn = showBtn.nextElementSibling;
  
    if (element.style.display === 'none' || element.style.display === '') {
        element.style.display = 'inline';
        showBtn.style.display = 'none';
        lessBtn.style.display = 'inline';
    } else {
        element.style.display = 'none';
        showBtn.style.display = 'inline';
        lessBtn.style.display = 'none';
    }
}
