/**
 * HomeEat 公共JS工具 V3
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
                showToast('上传成功', 'success');
            } else {
                showToast(data.msg || '上传失败', 'error');
            }
        })
        .catch(err => showToast('上传失败: ' + err, 'error'));
}

// 打开/关闭模态框
function openModal(id) {
    const el = document.getElementById(id);
    if (el) {
        el.classList.add('show');
        document.body.style.overflow = 'hidden';
    }
}
function closeModal(id) {
    const el = document.getElementById(id);
    if (el) {
        el.classList.remove('show');
        document.body.style.overflow = '';
    }
}

// 点击遮罩关闭模态框
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal-overlay') && e.target.classList.contains('show')) {
        e.target.classList.remove('show');
        document.body.style.overflow = '';
    }
});

// ESC 键关闭模态框
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal-overlay.show').forEach(function(m) {
            m.classList.remove('show');
        });
        document.body.style.overflow = '';
    }
});

// Toast 消息提示
function showToast(message, type) {
    type = type || 'info';
    const toast = document.createElement('div');
    toast.className = 'toast-msg toast-' + type;
    toast.textContent = message;
    document.body.appendChild(toast);
    requestAnimationFrame(function() { toast.classList.add('toast-show'); });
    setTimeout(function() {
        toast.classList.remove('toast-show');
        setTimeout(function() { toast.remove(); }, 300);
    }, 3000);
}

// 消息提示自动关闭
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(function() { alert.remove(); }, 300);
        }, 4000);
    });

    // 统计数字动画
    document.querySelectorAll('.stat-number').forEach(function(el) {
        const text = el.textContent.trim();
        const num = parseInt(text);
        if (!isNaN(num) && num > 0 && num < 100000) {
            el.textContent = '0';
            animateCounter(el, 0, num, 600);
        }
    });

    // 表格行渐入动画
    document.querySelectorAll('.data-table tbody tr').forEach(function(row, i) {
        row.style.opacity = '0';
        row.style.transform = 'translateY(8px)';
        row.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        setTimeout(function() {
            row.style.opacity = '1';
            row.style.transform = 'translateY(0)';
        }, 40 * i);
    });
});

// 数字递增动画
function animateCounter(el, start, end, duration) {
    const range = end - start;
    const startTime = performance.now();
    function step(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.floor(start + range * eased);
        if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
}

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
