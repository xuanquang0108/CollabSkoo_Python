
const dropArea = document.getElementById('dropArea');
const fileInput = document.getElementById('fileInput');
const filePreview = document.getElementById('filePreview');

// Ngăn hành động mặc định cho toàn trang
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
  window.addEventListener(eventName, (e) => {
    e.preventDefault();
    e.stopPropagation();
  }, false);
});

// Ngăn hành động mặc định cho vùng dropArea
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
  dropArea.addEventListener(eventName, (e) => {
    e.preventDefault();
    e.stopPropagation();
  }, false);
});

// Highlight khi kéo vào
['dragenter', 'dragover'].forEach(eventName => {
  dropArea.addEventListener(eventName, () => {
    dropArea.classList.add('dragover');
  }, false);
});

// Bỏ highlight khi kéo ra
['dragleave', 'drop'].forEach(eventName => {
  dropArea.addEventListener(eventName, () => {
    dropArea.classList.remove('dragover');
  }, false);
});

// Khi thả file
dropArea.addEventListener('drop', (e) => {
  if (e.dataTransfer.files.length > 0) {
    fileInput.files = e.dataTransfer.files;
    updateFilePreview();
  }
});

// Khi click chọn file
fileInput.addEventListener('change', () => {
  updateFilePreview();
});

// Hiển thị tên file
function updateFilePreview() {
  if (fileInput.files.length > 0) {
    const file = fileInput.files[0];
    filePreview.innerHTML = `Đã chọn: <strong>${file.name}</strong> (${(file.size / 1024).toFixed(1)} KB)`;
  } else {
    filePreview.innerHTML = '';
  }
}