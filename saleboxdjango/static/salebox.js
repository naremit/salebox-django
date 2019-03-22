var salebox = {
    redirect: {
        address: {
            remove: function(id, state, redirectUrl) {
                salebox.utils.post('/salebox/address/remove/', {
                    'id': id,
                    'redirect': redirectUrl,
                    'state': state
                });
            },

            setDefault: function(id, state, redirectUrl) {
                salebox.utils.post('/salebox/address/set-default/', {
                    'id': id,
                    'redirect': redirectUrl,
                    'state': state
                });
            }
        },
    },

    utils: {
        post: function(action, dict) {
            // default redirect, i.e. back to this page
            if (!(dict.redirect)) {
                dict.redirect = redirectUrl = window.location.pathname;
            }

            // add csrf token
            dict.csrfmiddlewaretoken = $("[name=csrfmiddlewaretoken]").val();

            // construct html
            var form = ['<form action="' + action + '" method="post">'];
            for (var key in dict) {
                if (dict[key]) {
                    form.push('<input type="hidden" name="' + key + '" value="' + dict[key] + '">');
                }
            }
            form.push('</form>');

            // append and submit
            var postForm = $(form.join(''));
            $('body').append(postForm);
            postForm.submit();
        }
    }
};
