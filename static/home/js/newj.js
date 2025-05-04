function initializeChatWidget(API_KEY, BUTTON_IMAGE_URL, HEADER_IMAGE_URL) {
    // تنظیم URL API و API Key شرکت
    const baseURL = "https://whotalk.app/api"; // آدرس سرور شما

    const widgetStyles = `
        @font-face {
            font-family: Yekan Bakh FaNum;
            font-style: normal;
            font-weight: normal;
            font-stretch: normal;
            src: url('https://whotalk.app/static/fonts/woff/YekanBakhFaNum-Regular.woff') format('woff');
        }
        
        @font-face {
            font-family: Yekan Bakh FaNum;
            font-style: normal;
            font-weight: bold;
            font-stretch: normal;
            src: url('https://whotalk.app/static/fonts/woff/YekanBakhFaNum-Bold.woff') format('woff');
        }
        
        @font-face {
            font-family: Yekan Bakh FaNum;
            font-style: normal;
            font-weight: 100;
            font-stretch: normal;
            src: url('https://whotalk.app/static/fonts/woff/YekanBakhFaNum-Thin.woff') format('woff');
        }

        .chat-modal-button {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 60px;
            height: 60px;
            background: url("${BUTTON_IMAGE_URL}");
            background-size: 100%;
            background-position: center;
            background-repeat: no-repeat;
            visibility: visible;
            animation: float 3s ease-out infinite;
            z-index: 499;
        }
        
        @keyframes float {
            50% {
                transform: translate(0, 10px);
            }
        }
        
        .chat-modal-button:hover {
            cursor: pointer;
        }
        
        .chat-user-parent {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 380px;
            height: 75%;
            border-radius: 25px;
            overflow: hidden;
            /*animation: chatUserBoxShow .3s ease-in-out;*/
            border: 1px solid #6B42C6;
            display: none;
            animation: myAnim 1s ease-in-out 0s 1 normal forwards;
            z-index: 500;
            font-family: "Yekan Bakh FaNum";
            direction:rtl;
        }
        
        @keyframes myAnim {
            0% {
                transform: scaleY(0.4);
                transform-origin: 0% 100%;
            }
        
            100% {
                transform: scaleY(1);
                transform-origin: 0% 100%;
            }
        }
        
        .chat-user-parent.show {
            display: block !important;
        }
        
        
        .chat-user-parent.hide {
            animation: myAnimOut 1s ease 0s 1 normal forwards;
        
        }
        
        @keyframes myAnimOut {
            0% {
                transform: scaleY(1);
                transform-origin: 0% 100%;
            }
        
            100% {
                transform: scaleY(0);
                transform-origin: 0% 100%;
            }
        }

        /* استایل چت‌بات */
        .chat-user-parent .chat-user {
            position: relative;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: white;
            display: flex;
            flex-direction: column;
        }
        
        .chat-user-parent .chat-user .chat-user-header {
            position: relative;
            top: 0;
            left: 0;
            width: 100%;
            height: 8%;
            min-height: 60px; 
            background-color: #6B42C6;
            display: flex;
            flex-direction: row;
            align-items: center;
            justify-content: space-between;
            padding: 5px 5px;
            font-family: "Yekan Bakh FaNum";
            direction: rtl;
        }
        
        .chat-user-parent .chat-user .chat-user-header .close-button {
            margin-left: 15px;
            margin-right: 15px;
            font-size: 30px;
            color: white;
            font-weight: normal;
            line-height: 1;
            

        }
        
        .chat-user-parent .chat-user .chat-user-header .close-button:hover {
            cursor: pointer;
        }
        
        .chat-user-parent .chat-user .chat-user-header p {
            font-size: 12px;
            color: white;
            margin: 0;
            padding: 0 10px;
            line-height: 1.4;
            flex-grow: 1;
            text-align: center;
        }
        
        .chat-user-parent .chat-user .chat-user-header span {
            font-size: 10px;
            color: white;
            direction: rtl;
        }
        
        .chat-user-parent .chat-user .chat-user-header .consultant {
            position: relative;
            width: 40px;
            height: 50px;
            display: flex;
        }
        
        .chat-user-parent .chat-user .chat-user-header .consultant .admin {
            position: relative;
            top: 0;
            left: 0;
            width: 80px;
            height: 80px;
            display: flex;
            border-radius: 20px;
            direction: rtl;
        }
        
        .chat-user-parent .chat-user .chat-user-header .consultant .admin img {
            position: relative;
            top: 0;
            right: 0;
            width: 50px;
            height: 50px;
        }
        
        .chat-user-parent .chat-user .chat-user-header .consultant .admin img:hover {
        }
        
        .chat-user-parent .chat-user .chat-user-body {
            position: relative;
            top: 0;
            left: 0;
            width: 100%;
            margin-top: 5px;
            height: calc(100% - 210px);
            /*background-color: white;*/
            background: rgba(255, 255, 255, 0.62);
            backdrop-filter: blur(11.7px);
            -webkit-backdrop-filter: blur(11.7px);
            overflow-y: auto;
            overflow-x: hidden;
        }
        
        .chat-user-parent .faq-section {
            position: relative; /* تغییر از absolute به relative */
            bottom: 0; /* فاصله از پایین را حذف کنید */
            left: 0;
            right: 0;
            padding: 10px 0;
            background-color: #fff;
            overflow-x: auto;
            white-space: nowrap;
            z-index: 2; /* در صورت نیاز به نمایش اولویت */
            flex-shrink: 0; /* جلوگیری از تغییر اندازه */
            display: none;
            font-family: "Yekan Bakh FaNum";
        }
        
        .chat-user-parent .faq-container {
            display: flex;
            gap: 10px; /* فاصله بین باکس‌ها */
            padding: 0 10px;
        }
        
        .chat-user-parent .faq-box {
            display: inline-block;
            min-width: 150px; /* عرض حداقل هر باکس */
            padding: 10px;
            background-color: #ffffff;
            border: 1px solid #FFC450;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
            cursor: pointer;
            transition: transform 0.2s ease-in-out;
            font-size: 11px;
        }
        
        .chat-user-parent .faq-box:hover {
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
        }
        
        .chat-user-parent .chat-user .chat-user-footer {
            position: relative;
            box-sizing: border-box;
            width: 95%;
            height: 132px;
            display: none;
            flex-direction: column;
            justify-content: space-between;
            align-items: center;
            flex-shrink: 0;
            border: 1px solid #FFC450;
            border-radius: 15px;
            background-color: #efeff0;
            margin: 10px auto 10px auto;
            font-family: "Yekan Bakh FaNum";
        }
        
        .chat-user-parent .chat-user .chat-user-footer .textarea {
            position: relative;
            top: -5px;
            left: 0;
            /*width: 62%;*/
            width: 100%;
            /*height: 100%;*/
            /*margin-right: 40px;*/
            margin-right: 30px;
            margin-left: 30px;
            margin-top: 5px;
            margin-bottom: 35px;
        }
        
        .chat-user-parent .chat-user .chat-user-footer .textarea textarea {
            position: relative;
            top: 0;
            left: 0;
            width: 100%;
            resize: none;
            border: none;
            border-radius: 15px;
            outline: none;
            font-size: 12px;
            font-family: Yekan Bakh FaNum;
            direction: rtl;
            padding: 10px;
            box-sizing: border-box;
            background-color: #efeff0;
        }
        
        .chat-user-parent .chat-user .chat-user-footer .textarea textarea[disabled] {
            opacity: 0.5;
            cursor: not-allowed;
            color: #a9a9a9;
        }
        
        .chat-user-parent .chat-user .chat-user-footer .footer-actions {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .chat-user-parent .chat-user .chat-user-footer .footer-actions .send-message {
            position: absolute;
            top: 61%;
            left: 10px;
            display: flex;
            font-size: 0.55em;
            line-height: 1;
            z-index: 1;
            height: 30%;
            margin-bottom: 20px;
            color: #FFC450;
            border-radius: 50%;
            transition: background .3s;
            direction: rtl;
        
            &:hover,
            &:focus {
            }
        
            &:active {
            }
        }
        
        .chat-user-parent .chat-user .chat-user-footer .footer-actions .send-message[disabled] {
            opacity: 0.5;
            cursor: not-allowed;
            pointer-events: none;
            background-color: #ccc;
        }
        
        .chat-user-parent .chat-user .chat-user-footer .footer-actions .send-message svg {
            margin-top: 10px;
        }
        
        .chat-user-parent .chat-user .chat-user-footer .footer-actions .send-message svg:hover {
            cursor: pointer;
        }
        
        .chat-user-parent .chat-user .chat-user-footer .footer-actions .send-message:hover svg {
        }
        
        .chat-user-parent .chat-user .chat-user-footer .footer-actions .file-upload input[type="file"] {
            font-family: Yekan Bakh FaNum;
            direction: rtl;
            margin-top: -100px;
            opacity: 0;
            height: 1px;
            width: 1px;
            z-index: -1;
            display: none;
        }
        
        .chat-user-parent .chat-user .chat-user-footer .footer-actions .file-upload .custom-file-upload-user {
            position: absolute;
            top: 67%;
            right: 10px;
        }
        
        .chat-user-parent .chat-user .chat-user-footer .footer-actions .file-upload .custom-file-upload-user svg {
            margin-top: 7px;
        }
        
        .chat-user-parent .chat-user .chat-user-footer .footer-actions .file-upload .custom-file-upload-user:hover {
            border-radius: 5px;
            cursor: pointer;
        }
        
        .chat-user-parent .chat-user .chat-user-footer .footer-actions .file-name-message-user {
            position: absolute;
            top: 77%;
            right: 33px;
            color: gray;
            font-size: 8px;
            direction:rtl;
        }
        
        .chat-user-parent .user-info {
            position: absolute;
            bottom: 10px;
            left: 50%;
            transform: translateX(-50%);
            width: 97%;
            background: rgb(230, 230, 250);
            background: linear-gradient(180deg, rgba(230, 230, 250, 1) 1%, rgba(230, 230, 250, 1) 14%, rgba(230, 230, 250, 1) 29%, rgba(230, 230, 250, 1) 59%, rgba(0, 212, 255, 0) 100%);
            margin: auto;
            direction: rtl;
            overflow: hidden;
            margin-right: 10px;
            margin-bottom: 5px;
            border-radius: 15px;
            padding: 15px;
            font-size: 11px;
            border: 1px solid #e6e6fa;
            display = "block";
            color: black;
        }
        
        .chat-user-parent .user-info p {
            text-align: right;
            font-family: 'Yekan Bakh FaNum';
            font-size: 14px;
        }
        
        .chat-user-parent .user-info .textin {
            text-align: center;
            box-sizing: border-box;
        }
        
        .chat-user-parent .user-info input {
            font-family: Yekan Bakh FaNum;
            box-sizing: border-box;
            width: 99%;
            height: 30px;
            border-radius: 5px;
            outline: none;
            border: none;
            padding: 7px 5px;
        
        }
        
        .chat-user-parent .user-info button {
            font-family: Yekan Bakh FaNum;
            direction: rtl;
            outline: none;
            border: 1px solid #6B42C6;
            width: 100%;
            color: white;
            background-color: #6B42C6;
            margin-top: 10px;
            padding: 2px 4px;
            border-radius: 5px;
            height: 30px;
            font-size: 11px;
        }
        
        .chat-user-parent .user-info button:hover {
            cursor: pointer;
            background-color: rgba(107, 66, 198, 0.2);
            color: #6B42C6;
        }
        
        .chat-user-parent .sent-chat-box-parent {
            margin-right: 10px;
        
        }
        
        .chat-user-parent .chat-user .chat-user-body .sent-chat-box-parent {
            margin-right: 10px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        @keyframes messageAnimation {
            0% {
                transform: scale(1.1);
            }
        }
        
        .chat-user-parent .chat-user .chat-user-body .sent-chat-box-parent .sent-chat-box {
            position: relative;
            font-family: 'Yekan Bakh FaNum';
            display: flex;
            flex-direction: column;
        }
        
        .chat-user-parent .chat-user .chat-user-body .sent-chat-box-parent .sent-chat-box .time-sent {
            margin-top: 2px;
            font-size: 12px;
        }
        
        .chat-user-parent .chat-user .chat-user-body .sent-chat-box-parent .sent-chat-box .attached-file-admin {
            font-size: 10px;
            margin-top: 0;
        }
        
        .chat-user-parent .chat-user .chat-user-body .sent-chat-box-parent .sent-chat-box .file-name-dl {
            font-size: 10px;
            margin-top: 0;
        }
        
        .chat-user-parent .chat-user .chat-user-body .sent-chat-box-parent .sent-chat-box .file-name-dl a {
            color: #FFC450;
            text-decoration: none;
        }
        
        .chat-user-parent .chat-user .chat-user-body .sent-chat-box-parent .sent-chat-box .footer-detail {
            display: flex;
            justify-content: flex-start;
            align-items: center;
            margin-top: 0px;
            gap: 5px;
            direction: rtl;
        }
        
        .chat-user-parent .chat-user .chat-user-body .sent-chat-box-parent .sent-chat-box .header {
            position: relative;
            top: 0;
            left: 0;
            width: 100%;
            height: 30px;
            background-color: #FDEBD0;
            display: flex;
            align-items: center;
            justify-content: right;
            font-size: 11px;
        }
        
        .chat-user-parent .chat-user .chat-user-body .sent-chat-box-parent .sent-chat-box .header p {
            margin: 0 10px;
            text-align: right;
        }
        
        .chat-user-parent .chat-user .chat-user-body .sent-chat-box-parent .sent-chat-box .body {
            position: relative;
            width: auto;
            height: auto;
            background-color: #FFC450;
            color: black;
            font-size: 11px;
            word-wrap: break-word;
            word-break: break-word;
            box-sizing: border-box;
            max-width: 200px;
            min-width: 100px;
            margin-top: 10px;
            margin-left: auto;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            padding: 12px;
            direction: rtl;
            border-top-left-radius: 15px;
            border-bottom-left-radius: 15px;
            border-top-right-radius: 15px;
            text-align: right;
            font-family: 'Yekan Bakh FaNum';
            animation: messageAnimation .2s ease-in-out;
        }
        
        .chat-user-parent .chat-user .chat-user-body .sent-chat-box-parent .sent-chat-box .body p {
            margin: auto;
            margin-right: 0;
            font-size: 12px;
        }
        
        .chat-user-parent .chat-user .chat-user-body .received-chat-box-parent {
            position: relative;
            width: auto;
            height: auto;
            margin-top: 10px;
            margin-left: 10px;
            margin-right: auto;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-sizing: border-box;
            font-family: 'Yekan Bakh FaNum', sans-serif;
            direction: rtl;
        }
        
        .chat-user-parent .chat-user .chat-user-body .received-chat-box-parent .received-chat-box .body {
            position: relative;
            width: 100%;
            margin-right: auto;
            border: 3px solid #6B42C6;
            color: #6B42C6;
            font-size: 11px;
            max-width: 200px;
            min-width: 100px;
            word-wrap: break-word;
            word-break: break-word;
            box-sizing: border-box;
            padding: 10px;
            direction: rtl;
            display: flex;
            border-top-left-radius: 15px;
            border-bottom-right-radius: 15px;
            border-top-right-radius: 15px;
            text-align: right;
            animation: messageAnimation .2s ease-in-out;
        }
        
        .chat-user-parent .chat-user .chat-user-body .received-chat-box-parent .received-chat-box .body p {
            margin: auto;
            margin-right: 0;
            font-size: 12px;
        }
        .chat-user-parent .chat-user .chat-user-body .received-chat-box-parent .received-chat-box .body .typing-received {
            margin: auto;
            margin-right: 0;
            color: #6B42C6;
            white-space: pre-wrap;
        }
        
        .chat-user-parent .chat-user .chat-user-body .received-chat-box-parent .header {
            position: relative;
            /*top: 0;*/
            /*left: 0;*/
            /*width: 100%;*/
            /*height: 30px;*/
            color: #6B42C6;
            display: flex;
            align-items: center;
            justify-content: left;
            font-family: 'Yekan Bakh FaNum';
            font-size: 11px;
            margin-left: 10px;
        }
        
        .chat-user-parent .chat-user .chat-user-body .received-chat-box-parent .header p {
            position: absolute;
            top: 3px;
            left: 26px;
            margin-bottom: 5px;
            margin-left: -5px;
            font-size: 11px;
            direction: rtl;
            justify-content: left;
        }
        
        .chat-user-parent .chat-user .chat-user-body .received-chat-box-parent .received-chat-box .footer-detail {
            position: relative;
            margin-right: auto;
            text-align: left;
            margin-top: 2px;
        }
        
        .chat-user-parent .chat-user .chat-user-body .received-chat-box-parent .received-chat-box .footer-detail .time-received {
            position: relative;
            display: inline-block;
            vertical-align: middle;
            font-size: 12px;
            margin-top: 0px;
        }
        
        
        .chat-user-parent .chat-user .chat-user-body .received-chat-box-parent .received-chat-box .footer-detail .attached-file-admin {
            vertical-align: middle;
            display: inline-block;
            font-size: 10px;
            margin-top: 0px;
            position: relative;        
        }
        
        .chat-user-parent .chat-user .chat-user-body .received-chat-box-parent .received-chat-box .footer-detail .file-name-dl {
            vertical-align: middle;
            display: inline-block;
            font-size: 10px;
            margin-top: -3px;
            position: relative;
        }
        
        .chat-user-parent .chat-user .chat-user-body .received-chat-box-parent .received-chat-box .footer-detail .file-name-dl a {
            color: #6B42C6;
            text-decoration: none;
        }
        
        
        .chat-user-parent .chat-user .chat-user-body .received-chat-box-parent .header .admin-pic {
            position: relative;
            width: 25px;
            height: 25px;
            border-radius: 100%;
            overflow: hidden;
            margin-left: -10px;
            margin-right: auto;
            margin-bottom: 5px;
        }
        
        .chat-user-parent .chat-user .chat-user-body .received-chat-box-parent .header .admin-pic img {
            position: relative;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
        }
        
        .send-in {
        }
        
        #loading-indicator {
            position: relative;
            bottom: 5px;
            left: 50%;
            transform: translateX(-50%);
            color: #FFC450;
            font-size: 10px;
            text-align: center;
            z-index: 1000;
            font-family: 'Yekan Bakh FaNum';
            direction: rtl;
        }
        
        .swiper-container {
            margin-top: 70px;
            width: 100%;
            height: 150px;
            overflow: hidden;
            direction: ltr;
        }
        
        .swiper-wrapper {
            display: flex;
        }
        
        .swiper-slide {
            display: flex;
            justify-content: center;
            align-items: center;
            width: auto;
        }
        
        .swiper-slide img {
            max-height: 100px;
            max-width: 100%;
            object-fit: contain;
        }
        
        /*------*/
        @media (max-width: 768px) {
            .chat-user-parent {
                width: 100%;
                height: 100%;
                bottom: 0;
                right: 0;
                border-radius: 0;
                border: none;
                z-index: 600;
            }
        
            .chat-user-parent .chat-user-body .user-info {
                bottom: 0;
                width: 95%;
                height: 120px;
                padding: 15px;
                font-size: 11px;
                border: 1px solid #FDEBD0;
            }
        
            .chat-modal-button {
                z-index: 599;
            }
        }
        
        @media (max-width: 425px) {
            .chat-user-parent {
                width: 100%;
                height: 100%;
                bottom: 0;
                right: 0;
                border-radius: 0;
                border: none;
            }
        
            .chat-user-parent .chat-user-body .user-info {
                bottom: 0;
                width: 82%;
                height: 120px;
                padding: 15px;
                font-size: 11px;
                border: 1px solid #FDEBD0;
              
            }
        
        }
    `;

    // اضافه کردن استایل‌ها
    const styleTag = document.createElement("style");
    styleTag.innerHTML = widgetStyles;
    document.head.appendChild(styleTag);


    // ساختن ساختار چت‌بات
    const chatWidget = document.createElement("div");
    chatWidget.className = "chat-widget";
    chatWidget.innerHTML = `
    <div class="chat-modal-button"></div>

    <div class="chat-user-parent">
        <div class="chat-user">
            <div class="chat-user-header">

                <div class="consultant">
                    <div class="admin">
                        <img src="${HEADER_IMAGE_URL}" alt="">
                    </div>
                </div>
                <p class="isTyping">پشتیبانی سایت<span class="indicator"></span>
                </p>
                <span class="close-button">&times;</span>
            </div>

            <div class="chat-user-body">


            </div>
            <div class="send-in"></div>
            <div class="user-info">
                <p>برای شروع شماره خود را وارد نمایید:</p>
                <div class="textin">
                    <input id="number-send-info" class="number" type="text" placeholder="شماره تماس">
                    <button class="send-info-button">شروع گفتگو</button>
                </div>
            </div>
            <div class="chat-user-footer">
                <div class="textarea">
                    <textarea class="text-type" placeholder="اینجا تایپ کنید ..."></textarea>
                </div>
                <div class="footer-actions">
                    <div class="file-upload">
                        <label for="fileInput-user" class="custom-file-upload-user">
                            <svg width="20px" height="20px" viewBox="0 0 24 24" fill="none"
                                 xmlns="http://www.w3.org/2000/svg">
                                <path fill-rule="evenodd" clip-rule="evenodd"
                                      d="M9 7C9 4.23858 11.2386 2 14 2C16.7614 2 19 4.23858 19 7V15C19 18.866 15.866 22 12 22C8.13401 22 5 18.866 5 15V9C5 8.44772 5.44772 8 6 8C6.55228 8 7 8.44772 7 9V15C7 17.7614 9.23858 20 12 20C14.7614 20 17 17.7614 17 15V7C17 5.34315 15.6569 4 14 4C12.3431 4 11 5.34315 11 7V15C11 15.5523 11.4477 16 12 16C12.5523 16 13 15.5523 13 15V9C13 8.44772 13.4477 8 14 8C14.5523 8 15 8.44772 15 9V15C15 16.6569 13.6569 18 12 18C10.3431 18 9 16.6569 9 15V7Z"
                                      fill="currentColor"></path>
                            </svg>
                        </label>
                        <input type="file" name="fileInput-user" id="fileInput-user" accept="*/*">
                    </div>
                    <span id="file-name-message-user" class="file-name-message-user">هیچ فایلی انتخاب نشده است</span>
                    <div class="send-message">
                        <svg fill="#000000" width="24px" height="24px" viewBox="0 0 512 512" data-name="Layer 1"
                             id="Layer_1" xmlns="http://www.w3.org/2000/svg">
                            <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                            <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
                            <g id="SVGRepo_iconCarrier" transform="rotate(270, 256, 256)">
                                <path d="M460.54,169.58A222.6,222.6,0,1,0,478,256,221.16,221.16,0,0,0,460.54,169.58ZM256,448C150,448,64,362,64,256S150,64,256,64s192,86,192,192S362,448,256,448Zm28.06-307.33L399.39,256,284.06,371.33l-21.21-21.21L342,271H133.82V241H342l-79.12-79.12Z"></path>
                            </g>
                        </svg>
                    </div>
                </div>
            </div>
        </div>

    </div>
    `;
    document.body.appendChild(chatWidget);
    const $ = document;
    const chatModalButton = $.querySelector('.chat-modal-button'),
        chatUserParent = $.querySelector('.chat-user-parent'),
        closeButton = $.querySelector('.close-button'),
        NumberSendInfo = $.querySelector('#number-send-info'),
        fileInputMessageUser = $.querySelector('#fileInput-user'),
        // faqSection = $.querySelector('.faq-section'),
        sendMessage = $.querySelector('.send-message');


    let number = $.querySelector('.number'),
        sendInfoButton = $.querySelector('.send-info-button'),
        userInfo = $.querySelector('.user-info'),
        chatUserFooter = $.querySelector('.chat-user-footer'),
        textType = $.querySelector('.text-type'),
        sendIN = $.querySelector('.send-in'),
        chatUserBody = $.querySelector('.chat-user-body');


    // const getUserIP = async () => {
    //     return new Promise((resolve, reject) => {
    //         const peerConnection = new RTCPeerConnection({
    //             iceServers: [{urls: "stun:stun.l.google.com:19302"}],
    //         });
    //
    //         peerConnection.createDataChannel("");
    //
    //         peerConnection.createOffer()
    //             .then((offer) => peerConnection.setLocalDescription(offer))
    //             .catch((error) => {
    //                 console.error("Failed to create offer:", error);
    //                 reject("Failed to create offer");
    //             });
    //
    //         peerConnection.onicecandidate = (event) => {
    //             if (event && event.candidate) {
    //                 const candidate = event.candidate.candidate;
    //                 const ipMatch = candidate.match(
    //                     /([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})/
    //                 );
    //                 if (ipMatch) {
    //                     const ipAddress = ipMatch[1];
    //                     peerConnection.close();
    //                     resolve(ipAddress);
    //                 }
    //             } else if (!event.candidate) {
    //                 peerConnection.close();
    //                 reject("No ICE candidate found");
    //             }
    //         };
    //     });
    // };
    const getPublicIP = async () => {
        try {
            const response = await fetch("https://ipinfo.io/json");
            const data = await response.json();
            console.log("Received IP Data:", data); // ببین چه چیزی برمی‌گردونه
            return data.ip;
        } catch (error) {
            console.error("Error fetching IP:", error);
            return null;
        }
    };

    const getUserIP = async () => {
        try {
            return await getPublicIP(); // ابتدا از API استفاده می‌کنیم
        } catch {
            return new Promise((resolve, reject) => {
                const peerConnection = new RTCPeerConnection({
                    iceServers: [{urls: "stun:stun.l.google.com:19302"}],
                });

                peerConnection.createDataChannel("");
                peerConnection.createOffer()
                    .then((offer) => peerConnection.setLocalDescription(offer))
                    .catch(() => reject("Failed to create offer"));

                peerConnection.onicecandidate = (event) => {
                    if (event && event.candidate) {
                        const candidate = event.candidate.candidate;
                        const ipMatch = candidate.match(/([0-9a-fA-F:.]+)/);
                        if (ipMatch) {
                            const ipAddress = ipMatch[1];
                            peerConnection.close();
                            resolve(ipAddress);
                        }
                    } else if (!event.candidate) {
                        peerConnection.close();
                        reject("No ICE candidate found");
                    }
                };
            });
        }
    };


    const storeUserIP = async () => {
        try {
            const userIP = await getUserIP();
            localStorage.setItem("userIP", userIP);
        } catch (error) {
        }
    };
    document.addEventListener("DOMContentLoaded", function () {
        const storedNumber = localStorage.getItem("userMobile");
        const storedIP = localStorage.getItem("userIP");

        if (storedNumber && storedIP) {
            // شماره تلفن و IP ذخیره شده است
            userMobile = storedNumber;
            userIP = storedIP;

            // حذف فرم اطلاعات کاربر و نمایش چت
            userInfo.remove();
            // userInfo.style.display = "none";
            chatUserFooter.style.display = "flex";
            fetchAndDisplayMessages(true);
            // faqSection.style.display = "flex";

            // نمایش پیام‌های قبلی

        } else {
            // اگر اطلاعات ذخیره نشده باشد، فرم نمایش داده می‌شود
            chatUserBody.innerHTML = "";
            userInfo.style.display = "block";
            chatUserFooter.style.display = "none";

            // faqSection.style.display = "none";
        }
    });
    const handleSaveNumber = async () => {
        let number = convertToEnglishNumbers(NumberSendInfo.value.trim());
        if (number.match('^(\\+98|0)?9\\d{9}$')) {
            storeNumber(number);

            userInfo.remove();
            // userInfo.style.display = "none";
            chatUserFooter.style.display = 'flex';
            await fetchAndDisplayMessages(true);
            // faqSection.style.display = 'flex';

        } else {
            alert("لطفاً شماره موبایل را به درستی وارد کنید.");
        }
    };

    chatModalButton.addEventListener('click', () => {
        chatUserParent.classList.remove('hide');
        chatUserParent.style.display = 'block';
        chatUserParent.classList.add('show');
        const storedNumber = localStorage.getItem("userMobile");
        const storedIP = localStorage.getItem("userIP");
        if (storedNumber && storedIP) {
            userMobile = storedNumber;
            userIP = storedIP;
            userInfo.remove();
            // userInfo.style.display = "none";
            chatUserFooter.style.display = "flex";
            fetchAndDisplayMessages(false);
            // faqSection.style.display = "flex";
        } else {
            userInfo.style.display = "block";
            chatUserFooter.style.display = "none";
            // faqSection.style.display = "none";
        }

        chatUserParent.classList.remove('hide');
        chatUserParent.style.display = 'block';
        chatUserParent.classList.add('show');

        if (!localStorage.getItem("userIP")) {
            storeUserIP();
        }
    });

    closeButton.addEventListener('click', () => {
        chatUserParent.classList.remove('show');
        chatUserParent.classList.add('hide');


        chatUserParent.addEventListener(
            'animationend',
            () => {
                if (chatUserParent.classList.contains('hide')) {
                    chatUserParent.style.display = 'none';
                }
            },
            {once: true}
        );
    });


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


    const chatBody = document.getElementById("chat-body");
    const chatInput = document.getElementById("chat-input");
    const sendMessageButton = document.getElementById("send-message");

    function convertToEnglishNumbers(input) {
        return input.replace(/[\u06F0-\u06F9]/g, (digit) => {
            return String.fromCharCode(digit.charCodeAt(0) - 0x06F0 + 48);
        }).replace(/[\u0660-\u0669]/g, (digit) => {
            return String.fromCharCode(digit.charCodeAt(0) - 0x0660 + 48);
        });
    }

    const checkStoredData = () => {
        const storedNumber = localStorage.getItem("userMobile");
        const storedIP = localStorage.getItem("userIP");

        if (storedNumber && storedIP) {
            userMobile = storedNumber;
            userIP = storedIP;
            return true;
        }
        return false;
    };

    const addMessageToChat = (message, tag) => {
        const messageElement = document.createElement("div");
        messageElement.className = `${tag === "sent" ? "sent-chat-box-parent" : "received-chat-box-parent"}`;
        const svgIcon = tag === "sent" ? `
        <svg width="12px" height="12px" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"
             fill="#000000" transform="matrix(-1, 0, 0, 1, 0, 0)">
            <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
            <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
            <g id="SVGRepo_iconCarrier">
                <path d="M7.44 15.44a1.5 1.5 0 0 0 2.115 2.125L20.111 7.131a3 3 0 1 0-4.223-4.262L4.332 14.304a4.5 4.5 0 1 0 6.364 6.363l8.98-9.079.712.703-8.981 9.08a5.5 5.5 0 1 1-7.779-7.777L15.185 2.159a4 4 0 1 1 5.63 5.683L10.259 18.276a2.5 2.5 0 0 1-3.527-3.544l8-8 .707.707z"></path>
                <path fill="none" d="M0 0h24v24H0z"></path>
            </g>
        </svg>` : `
        <svg width="12px" height="12px" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"
             fill="#000000" transform="matrix(-1, 0, 0, 1, 0, 0)">
            <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
            <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
            <g id="SVGRepo_iconCarrier">
                <path d="M7.44 15.44a1.5 1.5 0 0 0 2.115 2.125L20.111 7.131a3 3 0 1 0-4.223-4.262L4.332 14.304a4.5 4.5 0 1 0 6.364 6.363l8.98-9.079.712.703-8.981 9.08a5.5 5.5 0 1 1-7.779-7.777L15.185 2.159a4 4 0 1 1 5.63 5.683L10.259 18.276a2.5 2.5 0 0 1-3.527-3.544l8-8 .707.707z"></path>
                <path fill="none" d="M0 0h24v24H0z"></path>
            </g>
        </svg>`;

        // ساختار داخلی پیام
        messageElement.innerHTML = `
        <div class="${tag === "sent" ? "sent-chat-box" : "received-chat-box"}">
            ${tag === "received" ? `
            <div class="header">
                <span>
                    <p>ربات پشتیبانی ${message.company}</p>
                    <div class="admin-pic">
                        <img src="https://whotalk.app${message.msgImg || ''}" alt="Admin">
                    </div>
                </span>
            </div>` : ""}
            <div class="body">
                <p>${message.text}</p>
            </div>
            <div class="footer-detail">
                <p class="time-${tag}">${new Date(message.create).toLocaleTimeString("fa-IR")}</p>
                ${message.msgFile ? `<p class="attached-file-admin">
                    ${svgIcon}
                </p><p class="file-name-dl"><a href="https://whotalk.app${message.msgFile}" target="_blank"> فایل ضمیمه شده</a></p>` : ""}
            </div>
        </div>
    `;


        // اضافه کردن پیام به چت
        chatUserBody.appendChild(messageElement);
        chatUserBody.scrollTop = chatUserBody.scrollHeight;
    };

    function addMessageToChatWithTypingAnimation(message) {
        const messageElement = document.createElement("div");
        messageElement.className = "received-chat-box-parent";

        messageElement.innerHTML = `
        <div class="received-chat-box">
            <div class="header">
                <span>
                    <p>ربات پشتیبانی ${message.company}</p>
                    <div class="admin-pic">
                        <img src="https://whotalk.app${message.msgImg || ''}" alt="Admin">
                    </div>
                </span>
            </div>
            <div class="body">
                <p class="typing-received"></p>
            </div>
            <div class="footer-detail">
                <p class="time-received">${new Date(message.create).toLocaleTimeString("fa-IR")}</p>
                ${message.msgFile ? `<p class="attached-file-admin">
                    <svg width="12px" height="12px" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"
                         fill="#000000" transform="matrix(-1, 0, 0, 1, 0, 0)">
                        <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                        <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
                        <g id="SVGRepo_iconCarrier">
                            <path d="M7.44 15.44a1.5 1.5 0 0 0 2.115 2.125L20.111 7.131a3 3 0 1 0-4.223-4.262L4.332 14.304a4.5 4.5 0 1 0 6.364 6.363l8.98-9.079.712.703-8.981 9.08a5.5 5.5 0 1 1-7.779-7.777L15.185 2.159a4 4 0 1 1 5.63 5.683L10.259 18.276a2.5 2.5 0 0 1-3.527-3.544l8-8 .707.707z"></path>
                            <path fill="none" d="M0 0h24v24H0z"></path>
                        </g>
                    </svg>
                </p><p class="file-name-dl"><a href="${message.msgFile}" target="_blank"> فایل ضمیمه شده</a></p>` : ""}
            </div>
        </div>
    `;

        chatUserBody.appendChild(messageElement);
        chatUserBody.scrollTop = chatUserBody.scrollHeight;

        const textElement = messageElement.querySelector(".typing-received");
        const text = message.text;
        let charIndex = 0;

        const typeInterval = setInterval(() => {
            if (charIndex < text.length) {
                textElement.textContent += text[charIndex];
                charIndex++;
                chatUserBody.scrollTop = chatUserBody.scrollHeight; // اسکرول خودکار
            } else {
                clearInterval(typeInterval);
            }
        }, 50); // سرعت تایپ را می‌توانید تغییر دهید

    }

    let welcomeShown = false;
    // window.addEventListener('DOMContentLoaded', () => {
    //     console.log("DOM fully loaded and parsed.");
    //     const faqBoxes = document.querySelectorAll('.faq-box');
    //     console.log("FAQ boxes found:", faqBoxes);
    // });

    // function sendMessageFromFAQ(message) {
    //     if (message) {
    //         const textType = document.querySelector('.text-type');
    //         textType.value = message;
    //         handleSendMessage();
    //
    //     }
    // }

    // faqSection.addEventListener('click', (event) => {
    //     if (event.target.classList.contains('faq-box')) {
    //         const clickedQuestion = event.target.textContent.trim();
    //         console.log("Clicked on FAQ box:", clickedQuestion);
    //
    //         // ارسال پیام به چت‌بات
    //         sendMessageFromFAQ(clickedQuestion);
    //     }
    // });

    function showLoadingIndicator() {
        const loadingIndicator = document.createElement('div');
        loadingIndicator.setAttribute('id', 'loading-indicator');
        loadingIndicator.setAttribute('class', 'loading-indicator');
        loadingIndicator.textContent = 'در انتظار پاسخ...';
        sendIN.append(loadingIndicator);
        scroll();
    }

// Remove the loading message from the chat UI
    function hideLoadingIndicator() {
        const loadingIndicator = document.getElementById('loading-indicator');
        if (loadingIndicator) {
            loadingIndicator.remove();
        }
    }

    const storeNumber = (number) => {
        localStorage.setItem("userMobile", number);
    };


    sendInfoButton.addEventListener("click", handleSaveNumber);

    NumberSendInfo.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            handleSaveNumber();
        }
    });
    const processedMessages = new Set();
    const markMessageAsReceived = async (messageId) => {
        try {
            const response = await fetch(`${baseURL}/messages/${messageId}/mark_as_received/`, {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${API_KEY}`
                },
                body: JSON.stringify({})
            });

        } catch (error) {
        }
    };

    const checkForNewMessages = async () => {
        userMobile = localStorage.getItem("userMobile");
        userIP = localStorage.getItem("userIP");

        try {
            const response = await fetch(`${baseURL}/messages/?msg_sender=${userIP}&msg_sender_number=${userMobile}`, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${API_KEY}`
                }
            });

            const data = await response.json();
            // نمایش پیام‌های جدید (received=false)
            if (data.received_false_messages && data.received_false_messages.length > 0) {
                data.received_false_messages.forEach((message) => {
                    // بررسی اگر پیام قبلاً پردازش نشده باشد
                    if (!processedMessages.has(message.id)) {
                        if (message.tag === 'received') {
                            // اضافه کردن پیام با انیمیشن تایپ
                            addMessageToChatWithTypingAnimation(message);
                        } else {
                            // اضافه کردن پیام به صورت معمولی
                            addMessageToChat(message, message.tag);
                        }
                        // addMessageToChat(message, message.tag); // نمایش پیام
                        processedMessages.add(message.id); // افزودن پیام به مجموعه پردازش‌شده‌ها
                        markMessageAsReceived(message.id); // تغییر وضعیت پیام به received=true
                    }
                });
            }
        } catch (error) {
            console.error("Error checking for new messages:", error);
        }

    };

    function checkForAdminResponse(messageId) {
        const pollInterval = 4000;
        const maxRetries = 20;
        let retries = 0;

        const poll = setInterval(() => {
            if (retries >= maxRetries) {
                clearInterval(poll);
                console.error("پاسخی از ادمین دریافت نشد.");
                hideLoadingIndicator();
                sendMessage.disabled = false;
                textType.disabled = false;
                return;
            }

            fetch(`https://whotalk.app/check-response/${messageId}/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${API_KEY}`,
                },
            })
                .then(res => res.json())
                .then(data => {
                    if (data.adminResponse) {
                        hideLoadingIndicator();
                        // addMessageToChat(data.adminResponse, "received");
                        clearInterval(poll);
                        sendMessage.disabled = false;
                        textType.disabled = false;
                        textType.focus();
                    }
                })
                .catch(error => {
                    console.error('Error checking admin response:', error);
                    hideLoadingIndicator();
                    sendMessage.disabled = false;
                    textType.disabled = false;
                });

            retries++;
        }, pollInterval);
    }


    const fetchAndDisplayMessages = async (showWelcome = false) => {
        userMobile = localStorage.getItem("userMobile");
        userIP = localStorage.getItem("userIP");

        chatUserBody.innerHTML = "";
        try {
            const response = await fetch(`${baseURL}/messages/?msg_sender=${userIP}&msg_sender_number=${userMobile}`, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${API_KEY}`
                }
            });

            const data = await response.json();

            const isTypingElement = document.querySelector('.isTyping');
            if (isTypingElement && data.admin) {
                isTypingElement.innerHTML = `کارشناس هوشمند ${data.admin}<span class="indicator"></span>`;
            }
            // نمایش پیام‌های قبلی (received=true)
            if (data.received_true_messages && data.received_true_messages.length > 0) {
                data.received_true_messages.forEach((message) => {
                    addMessageToChat(message, message.tag);
                    processedMessages.add(message.id);
                });
            }

            chatUserBody.scrollTop = chatUserBody.scrollHeight;

            if (showWelcome && !welcomeShown && data.welcome) {
                const welcomeMessage = {
                    text: data.welcome,
                    create: new Date().toISOString(),
                    msgImg: data.admin_img,
                    company: data.admin
                };
                // console.log(welcomeMessage);
                addMessageToChat(welcomeMessage, "received");
                welcomeShown = true;
            }
            setInterval(checkForNewMessages, 1000);
        } catch (error) {
            console.error("Error fetching previous messages:", error);
        }

    };
    let fileBase64 = null

    const encodeFileToBase64 = (file) => {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = (error) => reject(error);
            reader.readAsDataURL(file);
        });
    };

    fileInputMessageUser.addEventListener("change", async function () {
        const fileNameElement = document.getElementById("file-name-message-user");
        const file = this.files[0];

        if (file) {
            try {
                fileBase64 = await encodeFileToBase64(file);
                fileNameElement.textContent = `فایل انتخاب شده: ${file.name}`;
            } catch (error) {
                console.error("Error encoding file to Base64:", error);
                fileNameElement.textContent = "خطا در خواندن فایل.";
            }
        } else {
            fileBase64 = null;
            fileNameElement.textContent = "هیچ فایلی انتخاب نشده است.";
        }
    });


    // ارسال پیام
    const handleSendMessage = async () => {
        userMobile = localStorage.getItem("userMobile");
        userIP = localStorage.getItem("userIP");
        const messageText = textType.value.trim();
        if (!messageText && !fileBase64) {
            console.error("Message text or fileBase64 is required.");
            return;
        }
        textType.disabled = true;
        sendMessage.disabled = true;
        textType.value = "";
        try {
            // ارسال پیام به سرور
            const response = await fetch("https://whotalk.app/api/messages/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${API_KEY}`
                },
                body: JSON.stringify({
                    msg_sender: userIP,
                    text: messageText,
                    msg_sender_number: userMobile,
                    msgFile_base64: fileBase64
                })
            });
            const data = await response.json();
            if (data.id) {
                showLoadingIndicator();
                checkForAdminResponse(data.id);
            }
            fileBase64 = null;
            fileInputMessageUser.value = "";
            document.getElementById("file-name-message-user").textContent = "هیچ فایلی انتخاب نشده است.";
        } catch (error) {
            console.error("Error sending message:", error);
            // نمایش پیام خطا
            const errorMessage = {
                text: "خطا در ارسال پیام. لطفاً دوباره تلاش کنید.",
                create: new Date().toISOString(),
                msgImg: null
            };
            addMessageToChat(errorMessage, "received");
        } finally {
            sendMessage.disabled = false;
            textType.disabled = false;
        }
    };


    sendMessage.addEventListener("click", handleSendMessage);

    textType.addEventListener("keypress", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            handleSendMessage();
        }
    });

}

