/* Bookmarklet code: javascript:(function()%7Bfunction%20callback()%7Badd_site()%7Dvar%20s%3Ddocument.createElement(%22script%22)%3Bs.src%3D%22https%3A%2F%2Fbeta.privacymail.info%2Fstatic%2Fjs%2Fbookmarklet%2Fbookmarklet.js%22%3Bif(s.addEventListener)%7Bs.addEventListener(%22load%22%2Ccallback%2Cfalse)%7Delse%20if(s.readyState)%7Bs.onreadystatechange%3Dcallback%7Ddocument.body.appendChild(s)%3B%7D)() */
function add_site() {
    var request = new XMLHttpRequest();
    request.open('POST', 'https://beta.privacymail.info/api/bookmarklet/identity/', true);
    request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    request.onload = function() {
        var data = JSON.parse(this.response);
        if (data.hasOwnProperty('error')) {
            alert("Error: " + data.error);
        } else {
            myField = document.activeElement;
            myField.value = data.email;
            alert("Name: " + data.first + " " + data.last + "\neMail: " + data.email + "\nGender: " + data.gender);
        }
    };
    var stuff = "url=" + window.location.href;
    console.log(stuff)
    request.send(stuff);
}