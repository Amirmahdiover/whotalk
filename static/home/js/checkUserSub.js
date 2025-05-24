function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function checkUserSubscriptionAndCreateChatbot() {
    fetch('/check-subscription/', { 
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.subscribed) {
            openModal()
                // Hide any old messages
            const msgEl = document.getElementById('subscription-message');
            if (msgEl) {
                msgEl.style.display = 'none';
            }
        } else {
            const msgEl = document.getElementById('subscription-message');
            if (msgEl) {
                msgEl.innerText = 'برای ساخت چت‌بات، ابتدا اشتراک خریداری کنید.';
                msgEl.style.display = 'block';
            }
        }
    })
    .catch(error => {
        console.error('🚫 Error checking subscription:', error);
    });
}
