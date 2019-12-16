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

    analytics: {
        getKey: function() {
            cookies = document.cookie.split('; ').filter(function(c) {
                return c.startsWith('salebox=');
            });

            if (cookies.length > 0) {
                return cookies[0].replace('salebox=', '');
            } else {
                // generate uuid
                var d = new Date().getTime();
                var d2 = (performance && performance.now && (performance.now()*1000)) || 0;
                var key = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                    var r = Math.random() * 16;
                    if(d > 0){
                        r = (d + r)%16 | 0;
                        d = Math.floor(d/16);
                    } else {
                        r = (d2 + r)%16 | 0;
                        d2 = Math.floor(d2/16);
                    }
                    return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
                });

                // write to cookie
                document.cookie = 'salebox=' + key + '; path=/';

                // return
                return key;
            }
        },

        getLanguage: function() {
            return (
                navigator.languages && navigator.languages[0] || // Chrome / Firefox
                navigator.language ||   // All browsers
                navigator.userLanguage
            );
        },

        init: function() {
            setTimeout(function() {
                var key = salebox.analytics.getKey();
                salebox.utils.ajax(
                    '/salebox/analytics/',
                    {
                        'key': key,
                        'height': screen.height || null,
                        'lang': salebox.analytics.getLanguage() || null,
                        'width': screen.width || null
                    },
                    function() {},
                    function() {}
                );
            }, 1000);
        }
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

    checkout: {
        shippingAddress: {
            toggle: function(show) {
                if (show) {
                    $('#salebox_shipping_invoice_address_picker').hide();
                    $('#salebox_shipping_invoice_address_addshipping').show();
                } else {
                    $('#salebox_shipping_invoice_address_addshipping').hide();
                    $('#salebox_shipping_invoice_address_picker').show();
                }
                salebox.utils.scrollTop(true);
            }
        },

        shippingInvoiceAddress: {
            hideAddForm: function(unsetInvoice) {
                if (unsetInvoice) {
                    $('#salebox_shipping_invoice_address_checkbox').prop('checked', false);
                }
                $('#salebox_shipping_invoice_address_addshipping').hide();
                $('#salebox_shipping_invoice_address_addinvoice').hide();
                $('#salebox_shipping_invoice_address_picker').show();
                //salebox.utils.scrollTop(true);
            },

            setInvoiceRequired: function(el, invoiceAddressCount) {
                if ($(el).is(':checked')) {
                    if (invoiceAddressCount > 0) {
                        $('#salebox_shipping_invoice_address_picker_invoice').show();
                    } else {
                        salebox.checkout.shippingInvoiceAddress.showAddForm(false);
                    }
                } else {
                    $('#salebox_shipping_invoice_address_picker_invoice').hide();
                }
            },

            showAddForm: function(shipping) {
                $('#salebox_shipping_invoice_address_picker').hide();
                if (shipping) {
                    $('#salebox_shipping_invoice_address_addshipping').show();
                } else {
                    $('#salebox_shipping_invoice_address_addinvoice').show();
                }
                salebox.utils.scrollTop(true);
            }
        }
    },

    rating: {
        addAjax: function(variantId, rating, review, results, callback, fail) {
            salebox.utils.ajax(
                '/salebox/rating/add/',
                {
                    variant_id: variantId,
                    rating: rating,
                    review: review,
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

        currency: function(amount) {
            amount = (amount / 100).toFixed(2).split('.');
            amount[0] = amount[0].split('').reverse().join('').replace(/(\d{3})(?=\d)/g, '$1,').split('').reverse().join('');
            return amount.join('.');
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
        },

        scrollTop: function(animate) {
            if (animate) {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            } else {
                $(window).scrollTop(0);
            }
        },

        sendQueryString: function(qs) {
            window.location.href = window.location.protocol + '//' + window.location.host + window.location.pathname + '?' + qs;
        },

        setSortOrder: function(code) {
            salebox.utils.sendQueryString('product_list_order=' + code);
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

    salebox.analytics.init();
});
