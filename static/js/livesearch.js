document.addEventListener('DOMContentLoaded', function() {
  const input = document.getElementById('search-input');
  if (!input) {
    console.error('Không tìm thấy search-input');
    return;
  }

  const suggestionBox = document.getElementById('suggestions');
  if (!suggestionBox) {
    console.error('Không tìm thấy suggestions box');
    return;
  }

  let documents = [];

  // Fetch dữ liệu
  fetch('/all-documents')
    .then(res => {
      if (!res.ok) {
        throw new Error('Lỗi khi fetch /all-documents: ' + res.status);
      }
      return res.json();
    })
    .then(data => {
      documents = data.documents || [];
      console.log('Dữ liệu documents:', documents.slice(0, 5)); // Debug 5 tài liệu đầu
    })
    .catch(err => {
      console.error('Lỗi fetch dữ liệu:', err);
    });

  input.addEventListener('input', function() {
    const query = this.value.toLowerCase();
    suggestionBox.innerHTML = '';

    if (!query) {
      suggestionBox.style.display = 'none';
      return;
    }

    const filtered = documents.filter(doc =>
      doc.title && doc.title.toLowerCase().includes(query)
    );

    if (filtered.length > 0) {
      filtered.forEach(doc => {
        const li = document.createElement('li');
        li.onclick = () => {
          window.location.href = `/documents/${doc.id}`;
        };

        const img = document.createElement('img');
        // Kiểm tra thumbnail chặt chẽ
        const thumbnailPath = (doc.thumbnail && doc.thumbnail.trim() && doc.thumbnail !== 'null')
          ? doc.thumbnail.startsWith('static/')
            ? `/${doc.thumbnail}`
            : `/static/thumbnails/${doc.thumbnail}`
          : '/static/thumbnails/default_thumb.png';
        img.src = thumbnailPath;
        img.alt = doc.title || 'Thumbnail';
        img.style.width = '40px';
        img.style.height = '40px';
        img.style.objectFit = 'cover';
        img.style.marginRight = '10px';
        img.onerror = () => {
          if (img.src !== '/static/thumbnails/default_thumb.png') {
            console.warn(`Không load được ảnh: ${img.src}, chuyển sang default`);
            img.src = '/static/thumbnails/default_thumb.png';
          } else {
            console.error('Ảnh mặc định không tồn tại: /static/thumbnails/default_thumb.png');
          }
        };

        const span = document.createElement('span');
        span.textContent = doc.title || 'Không có tiêu đề';

        li.appendChild(img);
        li.appendChild(span);
        suggestionBox.appendChild(li);
      });

      suggestionBox.style.display = 'block';
    } else {
      suggestionBox.style.display = 'none';
    }
  });
});