const $ = document;
const settingModal = $.querySelector('.setting-modal'),
    settingMenu = $.querySelector('.setting-menu'),
    // connectionRemover = $.querySelector('#connection-remover'),
    customers = $.querySelector('.customers'),
    dropdownList = $.querySelector('.dropdown-list'),
    sendMessageAdmin = $.querySelector('.send-message'),
    textAdmin = $.querySelector('.text-admin'),
    messageBoxAdmin = $.querySelector('#body'),
    leftSide = $.querySelector('.left-side'),
    rightSide = $.querySelector('.right-side'),
    topLeft = $.querySelector('.top-left'),
    // formUploadAdmin = $.querySelector('#faq-upload-form'),
    // uploadBtnAdmin = $.querySelector('#upload-faq-btn'),
    fileInput = $.querySelector('#faq'),
    fileInputMessageAdmin = $.querySelector('#fileInput-admin'),
    errorMessage = $.querySelector('#error-message'),
    closeButtonAdmin = $.querySelector('.close-modal-faq'),
    closeButtonApiAdmin = $.querySelector('.close-modal-API'),
    closeButtonFormAdmin = $.querySelector('.close-btn-bottom'),
    // modalApiParent = $.querySelector('.modal-API-parent'),
    modalUploadFaqParent = $.querySelector('.modal-upload-faq-parent'),
    customFileUploadAdmin = $.querySelector('.custom-file-upload-admin'),
    ffAdmin = $.querySelector('#ffAdmin'),
    apiShow = $.querySelector('#api-show'),
    faqShow = $.querySelector('.faq-show');


textAdmin.addEventListener('keypress', function (event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessagefAdmin()
    }
});


document.addEventListener("DOMContentLoaded", function () {
    const dropdownButton = document.getElementById("dropdown-button");
    const dropdownMenu = document.getElementById("dropdown-menu");
    const dropdownSearch = document.getElementById("dropdown-search");
    const dropdownList = document.getElementById("dropdown-list");
    const dropdownItems = document.querySelectorAll(".dropdown-item");
    const selectedCompanyInput = document.getElementById("selected-company");

    // باز و بسته کردن لیست کشویی
    dropdownButton.addEventListener("click", function () {
        dropdownMenu.classList.toggle("hidden");
        dropdownSearch.value = ""; // پاک کردن مقدار جستجو
        filterItems(""); // بازگرداندن همه آیتم‌ها
        dropdownSearch.focus(); // فوکوس روی فیلد جستجو
    });

    // انتخاب آیتم از لیست
    dropdownItems.forEach(item => {
        item.addEventListener("click", function () {
            const companyName = this.textContent;
            const companyId = this.dataset.id;

            // تنظیم مقدار انتخاب‌شده
            dropdownButton.textContent = companyName;
            selectedCompanyInput.value = companyId;

            // بستن لیست کشویی
            dropdownMenu.classList.add("hidden");
            leftSide.style.display = 'none';
            rightSide.style.display = 'flex';
        });
    });

    // فیلتر کردن آیتم‌ها بر اساس جستجو
    dropdownSearch.addEventListener("input", function () {
        const searchValue = this.value.toLowerCase();
        filterItems(searchValue);
    });

    function filterItems(query) {
        dropdownItems.forEach(item => {
            const itemText = item.textContent.toLowerCase();
            if (itemText.includes(query)) {
                item.style.display = "block";
            } else {
                item.style.display = "none";
            }
        });
    }

    // بستن منو اگر خارج از آن کلیک شود
    document.addEventListener("click", function (event) {
        if (!dropdownMenu.contains(event.target) && !dropdownButton.contains(event.target)) {
            dropdownMenu.classList.add("hidden");
        }
    });
});


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


// $.addEventListener('DOMContentLoaded', function () {
//     if (apiShow) {
//         apiShow.addEventListener('click', function (e) {
//             e.preventDefault()
//             modalApiParent.style.display = 'block';
//         });
//     } else {
//         console.warn('not found in DOM.');
//     }
// });

