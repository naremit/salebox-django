var salebox = {
    address: {
        countryStateDropdown: function(formId) {
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

        removeRedirect: function(id, state, redirectUrl) {
            salebox.utils.post('/salebox/address/remove/', {
                'id': id,
                'redirect': redirectUrl,
                'state': state
            });
        },

        setDefaultRedirect: function(id, state, redirectUrl) {
            salebox.utils.post('/salebox/address/set-default/', {
                'id': id,
                'redirect': redirectUrl,
                'state': state
            });
        },
    },

    basket: {
        basket: function(variantId, qty, relative, results, success, fail) {
            $.post(
                '/salebox/basket/basket/',
                {
                    variant_id: variantId,
                    quantity: qty,
                    relative: relative,
                    results: results
                },
                function(data) {
                    success(data);
                }
            );
        }
    },

    utils: {
        getCsrf: function() {
            return $('[name=csrfmiddlewaretoken]').eq(0).val();
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

// init ajax csrf
$(function() {
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!this.crossDomain) {
                xhr.setRequestHeader(
                    'X-CSRFToken',
                    salebox.utils.getCsrf()
                );
            }
        }
    });
});
