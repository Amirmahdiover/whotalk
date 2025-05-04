const $ = document;
const loginShow = $.querySelector('.login-show');
const modalBackgroundParent = $.querySelector('.modal-background-parent'),
    closeModal = $.querySelector('.close-modal'),
    chatModalButton = $.querySelector('.chat-modal-button'),
    chatUserParent = $.querySelector('.chat-user-parent'),
    closeButton = $.querySelector('.close-button'),
    fileInputMessageUser = $.querySelector('#fileInput-user'),
    NumberSendInfo = $.querySelector('#number-send-info'),
    SendInfoButtonTop = $.querySelector('#send-info-button-top'),
    // faqSection = $.querySelector('.faq-section'),
    // faqBoxes = document.querySelectorAll('.faq-box'),
    sendMessage = $.querySelector('.send-message'),
    swiperContainer = document.querySelector('.swiper-container');


let number = $.querySelector('.number'),
    sendInfoButton = $.querySelector('.send-info-button'),
    userInfo = $.querySelector('.user-info'),
    chatUserFooter = $.querySelector('.chat-user-footer'),
    textType = $.querySelector('.text-type'),
    sendIN = $.querySelector('.send-in'),
    chatUserBody = $.querySelector('.chat-user-body');

if (fileInputMessageUser) {
    fileInputMessageUser.addEventListener("change", function () {
        const fileNameElement = $.getElementById("file-name-message-user");
        if (!fileNameElement) {
            return;
        }
        if (this.files && this.files[0]) {
            fileNameElement.textContent = "فایل انتخاب شده: " + this.files[0].name;
        } else {
            fileNameElement.textContent = "هیچ فایلی انتخاب نشده است";
        }
    });
}

$.addEventListener('DOMContentLoaded', function () {
    if (loginShow) {
        loginShow.addEventListener('click', function (e) {
            e.preventDefault()
            modalBackgroundParent.style.display = 'block';
            chatModalButton.style.visibility = 'hidden';
        })
    } else {
        // console.warn('not found in DOM.');
    }
});

if (closeModal) {
    closeModal.addEventListener('click', () => {
        modalBackgroundParent.style.display = 'none';
        chatModalButton.style.visibility = 'visible';
    })
}

if (textType) {
    textType.addEventListener('keypress', function (event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            // showLoadingIndicator(); // Show the loading indicator
            sendMessagef()
        }
    });
}

// document.addEventListener('DOMContentLoaded', function () {
//     faqBoxes.forEach(box => {
//         box.addEventListener('click', () => {
//             const question = box.textContent.trim(); // گرفتن متن سوال
//             sendMessageFromFAQ(question); // ارسال مستقیم متن
//         });
//     });
//
//     function sendMessageFromFAQ(message) {
//         if (message) {
//             textType.value = message; // تنظیم متن در textarea (اختیاری)
//             // showLoadingIndicator(); // نمایش شاخص بارگذاری
//             sendMessagef();
//             textType.value = '';
//         }
//     }
// });


function openChat() {
    chatUserParent.classList.remove('hide'); // حذف کلاس hide
    chatUserParent.style.display = 'block'; // نمایش مستقیم
    chatUserParent.classList.add('show'); // اضافه کردن کلاس show
}

if (chatModalButton) {
    chatModalButton.addEventListener('click', openChat);
}

if (SendInfoButtonTop) {
    SendInfoButtonTop.addEventListener('click', (event) => {
        event.preventDefault(); // لغو رفتار پیش‌فرض
        openChat();
    });
}


// بستن چت با انیمیشن
if (closeButton) {
    closeButton.addEventListener('click', () => {
        chatUserParent.classList.remove('show'); // حذف کلاس show
        chatUserParent.classList.add('hide'); // اضافه کردن کلاس hide

        // پنهان کردن پس از اتمام انیمیشن
        chatUserParent.addEventListener(
            'animationend',
            () => {
                if (chatUserParent.classList.contains('hide')) {
                    chatUserParent.style.display = 'none'; // مخفی کردن پس از انیمیشن
                }
            },
            {once: true} // اطمینان از اجرای یک‌باره
        );
    });
}

