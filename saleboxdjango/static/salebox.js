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
        basketAjax: function(variantId, qty, relative, results, callback, fail) {
            salebox.utils.ajax(
                '/salebox/basket/basket/',
                {
                    variant_id: variantId,
                    quantity: qty,
                    relative: relative,
                    results: results
                },
                callback,
                fail
            );
        },

        migrateAjax: function(variantId, toBasket, results, callback, fail) {
            salebox.utils.ajax(
                '/salebox/basket/migrate/',
                {
                    variant_id: variantId,
                    to_basket: toBasket,
                    results: results
                },
                callback,
                fail
            );
        },

        wishlistAjax: function(variantId, add, results, callback, fail) {
            salebox.utils.ajax(
                '/salebox/basket/wishlist/',
                {
                    variant_id: variantId,
                    add: add,
                    results: results
                },
                callback,
                fail
            );
        }
    },

    rating: {
        addAjax: function(variantId, rating, results, callback, fail) {
            salebox.utils.ajax(
                '/salebox/rating/add/',
                {
                    variant_id: variantId,
                    rating: rating,
                    results: results
                },
                callback,
                fail
            );
        },

        removeAjax: function(variantId, results, callback, fail) {
            salebox.utils.ajax(
                '/salebox/rating/remove/',
                {
                    variant_id: variantId,
                    results: results
                },
                callback,
                fail
            );
        },
    },

    utils: {
        ajax: function(url, data, callback, fail) {
            $.post(url, data).done(function(data) {
                callback(data);
            }).fail(function() {
                fail();
            });
        },

        getCSRF: function() {
            return $('[name=csrfmiddlewaretoken]').eq(0).val();
        },

        post: function(action, dict) {
            // default redirect, i.e. back to this page
            if (!(dict.redirect)) {
                dict.redirect = redirectUrl = window.location.pathname;
            }

            // add csrf token
            dict.csrfmiddlewaretoken = salebox.utils.getCSRF();

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
                    salebox.utils.getCSRF()
                );
            }
        }
    });
});
