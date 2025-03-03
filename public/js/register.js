let passwordValid = false;
let passwordMatch = false;

function checkPassword(password) {
    // 檢查各項要求
    const requirements = {
        length: password.length >= 8,
        uppercase: /[A-Z]/.test(password),
        lowercase: /[a-z]/.test(password),
        number: /[0-9]/.test(password)
    };

    // 更新視覺提示
    for (let req in requirements) {
        const element = document.getElementById(req);
        if (requirements[req]) {
            element.classList.remove('invalid');
            element.classList.add('valid');
        } else {
            element.classList.remove('valid');
            element.classList.add('invalid');
        }
    }

    // 檢查是否所有要求都符合
    passwordValid = Object.values(requirements).every(Boolean);
    updateSubmitButton();
    
    // 如果已經輸入確認密碼，重新檢查密碼匹配
    if (document.getElementById('confirmPassword').value) {
        checkPasswordMatch();
    }
}

function checkPasswordMatch() {
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const errorElement = document.getElementById('confirmPasswordError');
    
    if (confirmPassword) {
        if (password === confirmPassword) {
            errorElement.style.display = 'none';
            passwordMatch = true;
        } else {
            errorElement.style.display = 'block';
            errorElement.textContent = '密碼不一致';
            passwordMatch = false;
        }
    } else {
        errorElement.style.display = 'none';
        passwordMatch = false;
    }
    
    updateSubmitButton();
}

function updateSubmitButton() {
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = !(passwordValid && passwordMatch);
}

function validateForm() {
    return passwordValid && passwordMatch;
}

function refreshCaptcha() {
    const captchaImage = document.getElementById('captchaImage');
    captchaImage.src = '/captcha?' + new Date().getTime();
} 