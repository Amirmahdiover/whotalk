const toggleButton = document.getElementById('toggleMenu');
const menu = document.getElementById('menu');
const overlay = document.getElementById('overlay');

toggleButton.addEventListener('click', () => {
    menu.classList.toggle('visible');
    overlay.classList.toggle('visible');
});

// وقتی روی هاله کلیک شد، منو و هاله مخفی شوند
overlay.addEventListener('click', () => {
    menu.classList.remove('visible');
    overlay.classList.remove('visible');
});

// تنظیمات اولیه هنگام بارگذاری صفحه
function updateMenuVisibility() {
    if (window.innerWidth > 768) {
        menu.classList.remove('menu-float', 'visible');
        overlay.classList.remove('visible');
    } else {
        menu.classList.add('menu-float');
        menu.classList.remove('visible');
        overlay.classList.remove('visible');
    }
}

// تغییر وضعیت منو هنگام تغییر اندازه صفحه
window.addEventListener('resize', updateMenuVisibility);

// تنظیم اولیه هنگام بارگذاری صفحه
updateMenuVisibility();


function openModal() {
    document.getElementById('company-modal').style.display = 'flex';
}

function closeModal(event) {
    const modal = document.getElementById('company-modal');
    if (!event || event.target === modal) {
        modal.style.display = 'none';
        document.getElementById('up-btn-faqs').value = 'ایجاد هوتاک';
        document.getElementById('company-id').value = '';
        document.getElementById('name').value = '';
        document.getElementById('website').value = '';
        document.getElementById('welcome_message').value = '';
    }
}
function openModalEdit(companyId = '', companyName = '', companyWebsite = '', companyWelcome = '') {
    const modal = document.getElementById('company-modal');
    modal.style.display = 'flex';

    // پر کردن اطلاعات فرم
    document.getElementById('company-id').value = companyId;
    document.getElementById('name').value = companyName;
    document.getElementById('website').value = companyWebsite;
    document.getElementById('welcome_message').value = companyWelcome === 'None' || companyWelcome === null ? '' : companyWelcome;
    document.getElementById('up-btn-faqs').value = 'ویرایش هوتاک';
}
function copyToClipboard(companyId) {
    const apiKeyElement = document.getElementById(`api-${companyId}`);
    const apiKey = apiKeyElement.textContent;

    navigator.clipboard.writeText(apiKey).then(() => {
        alert('کلید API با موفقیت کپی شد!');
    }).catch(err => {
        console.error('Error copying API key:', err);
        alert('مشکلی در کپی کردن کلید API رخ داد.');
    });
}