//chat user.body scroll
let scroll = () => {
    chatUserBody.scrollTo({
        top: chatUserBody.scrollHeight,
        behavior: "smooth"
    });
};


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Function to fetch user's IP
function fetchUserIP() {
    return fetch('/get-ip/')
        .then(response => response.json())
        .then(data => data.ip);
}

// Function to fetch user's company
let fetchCompany = (apikey) => {
    return fetch('/get-company-from-api-key/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFtoken': csrftoken,
        },
        body: JSON.stringify({'apikey': apikey}),
    })
        .then(res => {
            if (!res.ok) {
                throw new Error('Network response was not ok');
            }
            return res.json();
        })
        .then(data => {
            console.log('Company Name:', data.company_name);
            console.log('Owner Name:', data.owner_name);
            // به جای برگشت فقط company_name، کل data را برمی‌گردانیم
            return data;
        })
        .catch(error => {
            console.error('Error fetching company:', error);
            throw error; // Ensure the error propagates
        });
};

function convertToEnglishNumbers(input) {
    return input.replace(/[\u06F0-\u06F9]/g, (digit) => {
        return String.fromCharCode(digit.charCodeAt(0) - 0x06F0 + 48);
    }).replace(/[\u0660-\u0669]/g, (digit) => {
        return String.fromCharCode(digit.charCodeAt(0) - 0x0660 + 48);
    });
}

let array = [];
const apiKey = "08db4b82d3787b0d6e881b44b415310838fcd183:1:e6b41b845171c84c"; // Connection server


function handleNumberSubmission() {
    let numberValue = convertToEnglishNumbers(number.value);
    if (numberValue.match('^(\\+98|0)?9\\d{9}$')) {
        fetchCompany(apiKey).then((companyData) => {
            fetchUserIP().then((userIP) => {
                array.push({
                    'userEmail': userIP, 'userNumber': numberValue, 'companyName': companyData.company_name,
                    'ownerName': companyData.owner_name
                });
                connect(userIP, numberValue, companyData.company_name, companyData.owner_name);
            }).catch(error => {
                console.error('Error fetching user IP:', error);
            });
        }).catch(error => {
            console.error('Error fetching company name:', error);
        });
    } else {
        alert('لطفا شماره همراه صحیح وارد کنید');
    }
    number.value = ''; // Reset input field
}

// Event listeners
if (sendInfoButton) {
    sendInfoButton.addEventListener('click', handleNumberSubmission);
}

if (NumberSendInfo) {
    NumberSendInfo.addEventListener('keypress', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            handleNumberSubmission();
        }
    });
}

function clearChatMessages() {
    chatUserBody.innerHTML = '';
}

