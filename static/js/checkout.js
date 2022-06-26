if(isAuthenticated=="True" & is_shipping_able=="False") {
    document.getElementById('form-wrapper').classList.add('hidden')
    document.getElementById('payment-info').classList.remove('hidden')
}

let  form = document.getElementById('form')
form.addEventListener('submit', event => {
    event.preventDefault()
    document.getElementById('form-button').classList.add('hidden')
    document.getElementById('payment-info').classList.remove('hidden')
})

document.getElementById('make-payment').addEventListener('click', event => {
    submitForm()
})

function submitForm() {
    console.log('form submitted')
    let userFormData = {
        'name':null,
        'email':null,
        'total':total,
    }
    let shippingInfo = {
        'address':null,
        'city':null,
        'state':null,
        'zipcode':null,
    }
    if(is_shipping_able=="True") {
        shippingInfo.address = form.address.value
        shippingInfo.city = form.city.value
        shippingInfo.state = form.state.value
        shippingInfo.zipcode = form.zipcode.value
    }
    if(isAuthenticated=="False") {
        userFormData.name = form.name.value
        userFormData.email = form.email.value
    }
    let url = '/process_order/'
    fetch(url, {
        method: "POST",
        headers: {
            'Content-Type':'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({'form':userFormData, 'shipping':shippingInfo})
    })
    .then(response => {
        if(response.ok) {
            return response.json()
        } else {
            console.log(response.body)
        }
    })
    .then(data => {
        console.log(data)
        alert('ordercomplete')
        cart = {}
        document.cookie = 'cart='+JSON.stringify(cart)+';domain=;path=/' +';SameSite=Lax'
        window.location.href = homepage_url
    })
}