// closeButtonApiAdmin.addEventListener('click', () => {
//     modalApiParent.style.display = 'none';
// })
// $.addEventListener('DOMContentLoaded', function () {
//     settingMenu.addEventListener('click', (e) => {
//         e.stopPropagation();
//         settingModal.classList.toggle('show');
//     });
//
//     $.addEventListener('click', (e) => {
//         if (settingModal.classList.contains('show') || settingModal.contains(e.target)) {
//             settingModal.classList.remove('show');
//         }
//     });
// });

//
// fileInput.addEventListener("change", function () {
//     const fileNameElement = $.getElementById("file-name");
//     if (this.files && this.files[0]) {
//         fileNameElement.textContent = "فایل انتخاب شده: " + this.files[0].name;
//     } else {
//         fileNameElement.textContent = "هیچ فایلی انتخاب نشده است";
//     }
// });
//
//
// fileInputMessageAdmin.addEventListener("change", function () {
//     const fileNameElement = $.getElementById("file-name-message");
//     if (this.files && this.files[0]) {
//         fileNameElement.textContent = "فایل انتخاب شده: " + this.files[0].name;
//     } else {
//         fileNameElement.textContent = "هیچ فایلی انتخاب نشده است";
//     }
// });


// $.addEventListener('DOMContentLoaded', function () {
//     if (faqShow) {
//         faqShow.addEventListener('click', function (e) {
//             e.preventDefault()
//             modalUploadFaqParent.style.display = 'block';
//         });
//     } else {
//         console.warn('not found in DOM.');
//     }
// });


// $.addEventListener('DOMContentLoaded', function () {
//
//
//     if (faqShow) {
//         faqShow.addEventListener('click', function (e) {
//             e.preventDefault();
//             modalUploadFaqParent.style.display = 'block';
//         });
//     }
//
//     // نگه‌داشتن مدال باز پس از ارسال فرم
//     const messagesDiv = document.querySelector('.messages');
//     if (messagesDiv) {
//         modalUploadFaqParent.style.display = 'block';
//         setTimeout(() => {
//             messagesDiv.innerHTML = '';
//         }, 2000);
//     }
// });

// closeButtonAdmin.addEventListener('click', () => {
//     modalUploadFaqParent.style.display = 'none';
// })
// closeButtonFormAdmin.addEventListener('click', () => {
//     modalUploadFaqParent.style.display = 'none';
// })
//
topLeft.addEventListener('click', () => {
    leftSide.style.display = 'none';
    rightSide.style.display = 'flex';
});

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

const csrftoken2 = getCookie('csrftoken');


// //Admin Connection Remover
// connectionRemover.addEventListener('click', () => {
//     fetch('http://localhost:8000/admin-connection-remover/', {
//         method: 'GET',
//     })
//         .then(res => res.json())
//         .then(data => {
//             // console.log(data);
//
//         })
// })


//chat message box .body scroll
let scroll2 = () => {
    messageBoxAdmin.scrollTo({
        top: messageBoxAdmin.scrollHeight,
        behavior: "smooth"
    });
};
let scroll3 = () => {
    customers.scrollTo({
        top: customers.scrollTop,
        behavior: "smooth"
    });
};


// User selection
let userEmailAdmin = null,
    userNumberAdmin = null;

let company = null;

