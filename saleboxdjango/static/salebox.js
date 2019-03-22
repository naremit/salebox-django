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
            },
        },
    },

    utils: {
        addressCountryStates: function(formId) {
            var form = $('#' + formId);
            var countryId = $(form).find('select[name=country]').val();
            var stateInput = $(form).find('select[name=country_state]');
            $(stateInput).val('');

            if (countryId in saleboxCountryState) {
                // show states
                html = ['<option value=""></option>'];
                for (var i in saleboxCountryState[countryId]) {
                    html.push('<option value="' + saleboxCountryState[countryId][i]['i'] + '">' + saleboxCountryState[countryId][i]['s'] + '</option>');
                }
                $(stateInput).html(html.join(''));
                $(stateInput).parent().removeClass('d-none');
            } else {
                // hide states
                $(stateInput).parent().addClass('d-none');
                $(stateInput).html('');
            }
        },
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
