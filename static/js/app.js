    function signInCallback(authData) {
        if (authData['code']) {
            // Hide sign-in button now that the user is authorized
            $('#signinBtn').attr('style', 'display: none');
            // Send one-time code to server, if the server responds, write a 'login successful' message to the web page and then redirect back to the main restaurants page
            $.ajax({
                type: 'POST',
                url: '/google_signin?state={{STATE}}',
                processData: false,
                data: authData['code'],
                contentType: 'application/octet-stream; charset=UTF-8',
                success: function(result) {
                    // Handle or verify the server response if necessary.
                    if (result) {
                        $('#result').html('Login Successful!</br>' + result + '</br>Redirecting...')
                            setTimeout(function() {window.location.href = "/categories/";}, 2000);
                    } else if (authData['error']) {
                        console.log('There was an error: ' + authData['error']);
                    } else {
                        $('#result').html('Failed to make a server-side call. Check your configuration and console.');
                    }
                }

            });
        }
    }