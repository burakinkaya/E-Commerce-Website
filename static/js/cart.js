var updateBtns = document.getElementsByClassName('update-cart');

for (var i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function () {
        var productId = this.dataset.product;
        var action = this.dataset.action;
        var quantity = Number(this.dataset.quantity);
        console.log('productId:', productId, 'user:', user, 'Action:', action, 'quantity:', quantity);

        if (user === 'AnonymousUser') {
            addCookieItem(productId, action,quantity);
        } else {
            updateUserOrder(productId, action, quantity);
        }
    });
}

function addCookieItem(productId, action, quantity) {
    console.log('User is not authenticated');

    let cart = {};

    // Check if a cart already exists in cookies
    if (document.cookie.includes('cart=')) {
        cart = JSON.parse(getCookie('cart'));
    }

    if (action === 'add') {
        if (cart[productId] === undefined) {
            cart[productId] = { 'quantity': quantity };
        } else {
            if(cart[productId]['quantity'] == null){
            cart[productId]['quantity'] += 1;
            }else{
                cart[productId]['quantity'] += quantity;
            }
        }
    }
   //df
    if (action === 'remove') {
        if (cart[productId] !== undefined) {
            cart[productId]['quantity'] -= 1;

            if (cart[productId]['quantity'] <= 0) {
                console.log('Remove Item');
                delete cart[productId];
            }
        }
    }

    if (action === 'removeAll') {
        console.log('Remove Item');
        delete cart[productId];
    }

    console.log('CART:', cart);
    document.cookie = 'cart=' + JSON.stringify(cart) + ';domain=;path=/';
    location.reload();
}

function getCookie(name) {
    const value = '; ' + document.cookie;
    const parts = value.split('; ' + name + '=');
    if (parts.length === 2) {
        return parts.pop().split(';').shift();
    }
    return undefined;
}



function updateUserOrder(productId, action,quantity) {
    console.log('User is logged in, sending data...')

    var url = '/update_item/'

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ 'productId': productId, 'action': action , 'quantity': quantity })
    })
        .then((response) => {
            return response.json()

        })
        .then((data) => {
            console.log('data:', data)
        });

        


}