// Create all message
let allMessageCreatorAdmin = (data) => {
    data.forEach((item) => {
        if (item.sent_by_user) {
            let userChatMessageBoxAdmin = $.createElement('div');
            const displayFileName = item.fileName ? (item.fileName.split('/').pop().length > 15 ? `${item.fileName.split('/').pop().slice(0, 10)}...` : item.fileName.split('/').pop()) : '';
            userChatMessageBoxAdmin.setAttribute('class', 'received-chat-box-parent');
            userChatMessageBoxAdmin.innerHTML = `
            <div class="received-chat-box">
                <div class="header">
                    <p>${item.msgSender}</p>
                </div>
                <div class="body">
                    <p>${item.msgText}</p>
                </div>
                <div class="footer-detail">
                ${item.fileName ? `
                <p class="file-name-dl-user">
                    <a href="${item.fileName}" target="_blank">${displayFileName}</a>
                </p>
                <p class="attached-file-user">
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
            `;
            messageBoxAdmin.append(userChatMessageBoxAdmin);
            scroll2();
        } else if (item.sent_by_admin) {
            let chatMessageBoxAdmin = $.createElement('div');
            const displayFileName = item.fileName ? (item.fileName.split('/').pop().length > 15 ? `${item.fileName.split('/').pop().slice(0, 10)}...` : item.fileName.split('/').pop()) : '';

            chatMessageBoxAdmin.setAttribute('class', 'sent-chat-box-parent');
            chatMessageBoxAdmin.innerHTML = `
                <div class="admin-pic">
                    <img src=${item.msgImg} alt="">
                </div>
                <div class="sent-chat-box">
                    <div class="body">
                        <p>${item.msgText}</p>
                    </div>
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
                </div>`;
            messageBoxAdmin.append(chatMessageBoxAdmin);
            scroll2();
        }
    })
}


//get all messages panel admin - sent by user to admin and sent by admin to user
let getAllMessagesAdmin = () => {
    if (userNumberAdmin !== null && userEmailAdmin !== null) {
        fetch('/get-all-messages/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFtoken': csrftoken2,
            },
            body: JSON.stringify({msg_sender: userEmailAdmin, msg_sender_number: userNumberAdmin}),
        })
            .then(res => res.json())
            .then(data => {
                console.log(data);
                // data.sort((a, b) => new Date(a.dateTimeStatus) - new Date(b.dateTimeStatus));
                allMessageCreatorAdmin(data);
            })
    }
}


//Create user Message template admin
let userMessageCreatorAdmin = (data) => {
    data.forEach((item) => {
        let userChatMessageBoxAdmin = $.createElement('div');
        const displayFileName = item.fileName ? (item.fileName.split('/').pop().length > 15 ? `${item.fileName.split('/').pop().slice(0, 10)}...` : item.fileName.split('/').pop()) : '';
        userChatMessageBoxAdmin.setAttribute('class', 'received-chat-box-parent');
        userChatMessageBoxAdmin.innerHTML = `
        <div class="received-chat-box">
            <div class="header">
                <p>${item.msgSender}</p>
            </div>
            <div class="body">
                <p>${item.msgText}</p>
            </div>
            <div class="footer-detail">
                ${item.fileName ? `
                <p class="file-name-dl-user">
                    <a href="${item.fileName}" target="_blank">${displayFileName}</a>
                </p>
                <p class="attached-file-user">
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
            `;
        messageBoxAdmin.append(userChatMessageBoxAdmin)
    })
    scroll2()
}


//message creator => Admin message to user
let admin2MessageCreator = (data) => {
    let chatMessageBoxAdmin = $.createElement('div');
    const displayFileName = data.fileName ? (data.fileName.split('/').pop().length > 15 ? `${data.fileName.split('/').pop().slice(0, 10)}...` : data.fileName.split('/').pop()) : '';

    chatMessageBoxAdmin.setAttribute('class', 'sent-chat-box-parent');
    chatMessageBoxAdmin.innerHTML = `
        <div class="admin-pic">
            <img src=${data.msgImg} alt="">
        </div>
        <div class="sent-chat-box">
            <div class="body">
                <p>${data.msgTextAdmin}</p>
            </div>
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
        </div>`
    messageBoxAdmin.append(chatMessageBoxAdmin)
    scroll2()
}

//message creator => Admin message to user
let admin3MessageCreator = (data) => {
    data.forEach((item) => {
        let chatMessageBoxAdmin = $.createElement('div');
        const displayFileName = item.fileName ? (item.fileName.split('/').pop().length > 15 ? `${item.fileName.split('/').pop().slice(0, 10)}...` : item.fileName.split('/').pop()) : '';

        chatMessageBoxAdmin.setAttribute('class', 'sent-chat-box-parent');
        chatMessageBoxAdmin.innerHTML = `
            <div class="admin-pic">
                <img src=${item.msgImg} alt="">
            </div>
            <div class="sent-chat-box">
                <div class="body">
                    <p>${item.msgTextAdmin}</p>
                </div>
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
            </div>`
        messageBoxAdmin.append(chatMessageBoxAdmin)
    })
    scroll2()

}

sendMessageAdmin.addEventListener('click', () => {
    sendMessagefAdmin()
})

// Send message from admin to user
function sendMessagefAdmin() {
    const file = fileInputMessageAdmin.files[0]; // Get the selected file
    const fileNameMessage = document.getElementById('file-name-message');

    if (textAdmin.value.length > 0 && userNumberAdmin !== null && userEmailAdmin !== null && company !== null) {
        if (file) {
            const reader = new FileReader();
            reader.onload = function () {
                const fileData = reader.result.split(',')[1]; // Get Base64 content
                sendMessageRequest({
                    msg: textAdmin.value,
                    msg_receiver: userEmailAdmin,
                    msg_receiver_number: userNumberAdmin,
                    file_name: file.name,
                    file_data: fileData,
                    company: company,
                });
            };
            reader.onerror = function (error) {
                console.error('Error reading file:', error);
            };
            reader.readAsDataURL(file); // Read the file as Base64
        } else {
            // Send the request without a file
            sendMessageRequest({
                msg: textAdmin.value,
                msg_receiver: userEmailAdmin,
                msg_receiver_number: userNumberAdmin,
                file_name: null,
                file_data: null,
                company: company,
            });
        }
    } else {
        fileNameMessage.textContent = 'لطفاً فایل خود را مجددا انتخاب کنید و پیامی را بنویسید.';
    }
}

// Send request to the server
function sendMessageRequest(payload) {
    fetch('/send-admin-message/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken2,
        },
        body: JSON.stringify(payload),
    })
        .then(res => res.json())
        .then(data => {
            console.log(data);
            textAdmin.value = '';
            fileInputMessageAdmin.value = ''; // Clear file input
            $.getElementById('file-name-message').textContent = 'هیچ فایلی انتخاب نشده است';
            admin2MessageCreator(data); // Process server response
        })
        .catch(error => console.error('Error:', error));
}