// Create all message
let allMessageCreator = (data) => {
    data.forEach((item) => {
        if (item.sent_for) {
            let chatMessageBox = $.createElement('div');
            const displayFileName = item.fileName ? (item.fileName.split('/').pop().length > 15 ? `${item.fileName.split('/').pop().slice(0, 10)}...` : item.fileName.split('/').pop()) : '';
            chatMessageBox.setAttribute('class', 'sent-chat-box-parent');
            chatMessageBox.innerHTML = `
                <div class="sent-chat-box">
                   <div class="body">
                    <p>${item.msgText}</p>
                   </div>
                 <div class="footer-detail">
                 <p class="time-sent">${item.dateTimeStatus}</p>
                 ${item.fileName ? `
                <p class="attached-file-admin">
                    <svg width="12px" height="12px" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" fill="#000000" transform="matrix(-1, 0, 0, 1, 0, 0)">
                        <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                        <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
                        <g id="SVGRepo_iconCarrier">
                            <path d="M7.44 15.44a1.5 1.5 0 0 0 2.115 2.125L20.111 7.131a3 3 0 1 0-4.223-4.262L4.332 14.304a4.5 4.5 0 1 0 6.364 6.363l8.98-9.079.712.703-8.981 9.08a5.5 5.5 0 1 1-7.779-7.777L15.185 2.159a4 4 0 1 1 5.63 5.683L10.259 18.276a2.5 2.5 0 0 1-3.527-3.544l8-8 .707.707z"></path>
                            <path fill="none" d="M0 0h24v24H0z"></path>
                        </g>
                    </svg>
                </p>
                <p class="file-name-dl">
                    <a href="${item.fileName}" target="_blank">${displayFileName}</a>
                </p>
            ` : ''}
                </div></div>`;
            chatUserBody.append(chatMessageBox)
            scroll()
        } else if (item.received_from) {
            let chatMessageBox = $.createElement('div');
            const displayFileName = item.fileName ? (item.fileName.split('/').pop().length > 15 ? `${item.fileName.split('/').pop().slice(0, 10)}...` : item.fileName.split('/').pop()) : '';
            chatMessageBox.setAttribute('class', 'received-chat-box-parent');
            chatMessageBox.innerHTML = `
            <div class="received-chat-box">
                <div class="header">
                <span><p>${item.msgSender}</p>
                    <div class="admin-pic">
                        <img src=${item.msgImg} alt="">
                    </div>
                </span>
                </div>
                <div class="body">
                    <p>${item.msgText}</p>
                </div>
                <div class="footer-detail">
                ${item.fileName ? `
                <p class="file-name-dl">
                    <a href="${item.fileName}" target="_blank">${displayFileName}</a>
                </p>
                <p class="attached-file-admin">
                        <svg width="12px" height="12px" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"
                             fill="#000000" transform="matrix(-1, 0, 0, 1, 0, 0)">
                            <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                            <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
                            <g id="SVGRepo_iconCarrier">
                                <path d="M7.44 15.44a1.5 1.5 0 0 0 2.115 2.125L20.111 7.131a3 3 0 1 0-4.223-4.262L4.332 14.304a4.5 4.5 0 1 0 6.364 6.363l8.98-9.079.712.703-8.981 9.08a5.5 5.5 0 1 1-7.779-7.777L15.185 2.159a4 4 0 1 1 5.63 5.683L10.259 18.276a2.5 2.5 0 0 1-3.527-3.544l8-8 .707.707z"></path>
                                <path fill="none" d="M0 0h24v24H0z"></path>
                            </g>
                        </svg>
                    </p>
            ` : ''}
                   <p class="time-received">${item.dateTimeStatus}</p>
                </div>
            </div>
            `
            chatUserBody.append(chatMessageBox)
        }
        scroll()
    })
    // scroll()
}

// setTimeout(function (){getAllMessages()}, 2000)


//get all messages sent by user to admin and sent by admin to user
let getAllMessages = () => {
    if (JSON.parse(localStorage.getItem('user'))) {
        fetch('/all-messages/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFtoken': csrftoken,
            },
            body: JSON.stringify({
                msg_sender_admin: JSON.parse(localStorage.getItem('admin')),
                msg_sender: JSON.parse(localStorage.getItem('user'))[0].userEmail,
                msg_sender_number: JSON.parse(localStorage.getItem('user'))[0].userNumber,
                msg_sender_img: JSON.parse(localStorage.getItem('admin_url'))
            }),
        })
            .then(res => res.json())
            .then(data => {
                allMessageCreator(data)
            })
    }
}

getAllMessages()

//Create WELCOME admin Message template
let welcomeAdminMessageCreator = (data) => {
    let chatMessageBox = $.createElement('div');
    chatMessageBox.setAttribute('class', 'received-chat-box-parent');
    chatMessageBox.innerHTML = `
    <div class="received-chat-box">
        <div class="header">
         <span><p>${data.msgSender}</p>
                    <div class="admin-pic">
                        <img src=${data.msgImg} alt="">
                    </div>
                </span>
        </div>
        <div class="body">
            <p>${data.msgTextAdmin}</p>
        </div>
        <div class="footer-detail">
           <p class="time-received">${data.dateTimeStatus}</p>
        </div>
        
    </div>
    `;
    chatUserBody.append(chatMessageBox);
    scroll();
}


