var updateBtns = document.getElementsByClassName('update-cart')

for(var i=0; i<updateBtns.length; i++){
    updateBtns[i].addEventListener('click', function(){
        let productId = this.dataset.product
        let action = this.dataset.action
        if(isAuthenticated=="True"){
            updateOrderItem(productId, action)
        } else {
            addCookieItem(productId, action)
        }
    })
};

function addCookieItem(productID, action) {
    console.log("user not logged in..")
    if(action=='add'){
        if(cart[productID]==undefined){
            cart[productID] = {'quantity':1}
            console.log('item added')
        } else {
            cart[productID]['quantity'] += 1
            console.log('quantity incremented')
        }
    }
    if(action=='remove'){
        cart[productID]['quantity'] -= 1
        console.log('quantity reducted')
        if(cart[productID]['quantity'] <= 0){
            delete cart[productID]
            console.log('item deleted')
        }
    }
    let exp_time = (new Date(Date.now() + 86400*1000)).toUTCString()
    document.cookie = 'cart='+JSON.stringify(cart)+';expires='+exp_time+';domain=;path=/' +';SameSite=Lax'
    location.reload()
}


function updateOrderItem(productID, action) {
    let url = '/update_item/'
    fetch(url, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({'productID':productID, 'action':action})
    })
    .then((response) => {
        if(response.ok) {
            console.log('updated')
            location.reload()
        } else {
            console.log('error')
        }
    })
};
