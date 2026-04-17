/**
 * HomeEat 公共JS工具
 */

// 文件上传
function uploadFile(inputId, callback) {
    const input = document.getElementById(inputId);
    const file = input.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    fetch('/upload', { method: 'POST', body: formData })
        .then(r => r.json())
        .then(data => {
            if (data.code === 0) {
                callback(data.data.url);
            } else {
                alert(data.msg);
            }
        })
        .catch(err => alert('上传失败: ' + err));
}

// 打开/关闭模态框
function openModal(id) {
    document.getElementById(id).classList.add('show');
}
function closeModal(id) {
    document.getElementById(id).classList.remove('show');
}

// 消息提示自动关闭
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 300);
        }, 3000);
    });
});

// 确认删除
function confirmDelete(url, name) {
    if (confirm('确定要删除 "' + name + '" 吗？此操作不可撤销。')) {
        window.location.href = url;
    }
}

// 预览图片
function previewImage(url, targetId) {
    const img = document.getElementById(targetId);
    if (img) {
        img.src = url;
        img.style.display = 'block';
    }
}

// 格式化日期
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.getFullYear() + '-' +
           String(date.getMonth() + 1).padStart(2, '0') + '-' +
           String(date.getDate()).padStart(2, '0');
}