//get all messages sent by user to admin and sent by admin to user
let welcomeAdminMessage = () => {
    if (JSON.parse(localStorage.getItem('user'))) {
        fetch('/welcome-message/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFtoken': csrftoken,
            },
            body: JSON.stringify({
                msg_sender_admin: JSON.parse(localStorage.getItem('admin')),
                msg_sender: JSON.parse(localStorage.getItem('user'))[0].userEmail,
                msg_sender_number: JSON.parse(localStorage.getItem('user'))[0].userNumber,
                msg_sender_img: JSON.parse(localStorage.getItem('admin_url')),
                company: JSON.parse(localStorage.getItem('company_name')),
            }),
        })
            .then(res => {
                if (res.status === 204) {
                    return; // Stop further processing
                }
                return res.json();
            })
            .then(data => {
                if (data) {
                    welcomeAdminMessageCreator(data)
                }
            })
    }
}


function connect(email, number, company, admin) {
    fetch('/connect/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFtoken': csrftoken,
        },
        body: JSON.stringify({'userEmail': email, 'userNumber': number, 'company': company, 'admin': admin}),
    })
        .then(res => res.json())
        .then(data => {
            console.log(data);
            userInfo.remove()

            chatUserFooter.style.display = 'flex';
            // faqSection.style.display = 'flex';
            //save user in localstorage
            localStorage.setItem('user', JSON.stringify(array));
            //save admin in localstorage
            localStorage.setItem('admin', JSON.stringify(data.admin));
            // localStorage.setItem('admin2', JSON.stringify(data.admin2));
            localStorage.setItem('admin_url', JSON.stringify(data.admin_url));
            //save company name
            localStorage.setItem('company_name', JSON.stringify(data.company_name));
            // getAllMessages()
            if (JSON.parse(localStorage.getItem('admin')) !== 'Offline') {
                setTimeout(function () {
                    getAllMessages()
                }, 1000);
            }
            setTimeout(function () {
                welcomeAdminMessage()
            }, 2000);
        })
}


// User-info-remover
let userInfoRemover = () => {
    if (localStorage.getItem('user')) {
        userInfo.remove()
        chatUserFooter.style.display = 'flex';
        // faqSection.style.display = 'flex';
    }
}
userInfoRemover()

function showLoadingIndicator() {
    const loadingIndicator = document.createElement('div');
    loadingIndicator.setAttribute('id', 'loading-indicator');
    loadingIndicator.setAttribute('class', 'loading-indicator');
    loadingIndicator.textContent = 'در انتظار پاسخ...';
    sendIN.append(loadingIndicator);
    scroll(); // Ensure it's visible
}

// Remove the loading message from the chat UI
function hideLoadingIndicator() {
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.remove();
    }
}

//message creator => User message to admin
let messageCreator = (data) => {
    let chatMessageBox = $.createElement('div');
    const displayFileName = data.fileName ? (data.fileName.split('/').pop().length > 15 ? `${data.fileName.split('/').pop().slice(0, 10)}...` : data.fileName.split('/').pop()) : '';

    chatMessageBox.setAttribute('class', 'sent-chat-box-parent');
    chatMessageBox.innerHTML = `
        <div class="sent-chat-box">
           <div class="body">
            <p>${data.msgTextType}</p>
           </div>
           <div class="footer-detail">
         <p class="time-sent">${data.dateTimeStatus}</p>
                 ${data.fileName ? `
                <p class="attached-file-admin">
                    <svg width="12px" height="12px" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" fill="#000000" transform="matrix(-1, 0, 0, 1, 0, 0)">
                        <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                        <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
                        <g id="SVGRepo_iconCarrier">
                            <path d="M7.44 15.44a1.5 1.5 0 0 0 2.115 2.125L20.111 7.131a3 3 0 1 0-4.223-4.262L4.332 14.304a4.5 4.5 0 1 0 6.364 6.363l8.98-9.079.712.703-8.981 9.08a5.5 5.5 0 1 1-7.779-7.777L15.185 2.159a4 4 0 1 1 5.63 5.683L10.259 18.276a2.5 2.5 0 0 1-3.527-3.544l8-8 .707.707z"></path>
                            <path fill="none" d="M0 0h24v24H0z"></path>
                        </g>
                    </svg>
                </p>
                <p class="file-name-dl">
                    <a href="${data.fileName}" target="_blank">${displayFileName}</a>
                </p>
            ` : ''}
        </div></div>`;
    chatUserBody.append(chatMessageBox)
    scroll()

}