// //Send message from admin to user
// function sendMessagefAdmin() {
//     if (textAdmin.value.length > 0 && userNumberAdmin !== null && userEmailAdmin !== null) {
//         let fileData = null;
//         if (file){
//             fileData = readFileAsBase64(file);
//         }
//         fetch('http://localhost:8000/send-admin-message/', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//                 'X-CSRFToken': csrftoken2,
//             },
//             // body: formData,
//             body: JSON.stringify({
//                 msg: textAdmin.value,
//                 msg_receiver: userEmailAdmin,
//                 msg_receiver_number: userNumberAdmin,
//
//             }),
//         })
//             .then(res => res.json())
//             .then(data => {
//                 // console.log(data);
//                 textAdmin.value = '';
//                 fileInputMessageAdmin.value = '';
//                 admin2MessageCreator(data);
//             })
//     }
// }

//get message from admin to user
let getUserMessagesAdmin = () => {
    if (userNumberAdmin !== null && userEmailAdmin !== null) {
        fetch('/get-user-message/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFtoken': csrftoken2,
            },
            body: JSON.stringify({msg_sender: userEmailAdmin, msg_sender_number: userNumberAdmin}),
        })
            .then(res => res.json())
            .then(data => {
                if (data.length > 0) {
                    userMessageCreatorAdmin(data);
                }
            });
    }
}
getUserMessagesAdmin();
// setInterval(getUserMessagesAdmin, 2000)


//get API from admin to ture/false
let getAPIMessagesAdmin = () => {
    if (userNumberAdmin !== null && userEmailAdmin !== null) {
        fetch('/get-api-message/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFtoken': csrftoken2,
            },
            body: JSON.stringify({msg_sender: userEmailAdmin, msg_sender_number: userNumberAdmin}),
        })
            .then(res => res.json())
            .then(data => {

            });
    }
}
getAPIMessagesAdmin();


// get refresh admin connections
let getAdminConnections = (company) => {
    fetch('/admin-connections/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFtoken': csrftoken2,
        },
        body: JSON.stringify({company: company}),
    })
        .then(res => res.json())
        .then(data => {
            // console.log(company);
            if (data.length > 0) {
                // console.log(data);
                connectionTemplateCreator(data)
            }
        });
}


