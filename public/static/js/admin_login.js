function adminvalidateLogin(){
   
   
    var password = document.getElementById('password').value;

    var username_admin = document.getElementById('username_admin').value;



 
    var passwordError = document.getElementById('passwordError');
    var username_adminError = document.getElementById('username_adminError');



    passwordError.innerHTML = '';
    username_adminError.innerHTML = '';




    if (username_admin === ""){
        username_adminError.innerHTML = 'Username is required';
        return false;
    }


    if (password===""){
        passwordError.innerHTML = 'Password is required';
        return false;
    }

    return true;
}