function checkForAdminResponse(messageId) {
    const pollInterval = 4000; // 3 ثانیه
    const maxRetries = 20; // حداکثر تعداد تلاش‌ها
    let retries = 0;

    const poll = setInterval(() => {
        if (retries >= maxRetries) {
            clearInterval(poll);
            console.error("پاسخی از ادمین دریافت نشد.");
            sendMessage.disabled = false; // فعال کردن دکمه
            textType.disabled = false; // فعال کردن ورودی
            hideLoadingIndicator();
            return;
        }

        fetch(`/check-response/${messageId}/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFtoken': csrftoken,
            },
        })
            .then(res => res.json())
            .then(data => {
                if (data.adminResponse) {
                    hideLoadingIndicator();
                    // adminMessageCreatorFromAPI(data.adminResponse);
                    clearInterval(poll); // توقف Polling
                    sendMessage.disabled = false; // فعال کردن دکمه
                    textType.disabled = false; // فعال کردن ورودی
                    textType.focus();
                }
            })
            .catch(error => {
                console.error('Error checking admin response:', error);
                sendMessage.disabled = false; // فعال کردن دکمه
                textType.disabled = false; // فعال کردن ورودی
                hideLoadingIndicator();
            });

        retries++;
    }, pollInterval);
}

if (sendMessage) {
    sendMessage.addEventListener('click', () => {
        sendMessagef();
    })
}

//Create admin Message template
let adminMessageCreatorFromAPI = (data) => {
    let chatMessageBox = $.createElement('div');
    const displayFileName = data.fileName ? (data.fileName.split('/').pop().length > 15 ? `${data.fileName.split('/').pop().slice(0, 10)}...` : data.fileName.split('/').pop()) : '';
    chatMessageBox.setAttribute('class', 'received-chat-box-parent');
    chatMessageBox.innerHTML = `
    <div class="received-chat-box">
        <div class="header">
         <span><p>${data.msgSender}</p>
                    <div class="admin-pic">
                        <img src=${data.msgImg} alt="">
                    </div>
                </span>
        </div>
        <div class="body">
            <p>${data.msgTextAdmin}</p>
        </div>
        <div class="footer-detail">
            ${data.fileName ? `
                <p class="file-name-dl">
                    <a href="${data.fileName}" target="_blank">${displayFileName}</a>
                </p>
                <p class="attached-file-admin">
                        <svg width="12px" height="12px" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"
                             fill="#000000" transform="matrix(-1, 0, 0, 1, 0, 0)">
                            <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                            <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
                            <g id="SVGRepo_iconCarrier">
                                <path d="M7.44 15.44a1.5 1.5 0 0 0 2.115 2.125L20.111 7.131a3 3 0 1 0-4.223-4.262L4.332 14.304a4.5 4.5 0 1 0 6.364 6.363l8.98-9.079.712.703-8.981 9.08a5.5 5.5 0 1 1-7.779-7.777L15.185 2.159a4 4 0 1 1 5.63 5.683L10.259 18.276a2.5 2.5 0 0 1-3.527-3.544l8-8 .707.707z"></path>
                                <path fill="none" d="M0 0h24v24H0z"></path>
                            </g>
                        </svg>
                    </p>
            ` : ''}
           <p class="time-received">${data.dateTimeStatus}</p>
        </div>
        
    </div>
    `;
    chatUserBody.append(chatMessageBox);
    scroll();
}

function sendMessagef() {
    sendMessage.disabled = true; // غیرفعال کردن دکمه ارسال
    textType.disabled = true;
    const file = fileInputMessageUser.files[0]; // Get the selected file
    const fileNameMessage = document.getElementById('file-name-message-user');
    if (textType.value.length > 0 && localStorage.getItem('user')) {
        if (file) {
            const reader = new FileReader();
            reader.onload = function () {
                const fileData = reader.result.split(',')[1]; // Get Base64 content
                sendMessageRequestUser({
                    msg: textType.value,
                    msg_sender: JSON.parse(localStorage.getItem('user'))[0].userEmail,
                    msg_sender_number: JSON.parse(localStorage.getItem('user'))[0].userNumber,
                    msg_receiver: JSON.parse(localStorage.getItem('admin')),
                    company: JSON.parse(localStorage.getItem('company_name')),
                    file_name: file.name,
                    file_data: fileData,
                });
            };
            reader.onerror = function (error) {
                console.error('Error reading file:', error);
            };
            reader.readAsDataURL(file); // Read the file as Base64
        } else {
            // Send the request without a file
            sendMessageRequestUser({
                msg: textType.value,
                msg_sender: JSON.parse(localStorage.getItem('user'))[0].userEmail,
                msg_sender_number: JSON.parse(localStorage.getItem('user'))[0].userNumber,
                msg_receiver: JSON.parse(localStorage.getItem('admin')),
                company: JSON.parse(localStorage.getItem('company_name')),
                file_name: null,
                file_data: null,
            });
        }
    } else {
        fileNameMessage.textContent = 'لطفاً فایل خود را مجددا انتخاب کنید و پیامی را بنویسید.';
        sendMessage.disabled = false; // فعال کردن مجدد دکمه
        textType.disabled = false; // فعال کردن مجدد ورودی پیام
    }
}

function sendMessageRequestUser(payload) {
    fetch('/send-message/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFtoken': csrftoken,
        },
        body: JSON.stringify(payload),
    })
        .then(res => res.json())
        .then(data => {
            textType.value = '';
            fileInputMessageUser.value = ''; // Clear file input
            messageCreator(data);
            showLoadingIndicator();
            $.getElementById('file-name-message-user').textContent = 'هیچ فایلی انتخاب نشده است';
            const messageId = data.messageId;
            if (messageId) {
                checkForAdminResponse(messageId);
            } else {
                console.error("Message ID not found in response:", data);
            }
        })
        .catch(error => console.error('Error:', error));
}


//Create admin Message template
let adminMessageCreator = (data) => {
    data.forEach((item) => {
        let chatMessageBox = $.createElement('div');
        const displayFileName = item.fileName ? (item.fileName.split('/').pop().length > 15 ? `${item.fileName.split('/').pop().slice(0, 10)}...` : item.fileName.split('/').pop()) : '';
        chatMessageBox.setAttribute('class', 'received-chat-box-parent');
        chatMessageBox.innerHTML = `
        <div class="received-chat-box">
            <div class="header">
             <span><p>${item.msgSender}</p>
                <div class="admin-pic">
                    <img src=${item.msgImg} alt="">
                </div>
             </span>
            </div>
            <div class="body">
                    <p class="typing-received"></p>
<!--                <p>${item.msgText}</p>-->
            </div>
            <div class="footer-detail">
            ${item.fileName ? `
                <p class="file-name-dl">
                    <a href="${item.fileName}" target="_blank">${displayFileName}</a>
                </p>
                <p class="attached-file-admin">
                        <svg width="12px" height="12px" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"
                             fill="#000000" transform="matrix(-1, 0, 0, 1, 0, 0)">
                            <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                            <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
                            <g id="SVGRepo_iconCarrier">
                                <path d="M7.44 15.44a1.5 1.5 0 0 0 2.115 2.125L20.111 7.131a3 3 0 1 0-4.223-4.262L4.332 14.304a4.5 4.5 0 1 0 6.364 6.363l8.98-9.079.712.703-8.981 9.08a5.5 5.5 0 1 1-7.779-7.777L15.185 2.159a4 4 0 1 1 5.63 5.683L10.259 18.276a2.5 2.5 0 0 1-3.527-3.544l8-8 .707.707z"></path>
                                <path fill="none" d="M0 0h24v24H0z"></path>
                            </g>
                        </svg>
                    </p>
            ` : ''}
           <p class="time-received">${item.dateTimeText}</p>
        </div>
        </div>
        `;

        chatUserBody.append(chatMessageBox);

        // اجرای انیمیشن تایپ
        const textElement = chatMessageBox.querySelector('.typing-received');
        const text = item.msgText;
        let charIndex = 0;

        const typeInterval = setInterval(() => {
            if (charIndex < text.length) {
                textElement.textContent += text[charIndex];
                charIndex++;
                chatUserBody.scrollTop = chatUserBody.scrollHeight; // اسکرول خودکار به پایین
            } else {
                clearInterval(typeInterval);
            }
        }, 50); // سرعت تایپ (قابل تغییر)
    });
};


// chatUserBody.appendChild(messageElement);
// chatUserBody.scrollTop = chatUserBody.scrollHeight;
//
// const textElement = messageElement.querySelector(".typing-received");
// const text = message.text;
// let charIndex = 0;
//
// const typeInterval = setInterval(() => {
//     if (charIndex < text.length) {
//         textElement.textContent += text[charIndex];
//         charIndex++;
//         chatUserBody.scrollTop = chatUserBody.scrollHeight; // اسکرول خودکار
//     } else {
//         clearInterval(typeInterval);
//     }
// }, 50); // سرعت تایپ را می‌توانید تغییر دهید
// scroll()

//get message from admin to user
let getAdminMessages = () => {
    if (JSON.parse(localStorage.getItem('admin'))) {
        fetch('/admin-message/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFtoken': csrftoken,
            },
            body: JSON.stringify({
                msg_sender: JSON.parse(localStorage.getItem('admin')),
                msg_receiver: JSON.parse(localStorage.getItem('user'))[0].userEmail,
                msg_receiver_number: JSON.parse(localStorage.getItem('user'))[0].userNumber,
                msg_sender_img: JSON.parse(localStorage.getItem('admin_url'))
            }),
        })
            .then(res => res.json())
            .then(data => {
                // console.log(data);
                if (data.length > 0) {
                    setTimeout(function () {
                        adminMessageCreator(data)
                    }, 2000)
                }
            })
    }
}

// getAdminMessages()
setInterval(getAdminMessages, 2000)
//

let onlineAdminFinder = () => {
    let admin = JSON.parse(localStorage.getItem('admin'));
    if (admin == 'Offline') {
        fetch('/online-admin/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFtoken': csrftoken,
            },
            body: JSON.stringify({
                userEmail: JSON.parse(localStorage.getItem('user'))[0].userEmail,
                userNumber: JSON.parse(localStorage.getItem('user'))[0].userNumber
            }),
        })
            .then(res => res.json())
            .then(data => {
                console.log(data);
                localStorage.removeItem('admin');
                localStorage.setItem('admin', JSON.stringify(data.admin));
                localStorage.setItem('admin_url', JSON.stringify(data.admin_url));

                if (JSON.parse(localStorage.getItem('admin')) !== 'Offline') {
                    clearChatMessages();
                    getAllMessages();
                    clearInterval(di);
                }
            })
    }
}
let di = setInterval(onlineAdminFinder, 2000)

if (swiperContainer) {
    const swiper = new Swiper(swiperContainer, {
        slidesPerView: 'auto', // تعداد لوگوهای قابل نمایش متناسب با عرض
        spaceBetween: 30, // فاصله بین لوگوها
        loop: true, // فعال کردن حلقه
        speed: 5000, // سرعت حرکت
        autoplay: {
            delay: 0, // بدون توقف
            disableOnInteraction: false, // ادامه حرکت پس از تعامل
        },
        freeMode: true, // فعال‌سازی حالت آزاد برای حرکت پیوسته
        freeModeMomentum: false, // حذف شتاب اضافی
        breakpoints: {
            320: {slidesPerView: 2, spaceBetween: 10},
            768: {slidesPerView: 3, spaceBetween: 20},
            1024: {slidesPerView: 5, spaceBetween: 30},
        },
    });
}
document.addEventListener("DOMContentLoaded", function () {
    // همه‌ی عنوان‌های فوتر را انتخاب می‌کنیم
    var footerTitles = document.querySelectorAll("footer h4.footer-title");

    footerTitles.forEach(function (title) {
        title.addEventListener("click", function () {
            // با کلیک، کلاس active را اضافه/حذف می‌کنیم
            this.classList.toggle("active");
        });
    });
});