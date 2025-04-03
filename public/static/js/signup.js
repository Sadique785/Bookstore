function validateEmail(email){
    var emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;


    return emailPattern.test(email) 
}
function containsLetters(mobile) {
    var letterPattern = /[a-zA-Z]/;

    return letterPattern.test(mobile);
}

function validateMobileNumber(mobile) {
    var mobilePattern = /^\d{10}$/;

    return mobilePattern.test(mobile);
}


function validateForm(){
   
    var first_name = document.getElementById('first_name').value.trim();
    var last_name = document.getElementById('last_name').value.trim();
    var password = document.getElementById('password').value.trim();
    var confirm_password = document.getElementById('confirm_password').value.trim();
    var email = document.getElementById('email').value.trim();
    var mobile = document.getElementById('mobile').value.trim();

    var firstnameError = document.getElementById('firstnameError');
    var lastnameError = document.getElementById('lastnameError');
    var emailError = document.getElementById('emailError');
    var mobileError = document.getElementById('mobileError');
    var passwordError = document.getElementById('passwordError');
    var confirm_passwordError = document.getElementById('confirm_passwordError');

    firstnameError.innerHTML = '';
    lastnameError.innerHTML = '';
    emailError.innerHTML = '';

    mobileError.innerHTML = '';
    passwordError.innerHTML = '';
    confirm_passwordError.innerHTML = '';

    if (first_name===""){
        firstnameError.innerHTML = 'First Name is required';
        return false;
    }
    if (last_name===""){
        lastnameError.innerHTML = 'Last Name is required';
        return false;
    }

    if (email===""){
        emailError.innerHTML = 'Email is required';
        return false;
    }
    else if (!validateEmail(email)) {
        emailError.innerHTML = 'Please Enter a Valid Email Address';
    }
    
    

    if (mobile===""){
        mobileError.innerHTML = 'mobile is required';
        return false;
    }
    else if (containsLetters(mobile)) {
        mobileError.innerHTML = 'Mobile number cannot contain letters';
        return false;
    }

    else if (!validateMobileNumber(mobile)) {
    mobileError.innerHTML = 'Mobile number must have ten digits';
    return false;
    }   

    


    if (password===""){
        passwordError.innerHTML = 'password is required';
        return false;
    }

    if (confirm_password===""){
        confirm_passwordError.innerHTML = 'confirm your password';
        return false;
    }

    if (password!=confirm_password){
        confirm_passwordError.innerHTML = 'Enter the same password';
        return false;
    }


    return true;
}
function validateLogin(){
   
   
    var password = document.getElementById('password').value.trim();
    var email = document.getElementById('email').value.trim();




    var emailError = document.getElementById('emailError');  
    var passwordError = document.getElementById('passwordError');



    emailError.innerHTML = '';
    passwordError.innerHTML = '';




    if (email===""){
        emailError.innerHTML = 'Email is required';
        return false;
    }

    else if (!validateEmail(email)) {
    emailError.innerHTML = 'Please Enter a Valid Email Address';
    }



    if (password===""){
        passwordError.innerHTML = 'password is required';
        return false;
    }

    return true;
}