//Connection template creator
let allConnectionTemplateCreator = (data) => {

    let userExists = false;
    Array.from(customers.children).forEach((item) => {
        numberAdminPanel = item.querySelector('.user-info').firstElementChild.innerHTML;
        emailAdminPanel = item.querySelector('.user-info').lastElementChild.innerHTML;
        if (numberAdminPanel === data[0].userNumber && emailAdminPanel === data[0].userEmail) {
            userExists = true;
        }
    })
    if (!userExists) {
        data.forEach((item) => {
            let userConnection = $.createElement('div');
            userConnection.onclick = userSelection;
            userConnection.setAttribute('class', 'user');
            userConnection.innerHTML = `
                <div class="user-pic">
                    <img src="../../static/home/img/man.png" alt="">
                </div>
                <div class="user-info">
                    <div class="user-number">${item.userNumber}</div>
                    <div class="user-email">${item.userEmail}</div>
                </div>
                <div class="icon"></div>`
            customers.insertAdjacentElement('afterbegin', userConnection)
            scroll3()
        })
    }

}


// get All admin connections
let getAllAdminConnections = (company) => {
    fetch('/all-admin-connections/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFtoken': csrftoken2,
        },
        body: JSON.stringify({company: company}),
    })
        .then(res => res.json())
        .then(data => {
            // console.log(data);
            if (data.length > 0) {
                console.log(data);
                allConnectionTemplateCreator(data)
            }
        });
}
// connection = Connection.objects.filter(admin=request.user.name)
// let getAdminConnections = (company) => {
//     fetch('http://localhost:8000/admin-connections/?company=${company}', {
//         method: 'GET',
//     })
//         .then(res => res.json())
//         .then(data => {
//             console.log(company);
//             if (data.length > 0) {
//
//                 connectionTemplateCreator(data)
//             }
//         })
// }


// get message from admin to admin
let getAdminMessagesAdmin = () => {
    if (JSON.parse(localStorage.getItem('admin'))) {
        fetch('/admin-message-admin/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFtoken': csrftoken2,
            },
            body: JSON.stringify({msg_sender: userEmailAdmin, msg_sender_number: userNumberAdmin}),
        })
            .then(res => res.json())
            .then(data => {
                console.log(data);
                if (data.length > 0) {
                    setTimeout(function () {
                        admin3MessageCreator(data)
                    }, 1000)

                    admin3MessageCreator(data)

                }
            })
    }
}


// setTimeout(function () {getAdminMessagesAdmin()}, 1000)
getAdminMessagesAdmin()
// setInterval(getAdminMessagesAdmin, 2000)


textAdmin.disabled = true;

// ---------select company ------
let companySelection = (e) => {
    const companySelectedText = e.currentTarget.textContent.trim();
    company = e.currentTarget.textContent.trim();
    customers.innerHTML = '';
    getAllAdminConnections(companySelectedText);
    setInterval(() => getAdminConnections(companySelectedText), 2000);
}
Array.from(dropdownList.children).forEach((item) => {
    item.addEventListener('click', (e) => {
        companySelection(e)
    })
})
let userSelection = (e) => {
    fileInputMessageAdmin.value = "";
    e.currentTarget.querySelector('.icon').style.visibility = 'hidden';
    textAdmin.disabled = false;
    ffAdmin.style.display = 'flex';
    // e.currentTarget.querySelector('.footer-admin').style.display = 'flex';
    if (window.innerWidth < 1024) {
        rightSide.style.display = 'none';
        leftSide.style.display = 'flex';
    } else {
        rightSide.style.display = 'flex';
        leftSide.style.display = 'flex';
    }
    messageBoxAdmin.innerHTML = '';
    userNumberAdmin = e.currentTarget.querySelector('.user-info').firstElementChild.innerHTML;
    userEmailAdmin = e.currentTarget.querySelector('.user-info').lastElementChild.innerHTML;

    // clearFileInput();
    const fileNameElement = $.getElementById("file-name-message");
    if (fileNameElement) {
        fileNameElement.textContent = "هیچ فایلی انتخاب نشده است";
    }
    fileInputMessageAdmin.addEventListener("change", function () {
        const fileNameElement = $.getElementById("file-name-message");
        if (this.files && this.files[0]) {
            fileNameElement.textContent = "فایل انتخاب شده: " + this.files[0].name;
        } else {
            fileNameElement.textContent = "هیچ فایلی انتخاب نشده است";
        }
    });

    // getUserMessagesAdmin()
    // getAdminMessagesAdmin()

    setInterval(getUserMessagesAdmin, 1000);
    // setInterval(getAdminMessagesAdmin, 1000);
    getAllMessagesAdmin();
    getAPIMessagesAdmin();
}
Array.from(customers.children).forEach((item) => {
    item.addEventListener('click', (e) => {
        userSelection(e)
    })
})



//Connection template creator
let connectionTemplateCreator = (data) => {
    let userExists = false;
    Array.from(customers.children).forEach((item) => {
        numberAdminPanel = item.querySelector('.user-info').firstElementChild.innerHTML;
        emailAdminPanel = item.querySelector('.user-info').lastElementChild.innerHTML;
        if (numberAdminPanel === data[0].userNumber && emailAdminPanel === data[0].userEmail) {
            userExists = true;
        }
    })
    if (!userExists) {
        let userConnection = $.createElement('div');
        userConnection.onclick = userSelection;
        userConnection.setAttribute('class', 'user');
        userConnection.innerHTML = `
                <div class="user-pic">
                    <img src="../../static/home/img/man.png" alt="">
                </div>
                <div class="user-info">
                    <div class="user-number">${data[0].userNumber}</div>
                    <div class="user-email">${data[0].userEmail}</div>
                </div>
                <div class="icon"></div>`
        customers.insertAdjacentElement('afterbegin', userConnection)
        scroll3()
    }

}


// // new message check
// let newMessageAdmin = () => {
//     Array.from(customers.children).forEach((item) => {
//         numberAdminPanel = item.querySelector('.user-info').firstElementChild.innerHTML;
//         emailAdminPanel = item.querySelector('.user-info').lastElementChild.innerHTML;
//
//         fetch('http://localhost:8000/new-message/', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//                 'X-CSRFToken': csrftoken2,
//             },
//             body: JSON.stringify({msg_sender2: emailAdminPanel, msg_sender_number2: numberAdminPanel}),
//         })
//             .then(res => res.json())
//             .then(data => {
//                 // console.log(data.message2);
//                 // print(data.messages)
//                 if (data.message2 === 'true') {
//                     item.querySelector('.icon').style.visibility = 'visible';
//                 } else {
//                     item.querySelector('.icon').style.visibility = 'hidden';
//                 }
//             })
//     })
//
// }
// setInterval(newMessageAdmin, 2000);

function copyApiKey() {
    const apiKey = document.querySelector('.api-key-box span').textContent;
    navigator.clipboard.writeText(apiKey).then(() => {
        alert('کپی شد!');
    });
}

//
// const toggleButton = document.getElementById('toggleMenu');
// const menu = document.getElementById('menu');
// const overlay = document.getElementById('overlay');
//
// toggleButton.addEventListener('click', () => {
//     menu.classList.toggle('visible');
//     overlay.classList.toggle('visible');
// });
//
// // وقتی روی هاله کلیک شد، منو و هاله مخفی شوند
// overlay.addEventListener('click', () => {
//     menu.classList.remove('visible');
//     overlay.classList.remove('visible');
// });
//
// // تنظیمات اولیه هنگام بارگذاری صفحه
// function updateMenuVisibility() {
//     if (window.innerWidth > 768) {
//         menu.classList.remove('menu-float', 'visible');
//         overlay.classList.remove('visible');
//     } else {
//         menu.classList.add('menu-float');
//         menu.classList.remove('visible');
//         overlay.classList.remove('visible');
//     }
// }
//
// // تغییر وضعیت منو هنگام تغییر اندازه صفحه
// window.addEventListener('resize', updateMenuVisibility);
//
// // تنظیم اولیه هنگام بارگذاری صفحه
// updateMenuVisibility();

